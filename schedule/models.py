import datetime

from django.db import models
from django.conf import settings


class WorkDay(models.Model):
    available = models.BooleanField(default=True, verbose_name='availability',
                                    help_text='Writable')
    date = models.DateField(verbose_name='date', help_text='Date') #должна автоматически прописаться на годы вперед
    start = models.TimeField(default=datetime.time(9, 00), verbose_name='start',
                             help_text='Set the beginning of the work day')
    finish = models.TimeField(default=datetime.time(18, 00), verbose_name='end',
                              help_text='Set the end of the working day')
    # break_time, выбираем два любых времени через choises, blank=True
    # def break_time = models
    def __str__(self):
        return self.date.strftime("%b/%d/%Y")

        # наверное надо отдавать не то, чтобы получалось два числа.
    # число, месяц(название), год


class Lesson(models.Model):
    class Duration(models.TextChoices):
        half = '30 min'
        hour_1 = '1 hour'
        hour_and_half = '1.5 hour'

#Подкласс чойсес не создает таблицу

    day = models.ForeignKey('WorkDay', on_delete=models.CASCADE, related_name='lessons', verbose_name='day',
                            help_text='Day')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons',
                             verbose_name='user', help_text='User')
    ENG = 'ENG'
    MAT = 'MAT' # попробовать 4 символа
    RUS = 'RUS'
    SUBJECT_CHOISES = [
        (ENG, 'English'),
        (MAT, 'Maths'),
        (RUS, 'Russian')
    ]
    subject = models.CharField(max_length=3, choices=SUBJECT_CHOISES, default=ENG)
    duration_lessons = models.CharField(max_length=30, choices=Duration.choices, default=Duration.hour_1)
    start = models.TimeField(verbose_name='start', help_text='lesson start time')
    created_at = models.DateTimeField(auto_now_add=True)
    change_at = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=512, verbose_name='comment', help_text='comment')

# По всему проекту удалить все комменатрии, кроме моих в проекте по впоросам (не сделал, т.к удобно смотреть где что, в первое время
# Cделать время +3 часа (московскаое) (сделал)
# Сделать расскрывающийся список, виджеты (сделал, с классом под вопросом)
# choices изучить (choices предназначен для статических данных, которые мало меняются, если вообще когда-либо меняются.)
# параметры blank и Null (параметры поля)
# поменять сабжект!, перерывы сделать (в процессе)
# залить на гитхабе
