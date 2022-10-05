from django.urls import path, include
from app_tracker import views

app_name = 'app_tracker'

urlpatterns = [
    path('', views.TrackerHomeTemplateView.as_view(), name='tracker_home'),
    path('category/<category_id>/', views.category, name='category'),
    path('category/<category_id>/edit', views.category_edit, name='category_edit'),
    path('category/<int:pk>/delete', views.CategoryDeleteView.as_view(), name="category_delete"),    
    path('activity/<activity_id>/', views.activity, name='activity'),
    path('activity/<activity_id>/edit', views.activity_edit, name='activity_edit'),
    path('activity/<int:pk>/delete', views.ActivityDeleteView.as_view(), name="activity_delete"),
    path('timelog/<timelog_id>/edit', views.timelog_edit, name="timelog_edit"),
    path('timelog/<timelog_id>/delete', views.timelog_delete, name="timelog_delete"),
]