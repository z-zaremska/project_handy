from django.db import models
from django.utils import timezone
from datetime import timedelta, date

#Choices
COLOR_THEME_CHOICES = [
    ('gray', 'gray'),
    ('yellow', 'yellow'),
    ('purple', 'purple'),
    ('orange', 'orange'),
    ('blue', 'blue'),
    ('green', 'green'),
    ('pink', 'pink'),
]

# Models
class Category(models.Model):
    name = models.CharField(max_length=30, default="category name", unique=True)
    description = models.CharField(max_length=100, default="category description")
    
    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Activity(models.Model):
    category = models.ForeignKey(Category, related_name="all_activities", on_delete=models.CASCADE)
    name = models.CharField(max_length=200, default="activity name")
    color = models.CharField(max_length=100, choices=COLOR_THEME_CHOICES, default='gray')
    
    class Meta:
        verbose_name_plural = 'activities'
    
    def __str__(self):
        return f"{self.category} | {self.name}"


class TimeLog(models.Model):
    activity = models.ForeignKey(Activity, related_name="all_logs", on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    start_time = models.TimeField(default=timezone.now)
    log_time = models.DurationField(default=timedelta(minutes=30))

    def __str__(self):
        return f"{self.activity} | {self.log_time} - {self.date}"

    class Meta:
        verbose_name_plural = 'timelogs'
        ordering = ['-date']