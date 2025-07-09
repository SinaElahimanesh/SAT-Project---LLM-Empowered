from rest_framework import serializers
from .models import User, Message, Stage, UserGroup  # Import UserGroup

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'stage', 'group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            stage=validated_data.get('stage', Stage.BEGINNING),
            group=validated_data.get('group', UserGroup.CONTROL)  # Use UserGroup.CONTROL
        )
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
