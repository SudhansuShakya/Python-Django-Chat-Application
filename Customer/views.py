from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView

def login_view(request):
    if request.method == 'POST':
        try:
            userobj = User.objects.get(username=request.POST['username'])
            if userobj.is_active == False:
                messages.error(request, "Your Account is blocked . Please contact to administrator")
                return redirect('login')
            user = authenticate(
                username=request.POST['username'],
                password=request.POST['password'],
            )
            login(request, user)
            message = f'Hello {user.username}! You have been logged in'
            return redirect('home')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')
    return render(request, 'auth/login.html')


def register(request):
    if request.method == 'POST':
        username=request.POST['username']
        if User.objects.filter(username=username).exists():
            messages.error(request,"Username  "+username+" already exists !")
            return redirect('register')
        password1=request.POST['password1']
        password2=request.POST['password2']
        if password1 != password2:
            messages.success(request,"Password & Re-Type Password did't match, Try again.")
            return redirect('register')
        else:
            first_name=request.POST['first_name']
            last_name=request.POST['last_name']
            email=request.POST['email']
            userObj = User.objects.create(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                is_active=True
            )
            userObj.set_password(password1)
            userObj.save()
            
            user = authenticate(
                username=username,
                password=password1,
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    return render(request, 'auth/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to login page or any other page after logout

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = User.objects.all()
        return context
