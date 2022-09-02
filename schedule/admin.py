from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget

from .models import WorkDay, Lesson
from django.contrib.admin.decorators import display
from django import forms

# Register your models here.
admin.site.register(Lesson)
import datetime

from django.forms import SelectDateWidget
from django.utils.dates import MONTHS


class CustomSelectDateWidget(SelectDateWidget):

    def init(self, attrs=None, years=None, months=None, empty_label=None):
        self.attrs = attrs or {}

        # Optional list or tuple of years to use in the "year" select box.
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year + 5)

        # Optional dict of months to use in the "month" select box.
        if months:
            self.months = months
        else:
            self.months = MONTHS

        # Optional string, list, or tuple to use as empty_label.
        if isinstance(empty_label, (list, tuple)):
            if not len(empty_label) == 3:
                raise ValueError('empty_label list/tuple must have 3 elements.')

            self.year_none_value = ('', empty_label[0])
            self.month_none_value = ('', empty_label[1])
            self.day_none_value = ('', empty_label[2])
        else:
            if empty_label is not None:
                self.none_value = ('', empty_label)

            self.year_none_value = self.none_value
            self.month_none_value = self.none_value
            self.day_none_value = self.none_value


class WorkDayAdminForm(forms.ModelForm):
    start = forms.TimeField(widget=AdminTimeWidget(format='%H:%M'))
    class Meta:
        model = WorkDay
        widgets = {
            'date': CustomSelectDateWidget
        }
        fields = '__all__'


class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'available', 'lessons_amount', 'available_time')
    forms = WorkDayAdminForm

    @display(description='lessons amount')
    def lessons_amount(self, obj):
        return obj.lessons.count()

    @display(description='Available time')
    def available_time(self, obj):
        return obj.available_time()


# TODO cделать возврат читаемой эф строки с такого то время по такое 

admin.site.register(WorkDay, WorkDayAdmin)
