from django.contrib import admin
from django.contrib.admin.widgets import AdminTimeWidget
import datetime
from .models import WorkDay, Lesson, get_time_interval
from django.contrib.admin.decorators import display
from django import forms
from django.utils.dates import MONTHS



class CustomSelectDateWidget(forms.SelectDateWidget):

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
class LessonAdmin(admin.ModelAdmin):
    search_fields = ('day', )
    autocomplete_fields = ('day', )

class WorkDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'available', 'lessons_amount', 'available_time')
    forms = WorkDayAdminForm
    readonly_fields = ('slug',)

    @display(description='lessons amount')
    def lessons_amount(self, obj):
        return obj.lessons.count()

    @display(description='Available time')
    def available_time(self, obj):
        return f'{", ".join([": ".join(list(map(str,interval))) for interval in get_time_interval(obj.available_time())])}'



admin.site.register(WorkDay, WorkDayAdmin)
admin.site.register(Lesson, LessonAdmin)
# TODO скопировать код из телеграмма и разобраться в чем у меня отличие (должен зарабоать виджет) 
