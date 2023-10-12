from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Todo


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        exclude = ['user']
    
    def create(self, validated_data):
        user = self.context['request'].user['user_id']
        user = User.objects.get(id=user)
        return Todo.objects.create(**validated_data, user=user)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        
        instance.save()
        return instance