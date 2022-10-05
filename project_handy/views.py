from django.shortcuts import render
from django.views.generic import TemplateView

class ProjectHomeTemplateView(TemplateView):
    template_name = 'project_home.html'

class AboutMeTemplateView(TemplateView):
    template_name = 'about_me.html'

class ResumeTemplateView(TemplateView):
    template_name = 'resume.html'