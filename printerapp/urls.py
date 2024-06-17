from django.contrib import admin
from django.urls import path, include
from printer import views
from printer.urls import urlpatterns as api_urls

urlpatterns = [
    path("", views.web, name='web'),
    path('api/', include(api_urls)),
    path('admin/', admin.site.urls),
    path("", include("printer.urls")),
    path('users/', include('users.urls', namespace="users")),
    # path('select_printer/', views.select_printer, name='select-printer'),
    # path('send_command/<int:printer_id>/', views.send_command, name='send-command'),
    # path('printer_info/<int:printer_id>/', views.printer_info, name='printer-info'),

    path("control_printer/", views.control_printer, name='control_printer'),
    # path("add_3d_printer/", views.add_3d_printer, name='add_3d_printer'),
    # path("success_printer/", views.success_printer, name='success_printer'),
    path('web/', views.home, name='home'),




]
