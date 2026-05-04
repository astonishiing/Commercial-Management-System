from rest_framework import serializers
from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_cpf(self, value):
        cpf = value.replace('.', '').replace('-', '')
        if not cpf.isdigit() or len(cpf) != 11:
            raise serializers.ValidationError("CPF inválido. Use 000.000.000-00.")
        return value
