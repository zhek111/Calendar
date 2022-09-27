from django.core.management.base import BaseCommand
import datetime
import pandas as pd

from schedule.models import WorkDay


def create_days(year):
    start = datetime.datetime(year, 1, 1)
    end = datetime.datetime(year, 12, 31)
    datetime_list = pd.bdate_range(start, end).to_pydatetime()
    date_list = [date.date() for date in datetime_list]
    data = {
        'available': True,
        'start': datetime.time(9, 00),
        'finish': datetime.time(18, 00),
        'start_break_time': datetime.time(13, 00),
        'finish_break_time': datetime.time(14, 00)
    }
    days_list = []
    for day in date_list:
        data['date'] = day
        data['slug'] = data['date'].strftime("%d-%m-%y")
        days_list.append(WorkDay(**data))
    WorkDay.objects.bulk_create(days_list)


class Command(BaseCommand):
    help = 'Enter the year to create days in it'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        create_days(options['year'])
