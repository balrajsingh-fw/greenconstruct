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
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    building_type = models.CharField(max_length=100, blank=True, null=True)
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

    leed_certification = models.CharField(max_length=100, blank=True, null=True)
    leed_certification_insight = models.JSONField(null=True, blank=True)
    leed_graph_metrics = models.JSONField(null=True, blank=True)
    leed_combined_forecasting = models.JSONField(null=True, blank=True)
    leed_scorecard = models.JSONField(null=True, blank=True)

    well_certification = models.CharField(max_length=100, blank=True, null=True)
    well_certification_insight = models.JSONField(null=True, blank=True)
    well_graph_metrics = models.JSONField(null=True, blank=True)
    well_combined_forecasting = models.JSONField(null=True, blank=True)

    def __int__(self):
        return self.id

class BuildingType(models.Model):
    key = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=255)
    description = models.TextField()
    leed_applicable_ratings = models.CharField(max_length=255)

    def __str__(self):
        return self.label

class Document(models.Model):
    project = models.ForeignKey(Project, related_name='documents', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
