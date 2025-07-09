from rest_framework import serializers
from .models import User, Message, Stage, UserGroup

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'stage', 'group')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use the group from validated_data if present, otherwise default
        group = validated_data['group'] if 'group' in validated_data else UserGroup.CONTROL
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            stage=validated_data.get('stage', Stage.BEGINNING),
            group=group
        )
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
