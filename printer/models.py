from django.db import models
from django.contrib.auth.models import User

class ThreeDPrinterUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    build_volume = models.CharField(max_length=50, help_text="Specify the build volume in mm (e.g., 200x200x200)")
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    com_port = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='Ожидает')

    def __str__(self):
        return f"{self.brand} {self.model}"

class ThreeDPrinter(models.Model):
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    build_volume = models.CharField(max_length=50, help_text="Specify the build volume in mm (e.g., 200x200x200)")
    description = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default='Ожидает')

    def __str__(self):
        return f"{self.brand} {self.model}"

class Command(models.Model):
    command_text = models.CharField(max_length=255)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    rating = models.IntegerField(default=0)

class ThermalData(models.Model):
    name = models.CharField(max_length=255)
    temperature = models.FloatField()

    def __str__(self):
        return f"{self.name}: {self.temperature}°C"

class Job(models.Model):
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class GCodeFile(models.Model):
    file = models.FileField(upload_to='gcode_files/')

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    printer = models.ForeignKey(ThreeDPrinterUser, on_delete=models.CASCADE, null=True, blank=True)
    model_file = models.FileField(upload_to='model_files/')
    upload_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    customer = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.upload_date}"


class Dialog(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User)  # Adjust this field based on your actual model

    def __str__(self):
        return self.name

class PrivateMessage(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, default=1)  # Убедитесь, что объект с ID=1 существует
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message