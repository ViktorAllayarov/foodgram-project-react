from rest_framework.serializers import Serializer, SerializerMethodField

from users.models import Subscriptions


class IsSubscribedMixin(Serializer):
    is_subscribed = SerializerMethodField()

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            following=data, user=self.context.get('request').user
        ).exists()