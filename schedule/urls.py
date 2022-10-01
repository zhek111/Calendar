"""Calendar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
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
