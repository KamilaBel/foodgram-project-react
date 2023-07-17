from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import Follow, User
from users.serializers import FollowSerializer, UserSubscriptionSerializer


class UserSubscriptionsViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all().prefetch_related('follower')
    permission_classes = (AllowAny,)

    @action(detail=False)
    def subscriptions(self, request):
        qs = User.objects.filter(following__user_id=request.user.id)
        qs = self.paginate_queryset(qs)
        serializer = UserSubscriptionSerializer(qs, many=True,
                                                context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, pk: int):
        author = self.get_object()
        serializer = FollowSerializer(
            context={'request': request},
            data={
                'user': self.request.user.id,
                'author': author.id,
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk: int):
        author = self.get_object()
        subscription = get_object_or_404(Follow,
                                         author_id=author.id,
                                         user_id=self.request.user.id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
