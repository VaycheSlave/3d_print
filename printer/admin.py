# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ThreeDPrinter, ThermalData, Job, Dialog, PrivateMessage

STATUS_COLORS = {
    'Готов': 'green',
    'Выключен': 'red',
    'Неполадки': 'red',
    'Стoит': 'red',
    'Печает': 'orange',
    'Ожидает': 'yellow',
}

@admin.register(ThreeDPrinter)
class ThreeDPrinterAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'status_colored')

    def status_colored(self, obj):
        color = STATUS_COLORS.get(obj.status, 'red')
        return format_html('<span style="color: {color};"><span style="display: inline-block; width: 10px; height: 10px; background-color: {color}; border-radius: 50%; margin-right: 5px;"></span>{status}</span>', color=color, status=obj.status)

    status_colored.allow_tags = True
    status_colored.short_description = 'Status'

@admin.register(ThermalData)
class ThermalDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'temperature')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')

admin.site.register(Dialog)
admin.site.register(PrivateMessage)
