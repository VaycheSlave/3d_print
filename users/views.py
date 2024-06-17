from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import user_passes_test
from .forms import LoginUserForm, RegisterUserForm

def home(request):
    return render(request, 'web.html')

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

    def get_success_url(self):
        return reverse('printer:web')  # Возврат на главную страницу

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect('printer:web')  # Возврат на главную страницу

    return render(request, 'users/login.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('printer:web') + '?next=/api/web/')

def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterUserForm()
    return render(request, 'users/register.html', {'form': form})

def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_person(user):
    return user.groups.filter(name='Person').exists()

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name='admin').exists():
            # User is in the 'admin' group
            print("User is in the 'admin' group")
            return view_func(request, *args, **kwargs)
        else:
            print("User is NOT in the 'admin' group")
            return HttpResponse("Permission Denied")

    return _wrapped_view

def person_required(view_func):
    return user_passes_test(is_person, login_url=None)(view_func)

@person_required
def add_3d_printer(request):
    return render(request, 'printer/add_3d_printer.html')

@person_required
def print_gcode(request):
    return render(request, 'printer/print_gcode.html')

@admin_required
def admin_select_printer(request):
    return render(request, 'printer/select_printer.html')

@admin_required
def admin_add_3d_printer(request):
    return render(request, 'printer/add_3d_printer.html')

@admin_required
def admin_print_gcode(request):
    return render(request, 'printer/print_gcode.html')
