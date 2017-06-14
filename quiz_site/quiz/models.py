import json
import re

from django.conf import settings
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from model_utils.managers import InheritanceManager


class Quiz(models.Model):
    title = models.CharField(
        verbose_name=_("Название"),
        max_length=60, blank=False)

    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True, help_text=_("описание теста"))

    url = models.SlugField(
        max_length=60, blank=False,
        help_text=_("ссылка для пользователей"),
        verbose_name=_("ссылка для пользователей"))

    random_order = models.BooleanField(
        blank=False, default=False,
        verbose_name=_("Случайный порядок"),
        help_text=_("Отображать вопросы в случайном порядке или так, как они заданы?"))

    pass_mark = models.SmallIntegerField(
        blank=True, default=0,
        verbose_name=_("Нижняя граница"),
        help_text=_("Процент правильных ответов, необходимый для успешной сдачи."),
        validators=[MaxValueValidator(100)])

    success_text = models.TextField(
        blank=True, help_text=_("Отображается, если пользователь прошел тест."),
        verbose_name=_("Успех"))

    fail_text = models.TextField(
        verbose_name=_("Неудача"),
        blank=True, help_text=_("Отображается, если пользователь не прошел тест."))

    draft = models.BooleanField(
        blank=True, default=False,
        verbose_name=_("Черновик"),
        help_text=_("Если да, то обыкновенные пользователи не могут пройти данный тест."))

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        self.url = re.sub(r'\s+', '-', self.url).lower()

        self.url = ''.join(letter for letter in self.url if
                           letter.isalnum() or letter == '-')

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = _("Тест")
        verbose_name_plural = _("Тесты")

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.question_set.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()


class SittingManager(models.Manager):
    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.question_set.all() \
                .select_subclasses() \
                .order_by('?')
        else:
            question_set = quiz.question_set.all() \
                .select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. '
                                       'Please configure questions properly')

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if self.filter(user=user, quiz=quiz, end__isnull=False).exists():
            return False

        if self.filter(user=user, quiz=quiz, end__isnull=True).exists():
            return self.filter(user=user, quiz=quiz, end__isnull=True).last()

        return self.new_sitting(user, quiz)


class Sitting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Пользователь"))

    quiz = models.ForeignKey(Quiz, verbose_name=_("Тест"))

    question_order = models.CharField(
        max_length=1024, verbose_name=_("Порядок вопросов"), validators=[validate_comma_separated_integer_list])

    question_list = models.CharField(
        max_length=1024, verbose_name=_("Список вопросов"), validators=[validate_comma_separated_integer_list])

    incorrect_questions = models.CharField(
        max_length=1024, blank=True, verbose_name=_("Неправильные ответы"),
        validators=[validate_comma_separated_integer_list])

    current_score = models.IntegerField(verbose_name=_("Текущий результат"))

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name=_("Завершен"))

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name=_("Ответы пользователя"))

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name=_("Начат"))

    end = models.DateTimeField(null=True, blank=True, verbose_name=_("Завершен"))

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", _("Может видеть завершенные экзамены.")),)

    def get_first_question(self):
        if not self.question_list:
            return False

        first, _ = self.question_list.split(',', 1)
        question_id = int(first)
        return Question.objects.get_subclass(id=question_id)

    def remove_first_question(self):
        if not self.question_list:
            return

        _, others = self.question_list.split(',', 1)
        self.question_list = others
        self.save()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def _question_ids(self):
        return [int(n) for n in self.question_order.split(',') if n]

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = len(self._question_ids())
        if divisor < 1:
            return 0

        if dividend > divisor:
            return 100

        correct = int(round((dividend / divisor) * 100))

        if correct >= 1:
            return correct
        else:
            return 0

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    def add_incorrect_question(self, question):
        if len(self.incorrect_questions) > 0:
            self.incorrect_questions += ','
        self.incorrect_questions += str(question.id) + ","
        if self.complete:
            self.add_to_score(-1)
        self.save()

    @property
    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.add_to_score(1)
        self.save()

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        if self.check_if_passed:
            return self.quiz.success_text
        else:
            return self.quiz.fail_text

    def add_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        current[question.id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def get_questions(self, with_answers=False):
        question_ids = self._question_ids()
        questions = sorted(
            self.quiz.question_set.filter(id__in=question_ids)
                .select_subclasses(),
            key=lambda q: question_ids.index(q.id))

        if with_answers:
            user_answers = json.loads(self.user_answers)
            for question in questions:
                question.user_answer = user_answers[str(question.id)]

        return questions

    @property
    def questions_with_user_answers(self):
        return {
            q: q.user_answer for q in self.get_questions(with_answers=True)
        }

    @property
    def get_max_score(self):
        return len(self._question_ids())

    def progress(self):
        answered = len(json.loads(self.user_answers))
        total = self.get_max_score
        return answered, total

    def get_duration(self):
        return round((self.end - self.start).seconds/60)


class Question(models.Model):
    quiz = models.ManyToManyField(Quiz,
                                  verbose_name=_("Тест"),
                                  blank=True)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Введите текст вопроса"),
                               verbose_name=_('Вопрос'))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("Вопрос")
        verbose_name_plural = _("Вопросы")

    def __str__(self):
        return self.content


ANSWER_ORDER_OPTIONS = (
    ('content', _('По содержанию')),
    ('random', _('Случайно')),
    ('none', _('Никак'))
)


class MCQuestion(Question):
    answer_order = models.CharField(
        max_length=30, null=True, blank=True,
        choices=ANSWER_ORDER_OPTIONS,
        help_text=_("Порядок, в котором отображаются варианты ответов."),
        verbose_name=_("Порядок ответов"))

    def check_if_correct(self, guess):
        answer = Answer.objects.get(id=guess)

        if answer.correct is True:
            return True
        else:
            return False

    def order_answers(self, queryset):
        if self.answer_order == 'content':
            return queryset.order_by('content')
        if self.answer_order == 'random':
            return queryset.order_by('?')
        if self.answer_order == 'none':
            return queryset.order_by()
        return queryset

    def get_answers(self):
        return self.order_answers(Answer.objects.filter(question=self))

    def get_answers_list(self):
        return [(answer.id, answer.content) for answer in
                self.order_answers(Answer.objects.filter(question=self))]

    def answer_choice_to_string(self, guess):
        return Answer.objects.get(id=guess).content

    class Meta:
        verbose_name = _("Вопрос с несколькими вариантами ответов")
        verbose_name_plural = _("Вопросы с несколькими вариантами ответов")


class Answer(models.Model):
    question = models.ForeignKey(MCQuestion, verbose_name=_("Вопрос"))

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Введите текст ответа."),
                               verbose_name=_("Текст"))

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Это - правильный ответ?"),
                                  verbose_name=_("Правильный"))

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Ответ")
        verbose_name_plural = _("Ответы")


class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Отметьте здесь, если утверждение верно."),
                                  verbose_name=_("Правильно"))

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'Да'},
                {'correct': self.check_if_correct("False"),
                 'content': 'Нет'}]

    def get_answers_list(self):
        return [(True, _('Да')), (False, _('Нет'))]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = _("Вопрос да/нет")
        verbose_name_plural = _("Вопросы да/нет")
