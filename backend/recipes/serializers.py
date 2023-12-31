from collections import defaultdict

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from recipes.serializers_common import RecipeShortSerializer
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientsSerializer(many=True,
                                              source='recipe_ingredients')
    author = UserSerializer()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author',
            'tags', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientsSerializer(many=True,
                                              source='recipe_ingredients')

    class Meta:
        model = Recipe
        fields = (
            'id', 'cooking_time', 'author',
            'name', 'text', 'is_favorited',
            'is_in_shopping_cart',
            'ingredients', 'tags', 'image',
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients', [])

        request = self.context["request"]
        recipe_obj = Recipe.objects.create(author_id=request.user.id,
                                           **validated_data)

        self._attach_ingredients(recipe_obj, ingredients)
        recipe_obj.tags.add(*tags)
        return recipe_obj

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients', [])
        instance = super().update(instance, validated_data)
        self._attach_ingredients(instance, ingredients)
        return instance

    def validate(self, attrs):
        ingredients = attrs.pop('recipe_ingredients', [])
        unique_ingredients = defaultdict(int)
        for ing in ingredients:
            unique_ingredients[ing['ingredient']] += ing['amount']
        attrs['recipe_ingredients'] = unique_ingredients
        return attrs

    def _attach_ingredients(self, recipe_obj, ingredients):
        ingredients_to_append = []
        for ingredient, amount in ingredients.items():
            RecipeIngredient.objects.get_or_create(recipe=recipe_obj,
                                                   ingredient=ingredient,
                                                   amount=amount)
            ingredients_to_append.append(ingredient)

        recipe_obj.ingredients.set(ingredients_to_append)


class RecipeActionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeShortSerializer(instance.recipe,
                                     context={'request': request}).data


class FavoritesSerializer(RecipeActionSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message="Recipe is already in favorites"
            )
        ]


class ShoppingCartSerializer(RecipeActionSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message="Recipe is already in shopping cart"
            )
        ]
