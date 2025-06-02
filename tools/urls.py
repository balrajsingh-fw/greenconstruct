from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),   # old projects list view
    path('projects/create/', views.project_create, name='project_create'),  # create project view
    path('projects/<int:project_id>/step/<int:step>/', views.project_step, name='project_step'),
    path('projects/<int:project_id>/leed_certificate_analysis/', views.leed_analysis, name='leed_certificate_analysis'),
    path('projects/<int:project_id>/well_certificate_analysis/', views.well_analysis, name='well_certificate_analysis'),
    path('projects/<int:project_id>/gallery/', views.project_gallery, name='project_gallery'),
    path("download-scorecard/<int:project_id>/", views.download_scorecard, name="download_scorecard"),
]