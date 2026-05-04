from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'perfil']


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Usuario
        fields = ['username', 'password', 'perfil']

    def create(self, validated_data):
        return Usuario.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            perfil=validated_data.get('perfil', 'FUNCIONARIO'),
        )
