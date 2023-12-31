# Generated by Django 4.2.3 on 2023-07-17 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient', 'amount'), name='unique_recipe_ingredient'),
        ),
    ]
