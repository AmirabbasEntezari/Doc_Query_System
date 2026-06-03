from rest_framework import serializers
from .models import Document, ChatSession
from .services import LLMService

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'content', 'created_at', 'updated_at']
        read_only_fields = ['content', 'created_at', 'updated_at']


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, help_text="پرسش خود را وارد کنید [cite: 4, 21]")
    
    # فیلدهای خروجی (فقط برای نمایش در پاسخ API)
    answer = serializers.CharField(read_only=True)


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'document', 'question', 'answer', 'created_at']