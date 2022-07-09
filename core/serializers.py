from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import User
# when I remove the "." from import I receive this error: RuntimeError: Model class models.User doesn't declare an
# explicit app_label and isn't in an application in INSTALLED_APPS.


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email']


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        Model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
