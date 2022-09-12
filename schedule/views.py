from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from django.contrib.auth import get_user_model
from schedule.models import Lesson, WorkDay
from schedule.serializer import LessonSerializer, WorkDaySerializer
from django.conf import settings


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def create(self, request, *args, **kwargs):
        # user = request.user
        user_model = get_user_model()
        user = user_model.objects.first()
        request.data["user"] = user.id
        serializer = LessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def get_serializer(self, *args, **kwargs):
    #     if self.action == "retrieve":
    #         return LessonSerializer
    #     return LessonSerializer


class WorkDayViewSet(viewsets.ViewSet):
    permission_classes = []
    serializer_class = WorkDaySerializer

    def create(self, request):
        serializer = WorkDaySerializer(data=request.data)
        # self.serializer_class вот так можно тоже.
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=HTTP_201_CREATED)

    def list(self, request):
        workdays = WorkDay.objects.all()
        serialalizer = self.serializer_class(instance=workdays, many=True)
        return Response(data=serialalizer.data, status=HTTP_200_OK)

    def update(self, request):
       serializer = WorkDaySerializer(data=request.data)
       pass