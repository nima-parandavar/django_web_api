from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from drf_psq import PsqMixin, Rule

from .models import Image, Category, Collection
from .serializers import (CategorySerializer, ImageSerializer, ImageUserSerializer,
                          ImageCollectionSerializer, ListImageSerializer, CollectionSerializer, LikeActionSerializer)
from config.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from action.utils import create_action

# Create your views here.

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        category = get_object_or_404(Category, pk=kwargs.get('pk'))
        serializer = CategorySerializer(category)

        images = category.image_categories.all()
        image_serializer = ImageSerializer(images, many=True)
        return Response({'category': serializer.data, 'images': image_serializer.data})


class ImageViewSet(PsqMixin, ModelViewSet):
    queryset = Image.available_images.all()
    serializer_class = ImageSerializer

    psq_rules = {
        ('create', 'destroy', 'update', 'partial_update'): [
            Rule([IsOwnerOrReadOnly & permissions.IsAuthenticatedOrReadOnly],
                 ImageSerializer,
                 queryset=Image.available_images.all())
        ]
    }

    def list(self, request, *args, **kwargs):
        serializer = ListImageSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        image = get_object_or_404(Image.available_images, pk=kwargs.get('pk'))
        image_serializer = ImageSerializer(image)

        user_serializer = ImageUserSerializer(image.photographer)
        categories_serializer = CategorySerializer(image.categories, many=True)
        collections_serializer = ImageCollectionSerializer(image.collection, many=True)

        return Response(
            {'image': image_serializer.data, 'photographer': user_serializer.data,
             'categories': categories_serializer.data, 'collection': collections_serializer.data}
        )

    def create(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['photographer'] = self.request.user
        serializer.save()
        return Response(serializer.data)


class CollectionViewSet(PsqMixin, ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    psq_rules = {
        ('create', 'update', 'partial_update', 'destroy'): [
            Rule([IsOwnerOrReadOnly & permissions.IsAuthenticatedOrReadOnly], CollectionSerializer),
        ]
    }

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user'] = self.request.user
        serializer.save()
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs.get('pk'))
        serializer = CollectionSerializer(collection)
        user_serializer = ImageUserSerializer(collection.user)
        images = collection.collections.all()
        image_serializer = ListImageSerializer(images, many=True)

        return Response({'collection': serializer.data, 'user': user_serializer.data, 'images': image_serializer.data})


class LikeActionAPIView(APIView):
    # todo check authentication user
    def post(self, request, **kwargs):
        serializer = LikeActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        img = get_object_or_404(Image.available_images, id=serializer.validated_data['id'])
        user_images = request.user.images.all()

        if img not in user_images:
            user_liked_images: list = request.user.likes.values_list("id", flat=True)

            if img.id in user_liked_images:
                state = create_action(request.user, 'disliked', img)
                if state:
                    img.like.remove(request.user)
                    return Response({'msg': 'user disliked a photo'})
            else:
                state = create_action(request.user, 'like', img)
                if state:
                    img.like.add(request.user)
                    return Response({"msg": "user liked a photo"})