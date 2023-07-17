from django.urls import include, path
from rest_framework import routers

from users.views import UserSubscriptionsViewSet

router = routers.DefaultRouter()
router.register('users', UserSubscriptionsViewSet,
                basename='user-subscriptions')

urlpatterns = [
    path('', include(router.urls)),
]
