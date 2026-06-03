from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Document, ChatSession
from .serializers import DocumentSerializer, AskQuestionSerializer, ChatHistorySerializer
from .services import LLMService

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API کامل برای:
    1. افزودن، ویرایش، حذف و مشاهده اسناد [cite: 4, 15, 19]
    2. پرسش از یک سند خاص و دریافت پاسخ هوشمند [cite: 4, 21, 24]
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    @action(detail=True, methods=['post'], url_path='ask')
    def ask_question(self, request, pk=None):
        """
        نقطه اتصال (Endpoint) برای پرسش از یک سند خاص [cite: 4, 21]
        آدرس: /api/documents/{id}/ask/
        """
        document = self.get_object()
        serializer = AskQuestionSerializer(data=request.data)
        
        if serializer.is_valid():
            question = serializer.validated_data['question']
            
            # بررسی اینکه آیا سند اصلا متنی دارد یا خیر [cite: 20]
            if not document.content:
                return Response(
                    {"error": "این سند فاقد متن است یا پردازش آن با خطا مواجه شده است."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # صدا زدن سرویس هوش مصنوعی و لانگ‌چین برای پاسخگویی [cite: 11, 24]
            answer = LLMService.ask_llm_about_document(document.content, question)
            
            # ذخیره تاریخچه پرسش و پاسخ در دیتابیس 
            ChatHistory.objects.create(
                document=document,
                question=question,
                answer=answer
            )
            
            return Response({
                "question": question,
                "answer": answer
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API برای مشاهده تاریخچه پرسش‌ها و پاسخ‌ها 
    آرسی: /api/history/
    """
    queryset = ChatSession.objects.all()
    serializer_class = ChatHistorySerializer