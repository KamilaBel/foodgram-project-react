from collections import defaultdict

from django.contrib.admin import display
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Exists, OuterRef, Prefetch
from recipes.validators import hex_color_regex


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'Ингредиент: {self.name}, {self.measurement_unit}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey('Recipe',
                               verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='recipe_ingredients')

    ingredient = models.ForeignKey('Ingredient',
                                   verbose_name='Ингредиент',
                                   on_delete=models.CASCADE,
                                   related_name='recipe_ingredients')

    amount = models.SmallIntegerField('Количество',
                                      validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self):
        return (f'Ингредиент для {self.recipe}, {self.ingredient.name},'
                f'{self.amount}{self.ingredient.measurement_unit}')


class Tag(models.Model):
    name = models.CharField('Название', max_length=150)
    color = models.CharField('Цвет',
                             max_length=7,
                             validators=[hex_color_regex],
                             help_text="Цвет в HEX-формате, например: #AABBCC")
    slug = models.SlugField('Идентификатор', unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'Тег: {self.slug} ({self.name})'


class RecipeQuerySet(models.QuerySet):
    def with_related(self):
        fav_obj = Favorite.objects
        sh_car_obj = ShoppingCart.objects
        rec_ing_obj = RecipeIngredient.objects
        favorites = Prefetch('favorites',
                             queryset=fav_obj.select_related('user', 'recipe'))
        shoping_cart = Prefetch(
            'shopping_cart',
            queryset=sh_car_obj.select_related('user', 'recipe')
        )
        recipe_ingredients = Prefetch(
            'recipe_ingredients',
            queryset=rec_ing_obj.select_related('recipe', 'ingredient')
        )
        return self.select_related('author') \
            .prefetch_related('tags', 'ingredients') \
            .prefetch_related(favorites) \
            .prefetch_related(shoping_cart) \
            .prefetch_related(recipe_ingredients)

    def annotate_is_favorited(self, user):
        return self.annotate(
            is_favorited=Exists(
                Favorite.objects.filter(recipe=OuterRef('pk'), user=user.pk),
            ))

    def annotate_is_in_shopping_cart(self, user):
        return self.annotate(
            is_in_shopping_cart=Exists(
                ShoppingCart.objects.filter(
                    recipe=OuterRef('pk'),
                    user=user.pk,
                ),
            ),
        )


class Recipe(models.Model):
    author = models.ForeignKey('users.User', verbose_name='Автор',
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField('Ingredient',
                                         through='RecipeIngredient')
    tags = models.ManyToManyField('Tag')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)

    objects = RecipeQuerySet().as_manager()

    def __str__(self):
        return f'Рецепт: {self.name} от {self.author.username}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    @display(description="Кол-во добавлений в избранное")
    def favorite_count(self):
        return Favorite.objects.filter(recipe_id=self.id).count()


class Favorite(models.Model):
    user = models.ForeignKey('users.User', verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey('Recipe', verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorite')
        ]

    def __str__(self) -> str:
        return str(self.recipe)


class ShoppingCart(models.Model):
    user = models.ForeignKey('users.User', verbose_name='Пользователь',
                             on_delete=models.CASCADE,
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               related_name='shopping_cart')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart')
        ]

    def __str__(self) -> str:
        return f'Корзина {self.user.username}: {self.recipe.name}'

    @classmethod
    def export(cls, user):
        result = ["Список покупок:\n"]
        total = defaultdict(int)

        recipe_ids = user.shopping_cart.values_list('recipe__id', flat=True)
        contents = (RecipeIngredient.objects.filter(recipe_id__in=recipe_ids)
                    .select_related('ingredient')
                    .order_by('ingredient__name'))
        for ingredient in contents:
            total[ingredient.ingredient] += ingredient.amount

        for ingredient, amount in total.items():
            result.append(
                f'- {ingredient.name} — {amount} '
                f'{ingredient.measurement_unit}'
            )

        return '\n'.join(result)
