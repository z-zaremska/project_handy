from django.contrib import admin
from app_tracker.models import Category, Activity, TimeLog

# Register your models here.
admin.site.register(Category)
admin.site.register(Activity)
admin.site.register(TimeLog)