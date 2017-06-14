# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-09 09:25
from __future__ import unicode_literals

import re

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='Введите текст ответа.', max_length=1000, verbose_name='Текст')),
                ('correct',
                 models.BooleanField(default=False, help_text='Это - правильный ответ?', verbose_name='Правильный')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='Введите текст вопроса', max_length=1000, verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, verbose_name='Название')),
                ('description', models.TextField(blank=True, help_text='описание теста', verbose_name='Описание')),
                ('url', models.SlugField(help_text='ссылка для пользователей', max_length=60,
                                         verbose_name='ссылка для пользователей')),
                ('random_order', models.BooleanField(default=False,
                                                     help_text='Отображать вопросы в случайном порядке или так, как они заданы?',
                                                     verbose_name='Случайный порядок')),
                ('pass_mark', models.SmallIntegerField(blank=True, default=0,
                                                       help_text='Процент правильных ответов, необходимый для успешной сдачи.',
                                                       validators=[django.core.validators.MaxValueValidator(100)],
                                                       verbose_name='Нижняя граница')),
                ('success_text', models.TextField(blank=True, help_text='Отображается, если пользователь прошел тест.',
                                                  verbose_name='Успех')),
                ('fail_text', models.TextField(blank=True, help_text='Отображается, если пользователь не прошел тест.',
                                               verbose_name='Неудача')),
                ('draft', models.BooleanField(default=False,
                                              help_text='Если да, то обыкновенные пользователи не могут пройти данный тест.',
                                              verbose_name='Черновик')),
            ],
            options={
                'verbose_name': 'Тест',
                'verbose_name_plural': 'Тесты',
            },
        ),
        migrations.CreateModel(
            name='Sitting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.CharField(max_length=1024, validators=[
                    django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z', 32), code='invalid',
                                                          message='Enter only digits separated by commas.')],
                                                    verbose_name='Порядок вопросов')),
                ('question_list', models.CharField(max_length=1024, validators=[
                    django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z', 32), code='invalid',
                                                          message='Enter only digits separated by commas.')],
                                                   verbose_name='Список вопросов')),
                ('incorrect_questions', models.CharField(blank=True, max_length=1024, validators=[
                    django.core.validators.RegexValidator(re.compile('^\\d+(?:\\,\\d+)*\\Z', 32), code='invalid',
                                                          message='Enter only digits separated by commas.')],
                                                         verbose_name='Неправильные ответы')),
                ('current_score', models.IntegerField(verbose_name='Текущий результат')),
                ('complete', models.BooleanField(default=False, verbose_name='Завершен')),
                ('user_answers', models.TextField(blank=True, default='{}', verbose_name='Ответы пользователя')),
                ('start', models.DateTimeField(auto_now_add=True, verbose_name='Начат')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='Завершен')),
                ('quiz',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.Quiz', verbose_name='Тест')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                           verbose_name='Пользователь')),
            ],
            options={
                'permissions': (('view_sittings', 'Может видеть завершенные экзамены.'),),
            },
        ),
        migrations.CreateModel(
            name='MCQuestion',
            fields=[
                ('question_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='quiz.Question')),
                ('answer_order', models.CharField(blank=True, choices=[('content', 'Вопрос'), ('random', 'Случайно'),
                                                                       ('none', 'Никак')],
                                                  help_text='Порядок, в котором отображаются варианты ответов.',
                                                  max_length=30, null=True, verbose_name='Порядок ответов')),
            ],
            options={
                'verbose_name': 'Вопрос с несколькими вариантами ответов',
                'verbose_name_plural': 'Вопросы с несколькими вариантами ответов',
            },
            bases=('quiz.question',),
        ),
        migrations.CreateModel(
            name='TF_Question',
            fields=[
                ('question_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='quiz.Question')),
                ('correct', models.BooleanField(default=False, help_text='Отметьте здоесь, если текст - правильный..',
                                                verbose_name='Правильно')),
            ],
            options={
                'verbose_name': 'Вопрос да/нет',
                'verbose_name_plural': 'Вопросы да/нет',
            },
            bases=('quiz.question',),
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ManyToManyField(blank=True, to='quiz.Quiz', verbose_name='Тест'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz.MCQuestion',
                                    verbose_name='Вопрос'),
        ),
    ]
