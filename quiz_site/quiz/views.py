from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, TemplateView, FormView

from .forms import QuestionForm
from .models import Quiz, Sitting


class IndexView(TemplateView):
    template_name = 'home.html'


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class QuizTake(LoginRequiredMixin, FormView):
    form_class = QuestionForm
    template_name = 'question.html'

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        self.sitting = Sitting.objects.user_sitting(request.user,
                                                    self.quiz)

        if self.sitting is False:
            return render(request, 'single_complete.html', {'quiz': self.quiz})

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self):
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()

        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        self.form_valid_user(form)
        if self.sitting.get_first_question() is False:
            return self.final_result_user()

        self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
        else:
            self.sitting.add_incorrect_question(self.question)

        self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()

        results['questions'] = self.sitting.get_questions(with_answers=True)
        results['incorrect_questions'] = self.sitting.get_incorrect_questions

        return render(self.request, 'result.html', results)
