from rest_framework import serializers

from .models import Location,TVStation,Program

class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'