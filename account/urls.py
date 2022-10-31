from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('email-confirmation/<str:uid64>/<str:token>/', EmailConfirmView.as_view() ,name='email_confirm'),
    path('follow_action/', FollowActionAPIView.as_view())
]
