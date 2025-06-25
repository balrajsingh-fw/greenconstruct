import os
import django
import csv

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenconstruct.settings")
django.setup()

from tools.models import BuildingType

with open("building_types.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        BuildingType.objects.create(
            key=row["key"],
            label=row["label"],
            description=row["description"],
            leed_applicable_ratings=row["leed_applicable_ratings"]
        )

print("Building types imported successfully.")
