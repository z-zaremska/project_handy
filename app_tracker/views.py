from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from app_tracker.models import Category, Activity, TimeLog
from app_tracker.forms import TimeLogForm, ActivityForm, CategoryForm, ChartTimeIntervalForm
from django.views.generic import TemplateView, DeleteView
from datetime import timedelta
from django.db.models import Sum
import plotly.express as px

# Create your views here.
class TrackerHomeTemplateView(TemplateView):
    template_name = 'app_tracker/tracker_home.html'

    def get_context_data(self, **kwargs):
        context = super(TrackerHomeTemplateView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

#Category

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    all_category_activities = Activity.objects.filter(category=category).all()
    all_activities_time = []

    if all_category_activities:
        for activity in all_category_activities:
            activity_time = activity.all_logs.aggregate(Sum('log_time'))['log_time__sum']
            if activity_time != None:
                all_activities_time.append(activity_time)
    
    category_time = sum(all_activities_time, timedelta())

    context = {
        'category': category,
        'all_category_activities': all_category_activities,
        'category_time': category_time,
    }

    return render(request, 'app_tracker/category.html', context)

class CategoryDeleteView(DeleteView):
    model = Category
    success_url = reverse_lazy(f"app_tracker:tracker_home")

def category_edit(request, category_id):
    category = Category.objects.get(pk=category_id)

    if request.method == 'POST':
        category_form = CategoryForm(request.POST or None, instance=category)

        if category_form.is_valid():
            category_form.save()
            messages.success(request, ("Category has been updated!"))
            return redirect('app_tracker:category', category_id)

    else:
        return render(request, 'app_tracker/category_edit.html', {'category': category})

#Activity

def activity(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    all_logs = TimeLog.objects.filter(activity=activity).all()
    time_summary_activity = activity.all_logs.aggregate(Sum('log_time'))['log_time__sum']

    #Create new time log
    if request.method == 'POST':
        timelog_form = TimeLogForm(request.POST or None)     
    
        if timelog_form.is_valid():
            new_timelog = timelog_form.save(commit=False)
            new_timelog.activity = activity
            new_timelog.save()    
            messages.success(request, ("New log has been created!"))

    #Chart(date vs. logged time)
    interval_start = request.GET.get('interval_start')
    interval_end = request.GET.get('interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if interval_start:
        all_logs = all_logs.filter(date__gte=interval_start)
    if interval_end:
        all_logs = all_logs.filter(date__lte=interval_end)
     
    x_data = [log.date for log in all_logs]
    y_data = [log.log_time for log in all_logs]

    fig = px.line(
        x = x_data,
        y = y_data,
        markers=True,
        title=f"How is {activity.name} activity going",
        labels={
            'x': 'Date',
            'y': 'Time',
        },
    )

    fig.update_layout(
        title = {
            'font_size': 22,
            'xanchor': 'center',
            'x': 0.5,
        }
    )
    
    chart = fig.to_html()
    
    #Context
    context = {
        'activity': activity,
        'all_activity_logs': all_logs,
        'time_summary_activity': time_summary_activity,
        'chart': chart,
        'chart_interval_form': chart_interval_form,
        'interval_start': interval_start,
        'interval_end': interval_end, 
    }

    return render(request, 'app_tracker/activity.html', context)

class ActivityDeleteView(DeleteView):
    model = Activity
    success_url = reverse_lazy(f"app_tracker:tracker_home")

def activity_edit(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)

    if request.method == 'POST':
        activity_form = ActivityForm(request.POST or None, instance=activity)

        if activity_form.is_valid():
            activity_form.save()
            messages.success(request, ("Activity has been updated!"))
            return redirect('app_tracker:activity', activity_id)

    else:
        return render(request, 'app_tracker/activity_edit.html', {'activity': activity})

#TimeLog

def timelog_delete(request, timelog_id):
    timelog = TimeLog.objects.get(pk=timelog_id)
    activity_id = timelog.activity.pk
    timelog.delete()
    messages.success(request, ('Time log has been deleted.'))
    return redirect('app_tracker:activity', activity_id)

def timelog_edit(request, timelog_id):
    timelog = TimeLog.objects.get(pk=timelog_id)
    activity_id = timelog.activity.pk

    if request.method == 'POST':
        timelog_form = TimeLogForm(request.POST or None, instance=timelog)
        print(timelog_form.errors)

        if timelog_form.is_valid():
            timelog_form.save()
            messages.success(request, ("Time log has been updated!"))
            return redirect('app_tracker:activity', activity_id)
    
    else:
        return render(request, 'app_tracker/timelog_edit.html', {'timelog': timelog})