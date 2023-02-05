from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from app_tracker.models import Category, Activity, TimeLog, COLOR_THEME_CHOICES
from app_tracker.forms import TimeLogForm, ActivityForm, CategoryForm, ChartTimeIntervalForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from decouple import config

# create connection to PostgreSQL database
engine = create_engine(config('DATABASE_URL'))


# FUNCTIONS


def check_category_owner(category, request):
    """Checks if the owner of the category is recent logged-in user."""
    if category.owner != request.user:
        raise Http404


# VIEWS

# App home


def tracker_home(request):
    all_categories = []
    if request.user.is_anonymous is not True:
        all_categories = Category.objects.all().filter(owner=request.user)

    # Create new category
    if request.method == 'POST':
        category_form = CategoryForm(request.POST or None)
        print(category_form.is_valid())

        if category_form.is_valid():
            new_category = category_form.save(commit=False)
            new_category.owner = request.user
            new_category.save()
            messages.success(request, "New category has been created!")
            return redirect('app_tracker:tracker_home')

    context = {
        'all_categories': all_categories,
    }

    return render(request, 'app_tracker/tracker_home.html', context)


# Category


def category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category_all_activities = Activity.objects.filter(category=category).all()
    category_all_logs = TimeLog.objects.filter(activity__in=category_all_activities)

    # Activities colors for chart
    colors = [activity.color for activity in category_all_activities]

    # Multiple forms
    if request.method == 'POST':
        check_category_owner(category, request)
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
                messages.success(request, "Category has been updated!")
                return redirect('app_tracker:category', category_id)

    # Category data frame
    # ---> adjusting data frame time interval
    try:
        first_log = category_all_logs.earliest('date', 'start_time').date
        last_log = category_all_logs.latest('date', 'start_time').date
        logging_period = pd.date_range(first_log, last_log)
    except:
        pass

    adjust_interval_start = request.GET.get('adjust_interval_start')
    adjust_interval_end = request.GET.get('adjust_interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if adjust_interval_start:
        if adjust_interval_start in logging_period:
            category_all_logs = category_all_logs.filter(date__gte=adjust_interval_start)
        elif adjust_interval_start == 'reset':
            category_all_logs = category_all_logs
        else:
            pass
    if adjust_interval_end:
        if adjust_interval_end in logging_period:
            category_all_logs = category_all_logs.filter(date__lte=adjust_interval_end)
        elif adjust_interval_end == 'reset':
            category_all_logs = category_all_logs
        else:
            pass

    try:
        interval_start = category_all_logs.earliest('date', 'start_time').date
        interval_end = category_all_logs.latest('date', 'start_time').date
    except ObjectDoesNotExist:
        interval_start = None
        interval_end = None

    # ---> page data frame
    category_timelogs_sql = f"""
    SELECT att.id, att.date, att.log_time, att.start_time, ata.name AS activity_name
    FROM app_tracker_timelog att
    JOIN app_tracker_activity ata 
    ON att.activity_id = ata.id
    JOIN app_tracker_category atc 
    ON atc.id = ata.category_id
    WHERE atc.name = '{category.name}';
    """
    category_page_df = pd.read_sql(category_timelogs_sql, engine)
    category_page_df["log_time_h"] = category_page_df.log_time.dt.total_seconds() / 3600

    # Total time for category and activity
    category.total_time = category_page_df.log_time.sum()
    for activity in category_all_activities:
        activity.total_time = category_page_df.groupby("activity_name").log_time.sum().loc[activity.name]
        try:
            activity.last_log = activity.all_logs.latest('date', 'start_time')
            # category_page_df.loc[category_page_df.activity_name == activity.name, ["date", "start_time"]].max()
        except ObjectDoesNotExist:
            pass

    # Category chart - line
    # ---> chart configuration
    fig = px.bar(
        x=category_page_df.date,
        y=category_page_df.log_time_h,
        color=category_page_df.activity_name,
        color_discrete_sequence=colors,
    )

    fig.update_layout(
        xaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray', tickangle=0,
                   tickformat='%d.%m', ),
        yaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray', ticksuffix='h',
                   zerolinecolor='Lightgray'),
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
        height=300,
        plot_bgcolor='white',
        hovermode=False,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.10,
            xanchor="left",
            x=0.00,
            title={'text': None})
    )

    category_chart = fig.to_html(config={'displayModeBar': False}, )

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

    return render(request, 'app_tracker/category_confirm_delete.html',
                  {'category': category, 'all_related_activities': all_related_activities})


# Activity

