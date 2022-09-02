from rest_framework import serializers

from schedule.models import Lesson, WorkDay


class LessonSerializer(serializers.ModelSerializer):
    subject_di = serializers.SerializerMethodField()

    def get_subject_di(self, obj):
        return obj.get_subject_display()

    class Meta:
        model = Lesson
        fields = ['user', 'id', 'day', 'start', 'subject', 'subject_di', 'duration', 'created_at', 'change_at',
                  'comment']
        read_only_fields = ['created_at', 'change_at']

class WorkDaySerializer(serializers.ModelSerializer):
    available = serializers.BooleanField(read_only=True)

    class Meta:
        model = WorkDay
        fields = ['id', 'available', 'date', 'start', 'finish']
