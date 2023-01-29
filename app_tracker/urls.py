from django.urls import path
from app_tracker import views

app_name = 'app_tracker'

urlpatterns = [
    # App main page
    path('', views.tracker_home, name='tracker_home'),
    # Category
    path('category/<category_id>/', views.category, name='category'),
    # Delete category confirmation
    path('category/<category_id>/delete', views.category_delete, name="category_delete"),
    # Activity
    path('activity/<activity_id>/', views.activity, name='activity'),
    # Delete activity confirmation
    path('activity/<activity_id>/delete', views.activity_delete, name="activity_delete"),
    # Timelog edit
    path('timelog/<timelog_id>/edit', views.timelog_edit, name="timelog_edit"),
    # Timelog delete
    path('timelog/<timelog_id>/delete', views.timelog_delete, name="timelog_delete"),
]
