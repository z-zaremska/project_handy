from django import forms
from app_tracker.models import TimeLog, Activity, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'color',]

class TimeLogForm(forms.ModelForm):
    class Meta:
        model = TimeLog
        fields = ['date', 'log_time', 'start_time',]

class ChartTimeIntervalForm(forms.Form):
    adjust_interval_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) 
    adjust_interval_end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'})) 