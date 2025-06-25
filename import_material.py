import os
import django
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "greenconstruct.settings")
django.setup()

from tools.models import Material

with open("materials.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        Material.objects.create(
            name=row["Material Name"],
            formula=row["Scientific Formula"],
            co2_intensity=row["CO2 Intensity (kg CO2 per kg of material)"]
        )
print("Materials imported.")
