import csv

from django.core.management import BaseCommand
from tqdm import tqdm

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ''' Import ingredients from CSV '''

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        file_path = options.get('csv_file')

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
                reader = csv.reader(csv_file, delimiter=',')

                created_count = 0
                for ingredient, unit in tqdm(reader,
                                             desc='Importing ingredients'):
                    obj, created = Ingredient.objects.get_or_create(
                        name=ingredient,
                        measurement_unit=unit
                    )
                    if created:
                        created_count += 1

                print(f'Imported {created_count} ingredients')

        except Exception as e:
            print('Failed to open file. Error: ' + str(e))
