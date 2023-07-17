from typing import Type, Union

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.filters import IngredientSearchFilter, RecipeFilter
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from recipes.serializers import (FavoritesSerializer, IngredientSerializer,
                                 RecipeCreateUpdateSerializer,
                                 RecipeListRetrieveSerializer,
                                 ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().with_related()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeListRetrieveSerializer
        return RecipeCreateUpdateSerializer

    def get_queryset(self):
        user = self.request.user
        var = self.queryset.annotate_is_favorited(user)
        return var.annotate_is_in_shopping_cart(user)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk: int):
        return self._add(FavoritesSerializer)

    @favorite.mapping.delete
    def unfavorite(self, request, pk: int):
        return self._cancel(Favorite)

    @action(detail=True, methods=['POST'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk: int):
        return self._add(ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk: int):
        return self._cancel(ShoppingCart)

    def _add(self, serializer_class: Union[Type[FavoritesSerializer],
                                           Type[ShoppingCartSerializer]]):
        recipe = self.get_object()

        serializer = serializer_class(data={
            'user': self.request.user.id,
            'recipe': recipe.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _cancel(self, model: Union[Type[Favorite], Type[ShoppingCart]]):
        recipe = self.get_object()
        obj = get_object_or_404(model, user=self.request.user, recipe=recipe)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_list_str = ShoppingCart.export(request.user)
        response = HttpResponse(shopping_list_str, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="list.txt"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
