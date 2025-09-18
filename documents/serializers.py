from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Document, Conversation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ('id', 'document', 'user', 'question', 'answer', 'created_at')
        read_only_fields = ('user', 'created_at')

class DocumentSerializer(serializers.ModelSerializer):
    conversations = ConversationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ('id', 'title', 'description', 'file', 'file_type', 'size', 'uploaded_at', 'user', 'conversations')
        read_only_fields = ('user', 'size', 'file_type') 