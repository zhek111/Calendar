import datetime
from itertools import chain
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from typing import Union

WORK_DAY_START = datetime.time(9, 00)
WORK_DAY_FINISH = datetime.time(18, 00)
BREAK_START = datetime.time(13, 00)
BREAK_FINISH = datetime.time(14, 00)


def is_half_hour_validator(value):
    if value.minute % 30 != 0 or value.second != 0:
        raise ValidationError(message='The set time must be a multiple of 30 minutes.')


def time_of_function(function):
    def wrapper(*args, **kvargs):
        startTime = datetime.datetime.now()
        result = function(*args, **kvargs)
        print("Used time:", datetime.datetime.now() - startTime)
        return result

    return wrapper


def time_to_float(time: datetime.time) -> float:
    float_value = float(time.strftime("%H"))
    if time.strftime("%M") == "30":
        float_value += 0.5
    return float_value


def get_event_duration(start: float, stop: float) -> set:
    duration = []
    result = start
    while result < stop:
        duration.append(result)
        result += 0.5
    return set(duration)


def get_time_interval(time: list) -> list[tuple]:
    intervals = []
    for i, d in enumerate(time):
        if time[i - 1] != d - 0.5:
            start = d
        if i + 1 < len(time):
            if time[i + 1] != d + 0.5:
                intervals.append((start, d + 0.5))
        if i + 1 >= len(time):
            intervals.append((start, d + 0.5))
    return intervals


class WorkDay(models.Model):
    available = models.BooleanField(default=True, verbose_name='availability',
                                    help_text='Writable')
    date = models.DateField(default=now, verbose_name='date', help_text='Set the date', unique=True)
    # TODO прописать дату на годы вперед
    start = models.TimeField(default=WORK_DAY_START, verbose_name='start',
                             help_text='Set the beginning of the work day', validators=[is_half_hour_validator])
    finish = models.TimeField(default=WORK_DAY_FINISH, verbose_name='end',
                              help_text='Set the end of the working day', validators=[is_half_hour_validator])

    start_break_time = models.TimeField(default=BREAK_START, blank=True, verbose_name='start break'
                                        , help_text='select the start time of the break,'
                                                    ' or leave the field blank if there is none',
                                        validators=[is_half_hour_validator])
    finish_break_time = models.TimeField(default=BREAK_FINISH, blank=True, verbose_name='finish break'
                                         , help_text='select the finish time of the break,'
                                                     ' or leave the field blank if there is none',
                                         validators=[is_half_hour_validator])

    def __str__(self):
        return self.date.strftime("%A %d %B %Y")

    def clean(self):
        errors = []
        if self.start >= self.finish:
            errors.append('Invalid time, start after finish')
        if self.start_break_time and not self.finish_break_time:
            errors.append('Invalid break, set finish break')
        if self.finish_break_time and not self.start_break_time:
            errors.append('Invalid break, set start break')
        if self.start_break_time and self.finish_break_time:
            if self.start_break_time >= self.finish_break_time:
                errors.append('Invalid time, start break after finish')
            if not self.start < self.start_break_time < self.finish:
                errors.append('Invalid time, start of a break in non-working hours')
            if not self.start < self.finish_break_time < self.finish:
                errors.append('Invalid time, finish of a break in non-working hours')
        if errors:
            raise ValidationError(message=errors)

    # @time_of_function
    def available_time(self) -> list:
        if not self.available:
            return []
        duration_day = get_event_duration(time_to_float(self.start), time_to_float(self.finish))
        duration_break = set()
        if self.start_break_time:
            duration_break = get_event_duration(time_to_float(self.start_break_time),
                                                time_to_float(self.finish_break_time))
        duration_lessons = set()
        lessons = self.lessons.all()
        if lessons.exists():
            start_lessons, finish_lessons = list(), list()
            for lesson in lessons:
                start_lessons.append(time_to_float(lesson.start))
                finish_lessons.append(time_to_float(lesson.start) + time_to_float(lesson.duration))
            duration_lessons = list(map(get_event_duration, start_lessons, finish_lessons))
            duration_lessons = set(chain(*duration_lessons))
        free_time = sorted(list(duration_day - duration_lessons - duration_break))
        return free_time

    # TODO сделать метод проверки входящих данных(что время для урока свободно) методы тертив, апдейт в вьюшку
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

    duration = models.TimeField(choices=TIME_CHOISES, default=HOUR,
                                verbose_name='lesson duration', help_text='select lesson duration')
    created_at = models.DateTimeField(auto_now_add=True)
    change_at = models.DateTimeField(auto_now=True)
    comment = models.CharField(max_length=512, verbose_name='comment', help_text='Comment', blank=True)

    def __str__(self):
        return f'{self.start} | duration: {self.duration} | {self.day} | {self.user} | ' \
               f'{self.get_subject_display()} | {self.comment}'

    @staticmethod
    def is_avaiable_time(start, duration, day) -> bool:
        if start and duration and day:
            time_lesson = get_event_duration(time_to_float(start),
                                         (time_to_float(start) + time_to_float(duration)))
            free_time = set(day.available_time())
            return time_lesson < free_time
        return False

    class Meta:
        db_table = 'Lessons'
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        unique_together = ['day', 'start']
        ordering = ['day', 'start']

# TODO может быть добавить place = дома, работа, онлайн. чойзес. Или перегруз, пофик?
