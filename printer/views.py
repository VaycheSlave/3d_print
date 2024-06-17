import serial
import logging
import requests

from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ThreeDPrinterSerializer, CommandSerializer, MessageSerializer
from .forms import (
    ThreeDPrinterForm, PrinterSelectForm, GCodeForm, ThreeDPrinterFormUser, ModelUploadForm, ContactForm,
    UserProfileForm, CustomPasswordChangeForm, PrivateMessageForm
)
from .models import (
    ThreeDPrinter, Job, Command, ThermalData, GCodeFile, Order, ThreeDPrinterUser, UserProfile,
    Dialog, PrivateMessage
)
from users.views import person_required, admin_required



logger = logging.getLogger(__name__)

@login_required
def admin_select_printer(request):
    if request.user.is_staff:
        return render(request, 'printerapp/select_printer.html')
    else:
        return redirect('add_printer')

def printers_view(request):
    printer_users = ThreeDPrinterUser.objects.all()
    return render(request, 'kab_print.html', {'printer_users': printer_users})

@login_required
def admin_add_3d_printer(request):
    if request.user.is_staff:
        return render(request, 'printerapp/add_3d_printer.html')
    else:
        return redirect('print_gcode')

@login_required
def admin_print_gcode(request):
    if request.user.is_staff:
        return render(request, 'printerapp/print_gcode.html')
    else:
        return redirect('print_gcode')

@login_required
def add_printer(request):
    if not request.user.is_staff:
        return render(request, 'add_printer.html')
    else:
        return redirect('select_printer')

@login_required
def print_gcode(request):
    if not request.user.is_staff:
        if request.method == 'POST':
            form = GCodeForm(request.POST, request.FILES)
            if form.is_valid():
                gcode_file = form.save()
                order = Order.objects.create(user=request.user, model_file=gcode_file.file)
                try:
                    com_port = "COM5"
                    baud_rate = 115200
                    with serial.Serial(port=com_port, baudrate=baud_rate, timeout=1) as ser, open(gcode_file.file.path, 'rb') as file:
                        data = file.read()
                        ser.write(data)
                    return redirect('success_print')
                except Exception as e:
                    logger.error(f"Error sending G-code to printer: {e}")
                    return render(request, 'print_gcode.html', {'form': form, 'error': str(e)})
        else:
            form = GCodeForm()
        return render(request, 'print_gcode.html', {'form': form})
    else:
        return redirect('admin_print_gcode')

@admin_required
def orders_view(request):
    orders = Order.objects.all()
    filters = {k: v for k, v in request.GET.items() if v}

    if 'order_id' in filters:
        orders = orders.filter(id=filters['order_id'])
    if 'upload_date' in filters:
        orders = orders.filter(upload_date=filters['upload_date'])
    if 'username' in filters:
        orders = orders.filter(user__username=filters['username'])
    if 'status' in filters:
        orders = orders.filter(status=filters['status'])

    context = {'orders': orders}
    return render(request, 'orders.html', context)

def update_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.price = request.POST.get('price')
        order.status = request.POST.get('status')
        order.save()
        return redirect(reverse('orders'))

def web(request):
    return render(request, "web.html")

@admin_required
def control_printer(request):
    if request.method == 'POST':
        command = request.POST.get('command')
        if command:
            try:
                with serial.Serial('COM5', 115200) as ser:
                    commands = {
                        "G28": "G28\n",
                        "Сдвиг каретки на 10мм влево по X": "G91\nG1 X-10 F3000\n",
                        "Сдвиг каретки на 10мм вправо по X": "G91\nG1 X10 F3000\n",
                        "Остановить выполнение текущей задачи": "M84\n",
                        "Сдвиг стола на 10мм влево по Y": "G91\nG1 Y-10 F3000\n",
                        "Сдвиг стола на 10мм вправо по Y": "G91\nG1 Y10 F3000\n",
                        "Сдвиг подъема оси на 10мм влево по Z": "G91\nG1 Z-10 F3000\n",
                        "Сдвиг подъема оси на 10мм вправо по Z": "G91\nG1 Z10 F3000\n"
                    }
                    if command in commands:
                        ser.write(commands[command].encode())
                    return HttpResponse(f"Команда '{command}' успешно отправлена на принтер.")
            except serial.SerialException as e:
                logger.error(f"Error controlling printer: {e}")
                return HttpResponse(f"Ошибка: {e}")
    return render(request, 'control_printer.html')

@login_required
def add_3d_printer(request):
    if request.method == 'POST':
        form = ThreeDPrinterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_printer')
    else:
        form = ThreeDPrinterForm()
    return render(request, 'add_printer.html', {'form': form})

@login_required
def success_printer(request):
    return render(request, 'success_printer.html')

@login_required
def success_print(request):
    return render(request, 'success_print.html')

@login_required
def kab_print(request):
    return render(request, 'kab_print.html')

class ThreeDPrinterListCreateView(generics.ListCreateAPIView):
    queryset = ThreeDPrinter.objects.all()
    serializer_class = ThreeDPrinterSerializer

