from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from app_tracker.models import Category, Activity, TimeLog
from app_tracker.forms import TimeLogForm, ActivityForm, CategoryForm, ChartTimeIntervalForm
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict
from django.contrib import messages
from datetime import timedelta
import pandas as pd
import plotly.express as px

#FUNCTIONS

def check_category_owner(category, request):
    """Checks if the owner of the categroy is recent logged in user."""
    if category.owner != request.user:
        raise Http404

#VIEWS

#App home

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

@login_required
def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    check_category_owner(category, request)
    category_all_activities = Activity.objects.filter(category=category).all()
    category_all_logs = TimeLog.objects.filter(activity__in=category_all_activities)
    
    # Activities colors for chart
    colors = ['red'] # default category color
    for activity in category_all_activities:
        colors.append(activity.color)
    
    # Multiple forms
    if request.method == 'POST':
        # create activity
        if request.POST.get("form_type") == 'create_activity_form':
            activity_form = ActivityForm(request.POST or None)

            if activity_form.is_valid():
                new_activity = activity_form.save(commit=False)
                new_activity.category = category
                new_activity.save()
                messages.success(request, "New activity has been created!")
                return redirect('app_tracker:category', category.pk)

        # edit category
        elif request.POST.get("form_type") == 'edit_category_form':
            category_form = CategoryForm(request.POST or None, instance=category)

            if category_form.is_valid():
                category_form.save()
                messages.success(request, ("Category has been updated!"))
                return redirect('app_tracker:category', category_id)
      
    # Category data frame
    #---> adjusting chart time interval

    adjust_interval_start = request.GET.get('adjust_interval_start')
    adjust_interval_end = request.GET.get('adjust_interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if adjust_interval_start:
        if adjust_interval_start == 'reset':
            category_all_logs = category_all_logs            
        else:
            category_all_logs = category_all_logs.filter(date__gte=adjust_interval_start)
    if adjust_interval_end:
        if adjust_interval_end == 'reset':
            category_all_logs = category_all_logs            
        else:
            category_all_logs = category_all_logs.filter(date__lte=adjust_interval_end)
     
    try:
        interval_start = category_all_logs.earliest('date', 'start_time').date
        interval_end = category_all_logs.latest('date', 'start_time').date
    except ObjectDoesNotExist:
        interval_start = None
        interval_end = None

    #---> chart data
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

    # Total time for category and activity
    category.total_time = category_page_df[f'Category "{category.name}"'].sum()
    for activity in category_all_activities:
        activity.total_time = category_page_df[f'Activity "{activity.name}"'].sum()
        try:
            activity.last_log = activity.all_logs.latest('date', 'start_time')
        except ObjectDoesNotExist:
            pass

    # Category chart - line
    fig = px.line(
        category_page_df,
        markers=True,
        line_shape="spline",
        color_discrete_sequence = colors,
        title=None,
    )

    fig.update_traces(
        connectgaps=True,
        line=dict(dash='dash', width=4), selector = ({'name': f'Category "{category.name}"'}),
        )

    fig.update_layout(
        xaxis=dict(title=None,showgrid=True, gridwidth=1, gridcolor='Lightgray'),
        yaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray',),
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
        height=300,
        plot_bgcolor='white',
        hovermode=False,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bordercolor='black',
            borderwidth=2,
            title={'text': None})
        )
   
    category_chart = fig.to_html(config = {'displayModeBar': False},)

    # Context
    context = {
        'category': category,
        'category_all_activities': category_all_activities,
        'category_chart': category_chart,
        'category_all_logs': category_all_logs,
        'adjust_interval_start': adjust_interval_start,
        'adjust_interval_end': adjust_interval_end,
        'interval_start': interval_start,
        'interval_end': interval_end,
        'chart_interval_form': chart_interval_form,
    }

    return render(request, 'app_tracker/category.html', context)

@login_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    check_category_owner(category, request)
    all_related_activities = Activity.objects.filter(category=category).all()

    if request.method == 'POST':
        category.delete()
        return redirect('app_tracker:tracker_home')
    
    return render(request, 'app_tracker/category_confirm_delete.html', {'category': category, 'all_related_activities': all_related_activities})

#Activity

