from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register('actions', views.ActionViewSet, basename='actions')

urlpatterns = [
    path('', include(router.urls))
]