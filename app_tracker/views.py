from django.shortcuts import render, redirect
from app_tracker.models import Category, Activity, TimeLog
from app_tracker.forms import TimeLogForm, ActivityForm, CategoryForm, ChartTimeIntervalForm
from collections import defaultdict
from django.contrib import messages
from datetime import timedelta
import pandas as pd
import plotly.express as px
from django.core.exceptions import ObjectDoesNotExist

# App home

def tracker_home(request):
    all_categories = Category.objects.all()

    #Create new category
    if request.method == 'POST':
        category_form = CategoryForm(request.POST or None)     
    
        if category_form.is_valid():
            category_form.save()  
            messages.success(request, ("New category has been created!"))
            return redirect('app_tracker:tracker_home')

    context ={
        'all_categories': all_categories,
    }
    
    return render(request, 'app_tracker/tracker_home.html', context)

#Category

def category(request, category_id):
    category = Category.objects.get(pk=category_id)
    category_all_activities = Activity.objects.filter(category=category).all()
    category_all_logs = TimeLog.objects.filter(activity__in=category_all_activities)
    
    colors = ['red']
    for activity in category_all_activities:
        colors.append(activity.color)
    
    #Create new Activity
    if request.method == "POST":
        activity_form = ActivityForm(request.POST or None)

        if activity_form.is_valid():
            new_activity = activity_form.save(commit=False)
            new_activity.category = category
            new_activity.save()
            messages.success(request, "New activity has been created!")
            return redirect('app_tracker:category', category.pk)
      
    #Category data frame
    all_dates = []
    for log in category_all_logs:
        if log.date not in all_dates:
            all_dates.append(log.date)

    category_page_df = pd.Series(index=all_dates, data=pd.NaT, name=f'Category "{category.name}"').to_frame()

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
    
    category_page_df.index.name = "Dates"
    category_page_df = category_page_df.fillna(timedelta(0))
    category_page_df[f'Category "{category.name}"'] = category_page_df.iloc[:, 1:].sum(axis=1)
    print(category_page_df)

    #Total time for category and activity
    category.total_time = category_page_df[f'Category "{category.name}"'].sum()
    for activity in category_all_activities:
        activity.total_time = category_page_df[f'Activity "{activity.name}"'].sum()
        try:
            activity.last_log = activity.all_logs.latest('date', 'start_time')
        except ObjectDoesNotExist:
            pass
  
    #Category chart line
    fig = px.line(
        category_page_df,
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
        'category_all_logs': category_all_logs,
    }

    return render(request, 'app_tracker/category.html', context)

def category_delete(request, category_id):
    category = Category.objects.get(pk=category_id)
    all_related_activities = Activity.objects.filter(category=category).all()

    if request.method == 'POST':
        category.delete()
        return redirect('app_tracker:tracker_home')
    
    return render(request, 'app_tracker/category_confirm_delete.html', {'category': category, 'all_related_activities': all_related_activities})

def category_edit(request, category_id):
    category = Category.objects.get(pk=category_id)

    if request.method == 'POST':
        category_form = CategoryForm(request.POST or None, instance=category)

        if category_form.is_valid():
            category_form.save()
            messages.success(request, ("Category has been updated!"))
            return redirect('app_tracker:category', category_id)

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
            return redirect('app_tracker:activity', activity.pk)
    
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

def activity_delete(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)
    all_related_logs = TimeLog.objects.filter(activity=activity).all()
    category_id = activity.category.pk

    if request.method == 'POST':
        activity.delete()
        return redirect('app_tracker:category', category_id)
    
    return render(request, 'app_tracker/activity_confirm_delete.html', {'activity': activity, 'all_related_logs': all_related_logs})

def activity_edit(request, activity_id):
    activity = Activity.objects.get(pk=activity_id)

    if request.method == 'POST':
        activity_form = ActivityForm(request.POST or None, instance=activity)
        if activity_form.is_valid():
            activity_form.save()
            messages.success(request, ("Activity has been updated!"))
            return redirect('app_tracker:activity', activity.pk)

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
        if timelog_form.is_valid():
            timelog_form.save()
            messages.success(request, ("Time log has been updated!"))
            return redirect('app_tracker:activity', activity_id)
    
    return render(request, 'app_tracker/timelog_edit.html', {'timelog': timelog, "activity_id": activity_id,})