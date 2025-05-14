from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('carbon/', views.carbon_tool, name='carbon_tool'),
    path('waste/', views.waste_tool, name='waste_tool'),
    path('design/', views.design_tool, name='design_tool'),
]