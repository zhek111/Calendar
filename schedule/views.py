from django.db.models import Exists, OuterRef
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from django.contrib.auth import get_user_model
from schedule.models import Lesson, WorkDay
from schedule.serializer import LessonSerializer, WorkDaySerializer, LessonPatchSerializer, WorkDayRetrieveSerializer
from rest_framework.exceptions import NotFound
from rest_framework.decorators import api_view, permission_classes
from django.db.models.functions import ExtractYear


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = []
    queryset = Lesson.objects.all().select_related('user', 'day')
    serializer = LessonSerializer

    def get_serializer_class(self):
        if self.action == "partial_update":
            return LessonPatchSerializer
        return LessonSerializer

    def create(self, request, *args, **kwargs):
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

    def retrieve(self, request, *args, **kwargs):
        response = super(LessonViewSet, self).list(self, request, *args, **kwargs)
        response.data['subjects'] = Lesson.all_choises()
        return response


class WorkDayViewSet(viewsets.ViewSet):
    permission_classes = []
    serializer_class = WorkDaySerializer

    @staticmethod
    def get_object(slug):
        try:
            obj = WorkDay.objects.prefetch_related('lessons').get(slug=slug)
            return obj
        except WorkDay.DoesNotExist:
            return None

    def retrieve(self, request, workday_slug, *args, **kwargs):
        instance = self.get_object(slug=workday_slug)
        if not instance:
            raise NotFound(detail='No day')
        serializer = WorkDayRetrieveSerializer(instance=instance)
        return Response(serializer.data, status=HTTP_200_OK)

    def list(self, request):
        workdays = WorkDay.objects.all().annotate(
            lessons_ex=Exists(Lesson.objects.filter(day_id=OuterRef('pk'))),
            year_of_workday=ExtractYear('date')
        )
        serializer = self.serializer_class(instance=workdays, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([])
def get_subjects(request):
    data = Lesson.all_choises()
    return Response(data=data, status=HTTP_200_OK)
