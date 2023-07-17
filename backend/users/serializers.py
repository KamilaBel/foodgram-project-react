from djoser.serializers import UserSerializer as _UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow, User


class UserSerializer(_UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        current_user: User = getattr(request, 'user', None)
        if current_user is None or not current_user.is_authenticated:
            return False

        return current_user.is_subscribed(obj)


class UserSubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(source='get_recipes',
                                                read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        # Это сделано, чтобы не было циклического импорта:
        # users.serializers и recipes.serializers взаимно зависят друг от друга
        from recipes.serializers import RecipeShortSerializer

        request = self.context.get('request')

        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]

        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='User is already subscribed to this author'
            )
        ]

    def validate(self, attrs):
        user, author = attrs['user'], attrs['author']

        if user.id == author.id:
            raise ValidationError("Can't subscribe to yourself")

        return attrs

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return UserSubscriptionSerializer(instance.author,
                                          context=context).data
