from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions
from rest_framework import status
from rest_framework.authtoken.models import Token
from drf_psq import PsqMixin, Rule
from rest_framework.views import APIView


from .models import CUser
from .serializers import UserSerializer, FollowActionSerializer
from image.serializers import ListImageSerializer, CollectionSerializer
from config.permissions import IsSelfOrReadOnly
from .token_generator import confirm_email_token_generator
from .mails import send_confirmation_done
from action.utils import create_action


# Create your views here.


class UserViewSet(PsqMixin, ModelViewSet):
    queryset = CUser.active_users.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)

    psq_rules = {
        ('update', 'destroy', 'partial_update'): [
            Rule([IsSelfOrReadOnly & permissions.IsAuthenticatedOrReadOnly], UserSerializer,
                 queryset=lambda self: CUser.objects.all())
        ]
    }

    def retrieve(self, request, *args, **kwargs):
        user = get_object_or_404(CUser.active_users, pk=kwargs.get('pk'))
        serializer = UserSerializer(user)
        image_serializer = ListImageSerializer(user.images.all(), many=True)
        collection_serializer = CollectionSerializer(user.collections, many=True)

        return Response({
            'user': serializer.data,
            'images': image_serializer.data,
            'collections': collection_serializer.data
        })


class LoginView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class EmailConfirmView(APIView):
    def get(self, request, **kwargs):
        user_id = force_str(urlsafe_base64_decode(kwargs.get('uid64')))
        token = kwargs.get('token')
        user: CUser = get_object_or_404(CUser.inactive_users, id=user_id)
        if confirm_email_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            token_, created = Token.objects.get_or_create(user=user)
            send_confirmation_done(user)
            return Response({'token': token_.key})
        return Response({'token': None}, status=status.HTTP_406_NOT_ACCEPTABLE)


class FollowActionAPIView(APIView):
    # todo check if user is authenticated
    # TODO: check if user do a similar action less than one min
    def post(self, request, **kwargs):
        serializer = FollowActionSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(CUser.active_users, id=serializer.validated_data['id'])
            if serializer.validated_data['id'] != request.user.id:
                user_followers: list = request.user.following.values_list('id', flat=True)
                # prevent user to do similar action in one minute
                if user.id in user_followers:
                    state = create_action(self.request.user, 'unfollow', user)
                    if state:
                        request.user.following.remove(user)
                        return Response({'msg': 'user unfollowed'})

                else:
                    state = create_action(self.request.user, 'follow', user)
                    if state:
                        request.user.following.add(user)
                        return Response({'msg': "user followed"})
