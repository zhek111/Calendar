from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from schedule.models import Lesson, WorkDay
from schedule.serializer import LessonSerializer, WorkDaySerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class WorkDayViewSet(viewsets.ViewSet):
    permission_classes = []
    serializer_class = WorkDaySerializer

    def create(self, request):
        serializer = WorkDaySerializer(data=request.data)
        #self.serializer_class вот так можно тоже.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    def list(self, request):
        workdays = WorkDay.objects.all()
        s = self.serializer_class(workdays,many=True)
        return Response(data=s.data, status=HTTP_200_OK)
