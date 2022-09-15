from django.contrib.auth import get_user_model
from rest_framework import serializers

from schedule.models import Lesson, WorkDay


class UserForLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name']
        read_only_fields = ['username', 'first_name', 'last_name']


class LessonPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['user', 'id', 'day', 'start', 'subject', 'subject_di', 'duration', 'created_at', 'change_at',
                  'comment', 'user_data']
        read_only_fields = ['user', 'id', 'day', 'start', 'subject', 'subject_di', 'duration', 'created_at',
                            'change_at', 'user_data']



class LessonSerializer(serializers.ModelSerializer):
    subject_di = serializers.SerializerMethodField()
    user_data = UserForLessonSerializer(source='user', read_only=True)

    # TODO вырезать из ответа user(не user_data)
    def validate(self, attrs):
        avaiable = Lesson.is_avaiable_time(
            start=attrs.get('start'),
            duration=attrs.get('duration'),
            day=attrs.get('day')
        )
        if not avaiable:
            raise serializers.ValidationError(detail='Time not avaiable')
        return attrs

    def get_subject_di(self, obj):
        return obj.get_subject_display()

    class Meta:
        model = Lesson
        fields = ['user', 'id', 'day', 'start', 'subject', 'subject_di', 'duration', 'created_at', 'change_at',
                  'comment', 'user_data']
        read_only_fields = ['created_at', 'change_at']
        depth = 1
        # extra_kwargs = {
        #     'user': {
        #         'write_only': True    
        #     }
        # }


class WorkDaySerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkDay
        fields = ['id', 'available', 'date', 'start', 'finish']
