from django.urls import path
from . import views
from .views import register, admin_select_printer, admin_add_3d_printer, admin_print_gcode

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout'),
    path('home/', views.home, name='home'),
    path('register/', register, name='register'),
    path('select_printer/', admin_select_printer, name='admin_select_printer'),
    path('add_3d_printer/', admin_add_3d_printer, name='admin_add_3d_printer'),
    path('print_gcode/', admin_print_gcode, name='admin_print_gcode'),
]