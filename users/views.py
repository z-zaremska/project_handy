from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    """New users registration"""

    if request.method != 'POST':
        registration_form = UserCreationForm()
        return render(request, 'registration/register.html', {'registration_form': registration_form})
    
    else:
        registration_form = UserCreationForm(data=request.POST)
        if registration_form.is_valid():
            new_user = registration_form.save()
            login(request, new_user)
            return redirect('project_home')
