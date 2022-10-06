from django.core.management.base import BaseCommand
import datetime
import pandas as pd

from schedule.models import WorkDay, WORK_DAY_START, WORK_DAY_FINISH, BREAK_START, BREAK_FINISH, Lesson


def create_days(year: int, flag: bool = False) -> None:
    start = datetime.datetime(year, 1, 1)
    end = datetime.datetime(year, 12, 31)
    datetime_list = pd.bdate_range(start, end).to_pydatetime()
    date_list = [date.date() for date in datetime_list]
    data = {
        'available': True,
        'start': WORK_DAY_START,
        'finish': WORK_DAY_FINISH,
        'start_break_time': BREAK_START,
        'finish_break_time': BREAK_FINISH
    }
    days_list = [WorkDay(**data, date=day, slug=WorkDay.generate_slug(day)) for day in date_list]
    WorkDay.objects.bulk_create(days_list, ignore_conflicts=flag)


class Command(BaseCommand):
    help = 'Enter the year to create days in it, use flag for ignore conflicts'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('--flag', type=bool, help='use for force create')

    def handle(self, *args, **options):
        if options['flag']:
            pass
        elif d := WorkDay.objects.filter(date__year=options['year']):
            count_lessons = Lesson.objects.filter(day__date__year=options['year']).count()
            return self.stdout.write(
                self.style.ERROR(
                    f'Days already exists. {d.count()} days already exist, '
                    f'lessons = {count_lessons}, use any --flag for force create.'))
        create_days(options['year'], True)
        self.stdout.write(self.style.SUCCESS('Successfully'))