@login_required
def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    check_category_owner(activity.category, request)    
    all_logs = TimeLog.objects.filter(activity=activity).all()
    
    # Chart data for Activity
    #---> adjusting chart time interval
    adjust_interval_start = request.GET.get('adjust_interval_start')
    adjust_interval_end = request.GET.get('adjust_interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if adjust_interval_start:
        if adjust_interval_start == 'reset':
            all_logs = all_logs
        else:
            all_logs = all_logs.filter(date__gte=adjust_interval_start)
    if adjust_interval_end:
        if adjust_interval_end == 'reset':
            all_logs = all_logs        
        else:
            all_logs = all_logs.filter(date__lte=adjust_interval_end)
     
    try:
        interval_start = all_logs.earliest('date', 'start_time').date
        interval_end = all_logs.latest('date', 'start_time').date
    except ObjectDoesNotExist:
        interval_start = None
        interval_end = None

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
    
    #---> chart configuration
    fig = px.line(
        activity_page_df,
        markers=True,
        line_shape="spline",
        color_discrete_sequence = [activity.color],
        title=None,
    )

    fig.update_traces(connectgaps=True)

    fig.update_layout(
        xaxis=dict(title=None,showgrid=True, gridwidth=1, gridcolor='Lightgray'),
        yaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray',),
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
        height=300,
        plot_bgcolor='white',
        hovermode=False,
        showlegend=False,
    )
    
    activity_chart = fig.to_html(config = {'displayModeBar': False},)

    # Multiple forms
    if request.method == 'POST':
        # create time log
        if request.POST.get("form_type") == 'create_timelog_form':
            timelog_form = TimeLogForm(request.POST or None)     
        
            if timelog_form.is_valid():
                new_timelog = timelog_form.save(commit=False)
                new_timelog.activity = activity
                new_timelog.save()    
                messages.success(request, ("New log has been created!"))
                return redirect('app_tracker:activity', activity.pk)
        
        # elif request.POST.get("form_type") == 'edit_timelog_form':

        elif request.POST.get("form_type") == 'edit_activity_form':
            activity_form = ActivityForm(request.POST or None, instance=activity)
            if activity_form.is_valid():
                activity_form.save()
                messages.success(request, ("Activity has been updated!"))
                return redirect('app_tracker:activity', activity.pk)
    
    #Context
    context = {
        'activity': activity,
        'activity_all_logs': all_logs,
        'activity_chart': activity_chart,
        'chart_interval_form': chart_interval_form,
        'adjust_interval_start': adjust_interval_start,
        'adjust_interval_end': adjust_interval_end,
        'interval_start': interval_start,
        'interval_end': interval_end,
        'activity_page_df': activity_page_df,
    }

    return render(request, 'app_tracker/activity.html', context)

@login_required
def activity_delete(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    check_category_owner(activity.category, request)    
    all_related_logs = TimeLog.objects.filter(activity=activity).all()
    category_id = activity.category.pk

    if request.method == 'POST':
        activity.delete()
        return redirect('app_tracker:category', category_id)
    
    return render(request, 'app_tracker/activity_confirm_delete.html', {'activity': activity, 'all_related_logs': all_related_logs})

#TimeLog

@login_required
def timelog_edit(request, timelog_id):
    timelog = get_object_or_404(TimeLog, pk=timelog_id)
    activity = timelog.activity
    check_category_owner(activity.category, request) 

    if request.method == 'POST':
        timelog_form = TimeLogForm(request.POST or None, instance=timelog)
        if timelog_form.is_valid():
            timelog_form.save()
            messages.success(request, ("Time log has been updated!"))
            return redirect('app_tracker:activity', activity.pk)
    
    form = TimeLogForm(instance=timelog)
    return render(request, 'app_tracker/timelog_edit.html', {'timelog': timelog, "activity_id": activity.pk, 'form': form,})

@login_required
def timelog_delete(request, timelog_id):
    timelog = get_object_or_404(TimeLog, pk=timelog_id)
    activity = timelog.activity
    check_category_owner(activity.category, request)
    activity_id = activity.pk
    timelog.delete()
    messages.success(request, ('Time log has been deleted.'))
    return redirect('app_tracker:activity', activity_id)