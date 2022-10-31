from rest_framework import serializers
from .models import *
from account.models import CUser


# category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# image serializer
class ImageCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'name']


class ImageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CUser
        fields = ['id', 'username', 'get_full_name']


# retrieve, put, pach, post, destroy
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        exclude = ['like']
        read_only_fields = ['photographer', 'number_of_likes']
        extra_kwargs = {
            'collection': {'write_only': True},
            'categories': {'write_only': True},
        }


# list
class ListImageSerializer(serializers.ModelSerializer):
    collection = ImageCollectionSerializer(many=True)
    photographer = ImageUserSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = Image
        fields = '__all__'
        read_only_fields = ['photographer', 'like', 'number_of_likes']


# collection
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }


class LikeActionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
