from django.db import models

# Create your models here.

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    formula = models.CharField(max_length=200, blank=True, null=True)
    co2_intensity = models.FloatField()  # CO2 Intensity in kg CO2 per kg of material

    def __str__(self):
        return self.name