from django.urls import path, include

from schedule.views import LessonViewSet, WorkDayViewSet, get_subjects
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'lessons', LessonViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('workdays/', WorkDayViewSet.as_view({'get': 'list'})),
    path('workdays/<slug:workday_slug>/', WorkDayViewSet.as_view({'get': 'retrieve'})),
    path('subjects/', get_subjects),
    path('lessons/', LessonViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('lessons/<int:lesson_id>/', LessonViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
]
