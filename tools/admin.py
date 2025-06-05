from django.contrib import admin
from .models import Material, Project, BuildingType, Document, ProjectTeam

# Register your models here.
admin.site.register(Project)
admin.site.register(Material)
admin.site.register(BuildingType)
admin.site.register(Document)
admin.site.register(ProjectTeam)
