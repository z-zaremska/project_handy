from django.urls import path
from app_tracker import views

app_name = 'app_tracker'

urlpatterns = [
    path('', views.tracker_home, name='tracker_home'),
    path('category/<category_id>/', views.category, name='category'),
    path('category/<category_id>/delete', views.category_delete, name="category_delete"),    
    path('activity/<activity_id>/', views.activity, name='activity'),
    path('activity/<activity_id>/delete', views.activity_delete, name="activity_delete"),
    path('timelog/<timelog_id>/edit', views.timelog_edit, name="timelog_edit"),
    path('timelog/<timelog_id>/delete', views.timelog_delete, name="timelog_delete"),
]