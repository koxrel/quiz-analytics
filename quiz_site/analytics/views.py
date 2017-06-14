from quiz.models import Sitting, Quiz, Question
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView
from collections import Counter
from statistics import mean


class QuizListView(ListView):
    model = Quiz
    template_name = 'quiz_list.html'


class SummaryQuizView(TemplateView):
    template_name = 'summary.html'


    def get_context_data(self, **kwargs):
        context = super(SummaryQuizView, self).get_context_data(**kwargs)
        quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])
        sittings = Sitting.objects.filter(quiz=quiz)

        pie_chart_data = [0, 0]
        bar_chart_data = []
        incorrect_questions = []
        durations = []

        if not sittings:
            context['sittings'] = sittings
            return context

        for sitting in sittings:
            pie_chart_data[0] += sitting.check_if_passed
            bar_chart_data.append(sitting.get_percent_correct)
            incorrect_questions.extend([i for i in sitting.incorrect_questions.split(',') if i])
            durations.append(sitting.get_duration())
        pie_chart_data[1] = len(sittings) - pie_chart_data[0]

        incorrect_questions_top = Counter(incorrect_questions).most_common(5)

        incorrect_questions_top = [Question.objects.get(pk=int(i[0])) for i in incorrect_questions_top]

        context.update({
            'pie_chart_data': pie_chart_data,
            'quiz': quiz,
            'sittings': sittings,
            'incorrect_questions_top': incorrect_questions_top,
            'duration_avg': round(mean(durations), 1),
            'score_avg': round(mean(bar_chart_data))
        })

        return context


class UserQuizView(TemplateView):
    template_name = 'user.html'

    def get_context_data(self, **kwargs):
        context = super(UserQuizView, self).get_context_data(**kwargs)
        sitting = get_object_or_404(Sitting, quiz__url=self.kwargs['quiz_name'], user__username=self.kwargs['username'])


        context.update({
            'incorrect_questions': sitting.get_incorrect_questions,
            'questions': sitting.get_questions(with_answers=True),
            'sitting': sitting,
            'duration': sitting.get_duration()
        })

        return context

