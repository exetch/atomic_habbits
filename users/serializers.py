from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'avatar', 'phone_number', 'country']

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Обновление пароля, если он предоставлен
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super(UserSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        """
           Если пользователь, делающий запрос, не является владельцем объекта, из результата удаляются чувствительные поля.
           В данном случае, удаляются поля: 'password', 'last_name'.
           Если пользователь является владельцем объекта, объект возвращается без изменений.
           """
        ret = super().to_representation(instance)
        ret.pop('password', None)
        return ret
