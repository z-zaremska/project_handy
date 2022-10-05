"""project_handy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import ProjectHomeTemplateView, AboutMeTemplateView, ResumeTemplateView

app_name = 'project_handy'

urlpatterns = [
    #localhost:8000/admin/
    path('admin/', admin.site.urls),
    #localhost:8000/
    path('', ProjectHomeTemplateView.as_view(), name='project_home'),
    #localhost:8000/about-me
    path('about-me', AboutMeTemplateView.as_view(), name='about_me'),
    #localhost:8000/resume
    path('resume', ResumeTemplateView.as_view(), name='resume'),    
    #localhost:800/tracker/
    path ('tracker/', include('app_tracker.urls')),
]
