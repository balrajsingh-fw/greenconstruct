from django.db import models

# Create your models here.

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    formula = models.CharField(max_length=200, blank=True, null=True)
    co2_intensity = models.FloatField()  # CO2 Intensity in kg CO2 per kg of material

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_step = models.PositiveSmallIntegerField(default=1)

    # Store raw data and AI insights as JSON
    carbon_data = models.JSONField(null=True, blank=True)
    carbon_insight = models.JSONField(null=True, blank=True)

    waste_data = models.JSONField(null=True, blank=True)
    waste_insight = models.JSONField(null=True, blank=True)

    design_data = models.JSONField(null=True, blank=True)
    design_insight = models.JSONField(null=True, blank=True)

    combined_insight = models.JSONField(null=True, blank=True)
    graph_metrics = models.JSONField(null=True, blank=True)
    combined_forecasting = models.JSONField(null=True, blank=True)  # 👈 Add this

    def __int__(self):
        return self.id

class BuildingType(models.Model):
    key = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    description = models.TextField()
    leed_applicable_ratings = models.CharField(max_length=255)

    def __str__(self):
        return self.label
