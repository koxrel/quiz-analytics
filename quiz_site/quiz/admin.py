from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from .models import Quiz, Question, MCQuestion, Answer, TF_Question


class AnswerInline(admin.TabularInline):
    model = Answer


class QuizAdminForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label=_("Вопросы"),
        widget=FilteredSelectMultiple(
            verbose_name=_("Вопросы"),
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = \
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set = self.cleaned_data['questions']
        self.save_m2m()
        return quiz


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm

    list_display = ('title',)
    list_filter = ('title',)
    search_fields = ('description',)


class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('content',)
    list_filter = ('content',)
    fields = ('content', 'quiz', 'answer_order')

    search_fields = ('content',)
    filter_horizontal = ('quiz',)

    inlines = [AnswerInline]


class ProgressAdmin(admin.ModelAdmin):
    search_fields = ('user', 'score',)


class TFQuestionAdmin(admin.ModelAdmin):
    list_display = ('content',)
    list_filter = ('content',)
    fields = ('content', 'quiz', 'correct',)

    search_fields = ('content',)
    filter_horizontal = ('quiz',)


admin.site.register(Quiz, QuizAdmin)
admin.site.register(MCQuestion, MCQuestionAdmin)
admin.site.register(TF_Question, TFQuestionAdmin)