def activity(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    all_logs = TimeLog.objects.filter(activity=activity).all()

    # Multiple forms
    if request.method == 'POST':
        check_category_owner(activity.category, request)
        # create time log
        if request.POST.get("form_type") == 'create_timelog_form':
            timelog_form = TimeLogForm(request.POST or None)

            if timelog_form.is_valid():
                new_timelog = timelog_form.save(commit=False)
                new_timelog.activity = activity
                new_timelog.save()
                messages.success(request, "New log has been created!")
                return redirect('app_tracker:activity', activity.pk)

        # edit activity
        elif request.POST.get("form_type") == 'edit_activity_form':
            activity_form = ActivityForm(request.POST or None, instance=activity)

            if activity_form.is_valid():
                activity_form.save()
                messages.success(request, "Activity has been updated!")
                return redirect('app_tracker:activity', activity.pk)

    # Activity data frame
    # ---> adjusting data frame time interval
    try:
        first_log = all_logs.earliest('date', 'start_time').date
        last_log = all_logs.latest('date', 'start_time').date
        logging_period = pd.date_range(first_log, last_log)
    except:
        pass

    adjust_interval_start = request.GET.get('adjust_interval_start')
    adjust_interval_end = request.GET.get('adjust_interval_end')
    chart_interval_form = ChartTimeIntervalForm()

    if adjust_interval_start:
        if adjust_interval_start in logging_period:
            all_logs = all_logs.filter(date__gte=adjust_interval_start)
        elif adjust_interval_start == 'reset':
            all_logs = all_logs
        else:
            pass
    if adjust_interval_end:
        if adjust_interval_end in logging_period:
            all_logs = all_logs.filter(date__lte=adjust_interval_end)
        elif adjust_interval_end == 'reset':
            all_logs = all_logs
        else:
            pass

    try:
        interval_start = all_logs.earliest('date', 'start_time').date
        interval_end = all_logs.latest('date', 'start_time').date
    except ObjectDoesNotExist:
        interval_start = None
        interval_end = None

    # ---> page data frame
    activity_logs_sql = f"""
    SELECT att.id, att.date, att.log_time, att.start_time
    FROM app_tracker_timelog att
    JOIN app_tracker_activity ata 
    ON att.activity_id = ata.id
    WHERE ata.name = '{activity.name}';
    """
    activity_page_df = pd.read_sql(activity_logs_sql, engine)
    activity_page_df["log_time_h"] = activity_page_df.log_time.dt.total_seconds() / 3600


    # Total time for activity
    activity.total_time = activity_page_df.log_time.sum()

    # Activity chart - bar
    # ---> chart configuration
    fig = px.bar(
        activity_page_df.groupby("date").log_time_h.sum(),
        color_discrete_sequence=[activity.color]
    )

    fig.update_layout(
        xaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray', tickangle=0,
                   tickformat='%d.%m', ),
        yaxis=dict(title=None, showgrid=True, gridwidth=1, gridcolor='Lightgray', ticksuffix='h',
                   zerolinecolor='Lightgray'),
        margin=dict(l=0, r=0, b=0, t=0),
        autosize=True,
        height=300,
        plot_bgcolor='white',
        hovermode=False,
        showlegend=False,
    )

    activity_chart = fig.to_html(config={'displayModeBar': False}, )

    # Context
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
        'colors_list': [color[0] for color in COLOR_THEME_CHOICES],
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

    return render(request, 'app_tracker/activity_confirm_delete.html',
                  {'activity': activity, 'all_related_logs': all_related_logs})


# TimeLog

@login_required
def timelog_edit(request, timelog_id):
    timelog = get_object_or_404(TimeLog, pk=timelog_id)
    activity = timelog.activity
    check_category_owner(activity.category, request)

    if request.method == 'POST':
        timelog_form = TimeLogForm(request.POST or None, instance=timelog)
        if timelog_form.is_valid():
            timelog_form.save()
            messages.success(request, "Time log has been updated!")
            return redirect('app_tracker:activity', activity.pk)

    form = TimeLogForm(instance=timelog)
    return render(request, 'app_tracker/timelog_edit.html',
                  {'timelog': timelog, "activity_id": activity.pk, 'form': form, })


@login_required
def timelog_delete(request, timelog_id):
    timelog = get_object_or_404(TimeLog, pk=timelog_id)
    activity = timelog.activity
    check_category_owner(activity.category, request)
    activity_id = activity.pk
    timelog.delete()
    messages.success(request, 'Time log has been deleted.')
    return redirect('app_tracker:activity', activity_id)
