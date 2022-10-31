from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, ImageViewSet, CollectionViewSet, LikeActionAPIView

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('collections', CollectionViewSet)
router.register('images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('like_action/', LikeActionAPIView.as_view())
]
