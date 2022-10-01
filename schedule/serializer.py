from django.contrib.auth import get_user_model
from rest_framework import serializers

from schedule.models import Lesson, WorkDay


class UserForLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name']
        read_only_fields = ['username', 'first_name', 'last_name']


class WorkDayForLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = ['date', ]
        read_only_fields = ['date', ]


class LessonPatchSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if not Lesson.is_avaiable_time(
                start=attrs.get('start', self.instance.start),
                duration=attrs.get('duration', self.instance.duration),
                day=attrs.get('day', self.instance.day)
        ):
            raise serializers.ValidationError(detail='Time not avaiable')
        return attrs

    class Meta:
        model = Lesson
        fields = ['user', 'id', 'day', 'start', 'subject', 'duration', 'created_at', 'change_at',
                  'comment']
        read_only_fields = ['user', 'id', 'subject', 'created_at',
                            'change_at']


class LessonSerializer(serializers.ModelSerializer):
    subject_di = serializers.SerializerMethodField()
    user_data = UserForLessonSerializer(source='user', read_only=True)
    day_data = WorkDayForLessonSerializer(source='day', read_only=True)
    work_day_date = serializers.DateField(source='day.date', read_only=True)
    
    def validate(self, attrs):
        if not Lesson.is_avaiable_time(
                start=attrs.get('start'),
                duration=attrs.get('duration'),
                day=attrs.get('day')
        ):
            raise serializers.ValidationError(detail='Time not avaiable')
        return attrs

    def get_subject_di(self, obj):
        return obj.get_subject_display()

    class Meta:
        model = Lesson
        fields = ['user', 'id', 'day', 'start', 'subject', 'subject_di', 'duration', 'created_at', 'change_at',
                  'comment', 'user_data', 'day_data', 'work_day_date']
        read_only_fields = ['created_at', 'change_at']
        # TODO разобраться, почему depth =1 не возращает attr, и как это обойти(метотд create Postman)
        # depth = 1
        # extra_kwargs = {
        #     'user': {
        #         'write_only': True    
        #     }
        # }


class WorkDaySerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(read_only=True)
    lessons_ex = serializers.BooleanField(read_only=True)
    year_of_workday = serializers.CharField(read_only=True)
    class Meta:
        model = WorkDay
        fields = ['id', 'available', 'date', 'start', 'finish', 'lessons_ex', 'year_of_workday']


class WorkDayRetrieveSerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    class Meta:
        model = WorkDay
        fields = ['slug', 'id', 'available', 'date', 'start', 'finish', 'start_break_time',
                  'finish_break_time', 'lessons']

#TODO При получение одного урока я должен получить список доступных(из трех штук) предметов для записи(изменения) 
# TODO вывести такой же масив который мы получили из get_subjects во views. Надо сделать класс метод