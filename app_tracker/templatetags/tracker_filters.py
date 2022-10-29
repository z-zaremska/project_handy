from django import template
from datetime import timedelta, datetime

register = template.Library()

@register.filter(name="td_format")
def td_format(td):
    """Convert a datetime.timedelta object into days, hours and minutes."""
    seconds = td.total_seconds()
    total_time = ""
    # if seconds > 86400: # 60sec * 60min * 24hrs
    #     days = seconds // 86400
    #     total_time += f"{days} days"
    #     seconds = seconds - days*86400

    if seconds > 3600:
        hours = seconds // 3600
        total_time += f" {int(hours)} h"
        seconds = seconds - hours*3600
    
    if seconds == 0:
        total_time += " 00 min"
    elif seconds > 60:
        minutes = seconds // 60
        if minutes == "00":
            total_time += " 00 min"
        else:
            total_time += f" {int(minutes)} min"
        seconds = seconds - minutes*60

    return total_time