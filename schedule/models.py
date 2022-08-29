import datetime
from itertools import chain
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

WORK_DAY_START = datetime.time(9, 00)
WORK_DAY_FINISH = datetime.time(18, 00)
BREAK_START = datetime.time(13, 00)
BREAK_FINISH = datetime.time(14, 00)


def is_half_hour_validator(value):
    if value.minute % 30 != 0 or value.second != 0:
        raise ValidationError(message='Укажить время кратное 30 минутам')


def time_to_float(time):
    float_value = float(time.strftime("%H"))
    if time.strftime("%M") == "30":
        float_value += 0.5
    return float_value


def get_event_duration(start, stop):
    duration = []
    result = start
    while result < stop:
        duration.append(result)
        result += 0.5
    return duration


class WorkDay(models.Model):
    available = models.BooleanField(default=True, verbose_name='availability',
                                    help_text='Writable')
    date = models.DateField(default=datetime.date.today(), verbose_name='date', help_text='Set the date', unique=True)
    # TODO прописать дату на годы вперед
    start = models.TimeField(default=WORK_DAY_START, verbose_name='start',
                             help_text='Set the beginning of the work day', validators=[is_half_hour_validator])
    finish = models.TimeField(default=WORK_DAY_FINISH, verbose_name='end',
                              help_text='Set the end of the working day', validators=[is_half_hour_validator])

    start_break_time = models.TimeField(default=BREAK_START, null=True, verbose_name='start break'
                                        , help_text='select the start time of the break,'
                                                    ' or leave the field blank if there is none',
                                        validators=[is_half_hour_validator])
    finish_break_time = models.TimeField(default=BREAK_FINISH, null=True, verbose_name='finish break'
                                         , help_text='select the finish time of the break,'
                                                     ' or leave the field blank if there is none',
                                         validators=[is_half_hour_validator])

    def __str__(self):
        return self.date.strftime("%A %d %B %Y")

    def clean(self):
        errors = []
        if self.start >= self.finish:
            errors.append('Invalid time, start after finish')
        if self.start_break_time >= self.finish_break_time:
            errors.append('Invalid time, start break after finish')
        if not self.start < self.start_break_time < self.finish:
            errors.append('Invalid time, start of a break in non-working hours')
        if not self.start < self.finish_break_time < self.finish:
            errors.append('Invalid time, finish of a break in non-working hours')
        if errors:
            raise ValidationError(message=errors)

    # TODO прочитать по values и values list, сделать авиабл тайм (ниже пояснения)

    def available_time(self):
        start = time_to_float(self.start)
        start_break = time_to_float(self.start_break_time)
        finish = time_to_float(self.finish)
        finist_break = time_to_float(self.finish_break_time)
        duration_night = list(map(get_event_duration, (0.0, finish), (start, 24.0)))
        duration_night = list(chain(*duration_night))
        duration_break = get_event_duration(start_break, finist_break)
        lessons = self.lessons.all().order_by('start')
        start_lessons = []
        finish_lessons = []
        for lesson in lessons:
            start_lessons.append(time_to_float(lesson.start))
            finish_lessons.append(time_to_float(lesson.start) + time_to_float(lesson.duration_lessons))
        duration_lessons = list(map(get_event_duration, start_lessons, finish_lessons))
        duration_lessons = list(chain(*duration_lessons))
        all_hours = list(range(0, 24))
        all_time = list(map(lambda x: [x, x + 0.5], all_hours))
        all_time = set(chain(*all_time))
        busy_time = set(duration_break + duration_lessons + duration_night)
        free_time = sorted(list(all_time - busy_time))
        list_free_time = []
        for i, d in enumerate(free_time):
            if free_time[i - 1] != d - 0.5:
                start = d
            if i + 1 < len(free_time):
                if free_time[i + 1] != d + 0.5:
                    list_free_time.append((start, d + 0.5))
            if i + 1 >= len(free_time):
                list_free_time.append((start, d + 0.5))
        return list_free_time

    class Meta:
        db_table = 'Days'
        ordering = ['date']
        verbose_name = 'day'
        verbose_name_plural = 'days'


class Lesson(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons',
                             verbose_name='user', help_text='Set user')
    day = models.ForeignKey('WorkDay', on_delete=models.CASCADE, related_name='lessons', verbose_name='day',
                            help_text='Set the day')
    ENG = 'ENG'
    MAT = 'MAT'
    RUS = 'RUS'
    SUBJECT_CHOISES = [
        (ENG, 'English'),
        (MAT, 'Maths'),
        (RUS, 'Russian')
    ]
    subject = models.CharField(max_length=3, choices=SUBJECT_CHOISES, default=ENG, verbose_name='subject',
                               help_text='Select subject')
    start = models.TimeField(verbose_name='start of lesson', help_text='Set start of lesson',
                             validators=[is_half_hour_validator])
    HALF = datetime.time(0, 30)
    HOUR = datetime.time(1, 00)
    HOUR2 = datetime.time(2, 00)
    TIME_CHOISES = [
        (HALF, '30 minute'),
        (HOUR, '1 hour'),
        (HOUR2, '2 hours')
    ]

    duration_lessons = models.TimeField(choices=TIME_CHOISES, default=HOUR,
                                        verbose_name='lesson duration', help_text='select lesson duration')
    created_at = models.DateTimeField(auto_now_add=True)
    change_at = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=512, verbose_name='comment', help_text='Comment', blank=True)

    def __str__(self):
        return f'{self.start} | duration: {self.duration_lessons} | {self.day} | {self.user} | ' \
               f'{self.get_subject_display()} | {self.comment}'

    class Meta:
        db_table = 'Lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        unique_together = ['day', 'start']
        ordering = ['day', 'start']

# TODO может быть добавить place = дома, работа, онлайн. чойзес. Или перегруз, пофик? TODO определить класс мета 
#  везде подробно и создать базу и миграции заново (не работает, мб где то не так зарегистрированы таблицы, 
#  т.к у них новые имена)