class ControlPrinterAPIView(APIView):
    def post(self, request, *args, **kwargs):
        command_text = request.data.get('command')
        if command_text:
            try:
                with serial.Serial('COM5', 115200) as ser:
                    commands = {
                        "G28": "G28\n",
                        "Сдвиг каретки на 10мм влево по X": "G91\nG1 X-10 F3000\n",
                        "Сдвиг каретки на 10мм вправо по X": "G91\nG1 X10 F3000\n",
                        "Остановить выполнение текущей задачи": "M112\n",
                        "Сдвиг стола на 10мм влево по Y": "G91\nG1 Y-10 F3000\n",
                        "Сдвиг стола на 10мм вправо по Y": "G91\nG1 Y10 F3000\n",
                        "Сдвиг подъема оси на 10мм влево по Z": "G91\nG1 Z-10 F3000\n",
                        "Сдвиг подъема оси на 10мм вправо по Z": "G91\nG1 Z10 F3000\n"
                    }
                    if command_text in commands:
                        ser.write(commands[command_text].encode())
                    return Response({"message": f"Команда '{command_text}' успешно отправлена на принтер."}, status=status.HTTP_200_OK)
            except serial.SerialException as e:
                logger.error(f"Error controlling printer: {e}")
                return Response({"error": f"Ошибка: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"error": "Не указана команда"}, status=status.HTTP_400_BAD_REQUEST)

@admin_required
def select_printer(request):
    printers = ThreeDPrinterUser.objects.all()
    if request.method == 'POST':
        printer_id = request.POST.get('printer_id')
        printer = get_object_or_404(ThreeDPrinterUser, id=printer_id)
        printer.delete()
        return redirect('printers_list')
    return render(request, 'select_printer.html', {'printers': printers})

@admin_required
def send_command(request, printer_id):
    selected_printer = get_object_or_404(ThreeDPrinter, id=printer_id)
    if request.method == 'POST':
        command = request.POST.get('command')
        try:
            with serial.Serial(selected_printer.com_port, 115200, timeout=1) as ser:
                ser.write(command.encode())
                return HttpResponse(f"Command '{command}' sent to printer {selected_printer.name}.")
        except serial.SerialException as e:
            logger.error(f"Error sending command to printer: {e}")
            return HttpResponse(f"Error: {e}")
    return render(request, 'send_command.html', {'selected_printer': selected_printer})

@admin_required
def printer_info(request, printer_id):
    selected_printer = get_object_or_404(ThreeDPrinter, id=printer_id)
    return render(request, 'printer_info.html', {'selected_printer': selected_printer})

@admin_required
def delete_printer(request, printer_id):
    try:
        printer = get_object_or_404(ThreeDPrinter, pk=printer_id)
        printer.delete()
        return redirect('select_printer')
    except ThreeDPrinter.DoesNotExist:
        return render(request, 'select_printer.html', {'printer_id': printer_id})

def home(request):
    return render(request, 'web.html')

def print_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        success = True
        return JsonResponse({'success': success})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def update_order(request, order_id):
    if request.method == 'POST':
        price = request.POST.get('price')
        status = request.POST.get('status')
        order = get_object_or_404(Order, pk=order_id)
        order.price = price
        order.status = status
        order.save()
        return redirect('orders')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def add_3d_printerUser(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden('Только аутентифицированные пользователи могут добавлять принтеры.')
    if request.method == 'POST':
        form = ThreeDPrinterFormUser(request.POST)
        if form.is_valid():
            printer = form.save(commit=False)
            printer.user = request.user
            printer.save()
            messages.success(request, 'Принтер успешно добавлен.')
            return redirect('kab_print')
    else:
        form = ThreeDPrinterFormUser()
    return render(request, 'printerapp/add_3d_printer.html', {'form': form})

@login_required
def choose_printer(request, printer_id):
    printer = get_object_or_404(ThreeDPrinterUser, id=printer_id)
    return redirect('add_3d_model', printer_id=printer.id)

@login_required
def add_3d_model(request, printer_id):
    printer = get_object_or_404(ThreeDPrinterUser, id=printer_id)
    if request.method == 'POST':
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            model_file = form.cleaned_data['model_file']
            order = Order.objects.create(user=request.user, printer=printer, model_file=model_file, status='ожидает')
            return redirect('view_gcode', order_id=order.id)
    else:
        form = ModelUploadForm()
    return render(request, 'add_3d_model.html', {'form': form, 'printer': printer})

@login_required
def view_gcode(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'view_gcode.html', {'order': order})

@login_required
def send_to_printer(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    printer = order.printer
    flask_url = f"http://{printer.ip_address}:5000/print"
    files = {'model_file': order.model_file}
    data = {'order_id': order.id}
    response = requests.post(flask_url, files=files, data=data)
    if response.status_code == 200:
        order.status = 'в процессе'
    else:
        order.status = 'ошибка'
    order.save()
    return redirect('order_detail', order_id=order.id)



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_detail.html', {'order': order})
@csrf_exempt
@login_required
def submit_model(request):
    if request.method == 'POST':
        printer_id = request.POST.get('printer_id')
        com_port = request.POST.get('com_port')
        ip_address = request.POST.get('ip_address')
        model_file = request.FILES.get('model')

        saved_file = None
        try:
            saved_file = FileSystemStorage().save(f"model_files/{model_file.name}", model_file)
        except Exception as e:
            logger.error(f"Error saving model file: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        file_path = FileSystemStorage().path(saved_file)

        flask_url = f"http://{ip_address}:5000/api/print"
        response = requests.post(flask_url, json={
            'com_port': com_port,
            'file_path': file_path
        })

        if response.status_code == 200:
            try:
                printer_user = ThreeDPrinterUser.objects.get(id=printer_id) if printer_id else None
                order = Order.objects.create(
                    user=request.user,
                    printer=printer_user,
                    model_file=saved_file,
                    price=None,
                    customer=request.user.username,
                    status='Processing'
                )
                return JsonResponse({'status': 'success', 'message': 'Model sent to printer.'})
            except Exception as e:
                logger.error(f"Error creating order: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': response.json().get('message')}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)

def upload_file_view(request):
    if request.method == 'POST':
        com_port = request.POST.get('com_port')
        model_data = request.POST.get('model_data')
        ip_address = request.POST.get('ip_address')

        if com_port and model_data and ip_address:
            url = f'http://{ip_address}:5000/api/print'
            data = {
                'com_port': com_port,
                'model_data': model_data
            }
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    return JsonResponse({'status': 'success', 'message': 'Model sent to printer.'})
                else:
                    return JsonResponse({'status': 'error', 'message': response.json().get('message')})
            except requests.RequestException as e:
                logger.error(f"Error uploading model data: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'})
    return render(request, 'add_3d_model.html')

def printer_action(request):
    if request.method == 'POST':
        printer_id = request.POST.get('printer_id')
        command = request.POST.get('command')

        selected_printer = get_object_or_404(ThreeDPrinter, id=printer_id)
        com_port = selected_printer.com_port
        ip_address = selected_printer.ip_address

        url = f'http://{ip_address}:5000/api/print'
        data = {
            'com_port': com_port,
            'model_data': command
        }

        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return JsonResponse({'status': 'success', 'message': 'Команда успешно отправлена на принтер.'})
            else:
                return JsonResponse({'status': 'error', 'message': response.json().get('message')})
        except requests.RequestException as e:
            logger.error(f"Error sending command to printer: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def orders_user(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    return render(request, 'kab_print/orders_user.html', {'orders': orders})

def printers_user(request):
    user_printers = ThreeDPrinterUser.objects.filter(user=request.user)
    all_printers = ThreeDPrinterUser.objects.all()
    return render(request, 'kab_print/printers_user.html', {'user_printers': user_printers, 'all_printers': all_printers})

def management(request):
    return render(request, 'kab_print/management.html')

def printing(request):
    return render(request, 'kab_print/printing.html')

def telegram_auth(request):
    if request.method == 'GET':
        telegram_id = request.GET.get('telegram_id')
        if telegram_id:
            qr_code_url = request.build_absolute_uri(reverse('generate_qr_code') + f'?telegram_id={telegram_id}')
            return JsonResponse({'qr_code_url': qr_code_url})
        else:
            return HttpResponse("Неверный запрос")
    else:
        return HttpResponse("Метод запроса не поддерживается")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_mail(
                f'Контактная форма от {name}',
                message,
                email,
                ['recipient@example.com'],
                fail_silently=False,
            )
            return HttpResponseRedirect(reverse('contact_success'))
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)
        if profile_form.is_valid() and password_form.is_valid():
            profile_form.save()
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = CustomPasswordChangeForm(user)

    return render(request, 'kab_print/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'rating': user_profile.rating
    })
@login_required
def chat_view(request):
    dialogs = []

    for dialog in Dialog.objects.filter(participants=request.user):
        other_user = dialog.participants.exclude(id=request.user.id).first()
        dialogs.append((dialog, other_user.username))

    users = User.objects.exclude(id=request.user.id)

    return render(request, 'kab_print/chat.html', {
        'dialogs': dialogs,
        'users': users
    })

@login_required
def send_message(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)
    recipient = dialog.participants.exclude(id=request.user.id).first()
    if request.method == 'POST':
        form = PrivateMessageForm(request.POST)
        if form.is_valid():
            private_message = form.save(commit=False)
            private_message.sender = request.user
            private_message.recipient = recipient
            private_message.dialog = dialog
            private_message.save()
            return JsonResponse({
                'status': 'success',
                'message': private_message.message,
                'sender': private_message.sender.username,
                'timestamp': private_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def get_messages(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)
    messages = PrivateMessage.objects.filter(dialog=dialog).order_by('timestamp')
    data = {
        'messages': [{
            'sender': msg.sender.username,
            'message': msg.message,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': msg.is_read
        } for msg in messages]
    }
    return JsonResponse(data)

class SendMessageView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']

            return Response({"status": "message sent"}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

