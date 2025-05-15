from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('carbon/', views.carbon_tool, name='carbon_tool'),
    path('waste/', views.waste_tool, name='waste_tool'),
    path('design/', views.design_tool, name='design_tool'),
    path('projects/', views.project_list, name='project_list'),   # old projects list view
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),  # create project view
    path('projects/<int:project_id>/step/<int:step>/', views.project_step, name='project_step')
]