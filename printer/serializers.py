from rest_framework import serializers
from .models import ThreeDPrinter
from .models import Command

class ThreeDPrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreeDPrinter
        fields = '__all__'


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['command_text']

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField(required=True, max_length=255)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value