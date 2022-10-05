from django.forms import ModelForm
from app_tracker.models import TimeLog, Activity, Category

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class ActivityForm(ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'color',]

class TimeLogForm(ModelForm):
    class Meta:
        model = TimeLog
        fields = ['date', 'log_time', 'start_time',]