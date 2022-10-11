from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from app_tracker.models import Category, Activity, TimeLog
from app_tracker.forms import TimeLogForm, ActivityForm, CategoryForm, ChartTimeIntervalForm
from django.views.generic import TemplateView, DeleteView
from datetime import timedelta
from django.db.models import Sum, Q
from collections import defaultdict
import pandas as pd
import plotly.express as px

# App home

class TrackerHomeTemplateView(TemplateView):
    template_name = 'app_tracker/tracker_home.html'

    def get_context_data(self, **kwargs):
        context = super(TrackerHomeTemplateView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


#Category

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    category_all_activities = Activity.objects.filter(category=category).all()
    category_all_logs = TimeLog.objects.filter(activity__in=category_all_activities)
    colors = ['red']
    for activity in category_all_activities:
        colors.append(activity.color)
    
    #create new Activity
    if request.method == "POST":
        activity_form = ActivityForm(request.POST or None)

        if activity_form.is_valid():
            new_activity = activity_form.save(commit=False)
            new_activity.category = category
            new_activity.save()
            messages.success(request, "New activity has been created!")
      
    #Chart data for Category
    #---> category chart data
    category_logs_dates = [log.date for log in category_all_logs]
    category_logs_time = [log.log_time for log in category_all_logs]    
    
    category_chart_data = defaultdict(timedelta)
    for date, log in zip(category_logs_dates, category_logs_time):
        if date in category_chart_data:
            category_chart_data[date] += log
        else:
            category_chart_data[date] = log
 
    x_category_data = [date for date in category_chart_data.keys()]
    y_category_data = [log for log in category_chart_data.values()]

    category_page_df = pd.Series(index=x_category_data, data=y_category_data, name=f'Category "{category.name}"').to_frame()
    category_page_df.index.name = "Dates"

    #---> activity chart data for Activity
    for activity in category_all_activities:
        activity_logs_dates = [log.date for log in TimeLog.objects.filter(activity=activity)]
        activity_logs_time = [log.log_time for log in TimeLog.objects.filter(activity=activity)]
        activity_chart_data = defaultdict(timedelta)
        for date, log in zip(activity_logs_dates, activity_logs_time): 
            if date in activity_chart_data:
                activity_chart_data[date] += log
            else:
                activity_chart_data[date] = log
        x_activity_data = [date for date in activity_chart_data.keys()]
        y_activity_data = [log for log in activity_chart_data.values()]
        activity_data = pd.Series(index=x_activity_data, data=y_activity_data)
        category_page_df[f'Activity "{activity.name}"'] = activity_data

    #Total time for category and activity
    category.total_time = category_page_df[f'Category "{category.name}"'].sum()
    for activity in category_all_activities:
        activity.total_time = category_page_df[f'Activity "{activity.name}"'].sum()
        activity.last_log = activity.all_logs.latest('date', 'start_time')
   
    fig = px.line(
        category_page_df,
        x=category_page_df.index,
        y=category_page_df.columns,
        markers=True,
        line_shape="spline",
        color_discrete_sequence = colors,
        title=f"Category <b>{category.name}</b> sum up",
        labels={
            'x': 'Date',
            'y': 'Time logged',
        },
    )
    fig.update_traces(connectgaps=True)

    fig.update_layout({
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        })

    category_chart = fig.to_html()
    
    #Context
    context = {
        'category': category,
        'category_all_activities': category_all_activities,
        'category_chart': category_chart,
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
    
    #Chart data for Activity
    #---> adjusting chart time interval
    interval_start = request.GET.get('interval_start')
    interval_end = request.GET.get('interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if interval_start:
        all_logs = all_logs.filter(date__gte=interval_start)
    if interval_end:
        all_logs = all_logs.filter(date__lte=interval_end)
     
    #---> chart data
    activity_logs_dates = [log.date for log in all_logs]
    activity_logs_time = [log.log_time for log in all_logs]

    activity_chart_data = defaultdict(timedelta)
    for date, log in zip(activity_logs_dates, activity_logs_time):
        if date in activity_chart_data:
            activity_chart_data[date] += log
        else:
            activity_chart_data[date] = log

    x_activity_data = [date for date in activity_chart_data.keys()]
    y_activity_data = [log for log in activity_chart_data.values()]

    activity_page_df = pd.Series(index=x_activity_data, data=y_activity_data, name=f"Activity {activity.name}").to_frame()
    activity_page_df.index.name = "Dates"

    activity.total_time = activity_page_df[f"Activity {activity.name}"].sum()
    
    # #---> chart configuration
    fig = px.line(
        activity_page_df,
        x=activity_page_df.index,
        y=activity_page_df.columns,
        markers=True,
        line_shape="spline",
        color_discrete_sequence = [activity.color],
        title=f"Activity <b>{activity.name}</b> sum up",
        labels={
            'x': 'Date',
            'y': 'Time logged',
        },
    )

    fig.update_traces(connectgaps=True)

    fig.update_layout({
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        })
    
    activity_chart = fig.to_html()

    #Create new time log
    if request.method == 'POST':
        timelog_form = TimeLogForm(request.POST or None)     
    
        if timelog_form.is_valid():
            new_timelog = timelog_form.save(commit=False)
            new_timelog.activity = activity
            new_timelog.save()    
            messages.success(request, ("New log has been created!")) 
    
    #Context
    context = {
        'activity': activity,
        'all_activity_logs': all_logs,
        'activity_chart': activity_chart,
        'chart_interval_form': chart_interval_form,
        'interval_start': interval_start,
        'interval_end': interval_end,
        'activity_page_df': activity_page_df,
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