from django import forms
from .models import ThreeDPrinter, GCodeFile, Order, ThreeDPrinterUser, PrivateMessage
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class ThreeDPrinterForm(forms.ModelForm):
    class Meta:
        model = ThreeDPrinter
        fields = ['brand', 'model', 'build_volume', 'description']

    widgets = {
        'description': forms.Textarea(attrs={'rows': 4}),
    }

    labels = {
        'build_volume': 'Build Volume (mm)',

    }

    help_texts = {
        'build_volume': 'Specify the build volume in mm (e.g., 200x200x200)',

    }

class ThreeDPrinterFormUser(forms.ModelForm):
    class Meta:
        model = ThreeDPrinterUser
        fields = ['brand', 'model', 'build_volume', 'description', 'city']

        labels = {
            'build_volume': 'Build Volume (mm)',
            'city': 'City',  # Добавляем метку для поля city
        }

        help_texts = {
            'build_volume': 'Specify the build volume in mm (e.g., 200x200x200)',
            'city': 'Enter your city',  # Добавляем подсказку для поля city
        }

    widgets = {
        'description': forms.Textarea(attrs={'rows': 4}),
    }

class PrinterSelectForm(forms.Form):
    printers = ThreeDPrinter.objects.all()
    printer_choices = [(printer.id, str(printer)) for printer in printers]

    printer_id = forms.ChoiceField(choices=printer_choices, label='Выбрать принтер')

class SelectPrinterView(FormView):
    template_name = 'select_printer.html'
    form_class = PrinterSelectForm
    success_url = '/printer-info/'

    def form_valid(self, form):
        selected_printer_id = form.cleaned_data['printer_id']
        selected_printer = ThreeDPrinter.objects.get(id=selected_printer_id)

        return redirect('printer-info', printer_id=selected_printer.id)


class GCodeForm(forms.ModelForm):
    class Meta:
        model = GCodeFile
        fields = ['file']



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['price', 'status']


class ModelUploadForm(forms.Form):
    model_file = forms.FileField()

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}))
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ваш email'}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Ваше сообщение'}),
        required=True)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class CustomPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput)


class PrivateMessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['message']