from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import TokenAuthentication
from .serializer import ActionSerializer
from .models import Action
from config.permissions import ReadOnly


# Create your views here.

class ActionViewSet(ModelViewSet):
    serializer_class = ActionSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [ReadOnly]

    def get_queryset(self):
        verbs = ['like', 'follow']
        if not self.request.user.is_anonymous:
            actions = Action.objects.exclude(user=self.request.user)
            following_ids: list = self.request.user.following.values_list('id', flat=True)

            if following_ids:
                actions = actions.filter(user_id__in=following_ids, verb__in=verbs).prefetch_related('target')
            return actions
        return
