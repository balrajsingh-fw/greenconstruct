from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('projects/', views.project_list, name='project_list'),   # old projects list view
    path('projects/create/', views.project_create, name='project_create'),  # create project view
    path('projects/<int:project_id>/step/<int:step>/', views.project_step, name='project_step'),
    path('leed_certificate_analysis/<int:project_id>/', views.leed_analysis, name='leed_certificate_analysis'),
    path('well_certificate_analysis/<int:project_id>/', views.well_analysis, name='well_certificate_analysis'),
    path('projects/<int:project_id>/gallery/', views.project_gallery, name='project_gallery'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('leed_documentation/<int:project_id>/', views.leed_documentation, name='leed_docs'),
    path('submit_leed_docs/', views.submit_leed_docs, name='submit_leed_docs'),
    path('submit_l_n_t_form/', views.submit_l_n_t_form, name='submit_l_n_t_form'),
    path('well_documentation/<int:project_id>/', views.well_documentation, name='well_docs'),
    path("download-leed-scorecard/<int:project_id>/", views.download_leed_scorecard, name="download_leed_scorecard"),
    path("download-well-scorecard/<int:project_id>/", views.download_well_scorecard, name="download_well_scorecard"),
]