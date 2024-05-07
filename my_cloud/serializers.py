from django.contrib.auth.models import User
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import Serializer, ModelSerializer, CharField
from rest_framework.authtoken.models import Token

from .models import File, UserSettings


class FileSerializer(ModelSerializer):
    class Meta:
        model = File
        exclude = []


class UserSerializer(ModelSerializer):
    total_files = SerializerMethodField()
    total_size = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'password', 'total_files', 'total_size']
        extra_kwargs = {"password": {"write_only": True}}

    def get_total_files(self, obj):
        return File.objects.filter(user=obj).count()

    def get_total_size(self, obj):
        from django.db.models import Sum
        value = File.objects.filter(user=obj).aggregate(total_size=Sum('size'))['total_size']
        if value is None:
            return 0
        return int(value)

    def create(self, obj):
        user = User(username=obj['username'])
        user.first_name = obj['first_name']
        user.last_name = obj['last_name']
        user.email = obj['email']
        user.set_password(obj['password'])
        user.save()
        return user


class IssueTokenRequestSerializer(Serializer):
    model = User
    username = CharField(required=True)
    password = CharField(required=True)


class TokenSerializer(ModelSerializer):
    class Meta:
        model = Token
        fields = ['key']


class UserSettingsSerializer(ModelSerializer):
    class Meta:
        model = UserSettings
        # fields = ['user', 'color_theme']
        exclude = []

