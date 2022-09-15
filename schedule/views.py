import datetime

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from django.contrib.auth import get_user_model
from schedule.models import Lesson, WorkDay
from schedule.serializer import LessonSerializer, WorkDaySerializer, LessonPatchSerializer
from django.conf import settings


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == "partial_update":
            return LessonPatchSerializer
        return LessonSerializer

    def create(self, request, *args, **kwargs):
        # user = request.user
        user_model = get_user_model()
        user = user_model.objects.first()
        request.data["user"] = user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_be_delete():
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Impossible delete')
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkDayViewSet(viewsets.ViewSet):
    permission_classes = []
    serializer_class = WorkDaySerializer

    def create(self, request):
        serializer = WorkDaySerializer(data=request.data)
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
