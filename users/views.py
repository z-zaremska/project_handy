from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

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

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect('project_home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
