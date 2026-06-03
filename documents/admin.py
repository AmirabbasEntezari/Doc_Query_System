from django import forms
from django.contrib import admin
from django.contrib import messages
from .models import Document, ChatSession, Tag
from .services import LLMService

class ChatSessionForm(forms.ModelForm):
    class Meta:
        model = ChatSession
        fields = '__all__'
        widgets = {
            'question': forms.Textarea(attrs={
                'rows': 3, 
                'style': 'width: 100%; max-width: 700px; border-radius: 6px; padding: 10px;',
                'placeholder': 'سوال خود را اینجا بنویسید...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_document'].empty_label = "🔍 جست‌جو و استخراج از تمام اسناد آپلود شده"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('content', 'created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    form = ChatSessionForm
    
    list_display = ('question_preview', 'answer_preview', 'get_scope', 'tags_display', 'created_at')
    
    # 🌟 این بخش اصلاح شد: تفکیک فیلتر محدوده جست‌جو از برچسب‌های هوشمند
    list_filter = ('target_document', 'tags__name', 'created_at')
    
    search_fields = ('question', 'answer', 'tags__name')
    readonly_fields = ('answer', 'tags', 'created_at')
    
    fieldsets = (
        ("تنظیمات پرسش هوش مصنوعی", {
            'fields': ('target_document', 'question'),
        }),
        ("💡 خروجی و پاسخ نهایی", {
            'fields': ('answer', 'tags'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if change and 'question' not in form.changed_data:
            super().save_model(request, obj, form, change)
            return

        if not obj.question:
            return

        # خواندن مقدار اولیه فرم
        if 'target_document' in form.cleaned_data:
            obj.target_document = form.cleaned_data['target_document']

        try:
            detected_doc_id = None

            # ۱. دریافت پاسخ از هوش مصنوعی
            if obj.target_document:
                if not obj.target_document.content:
                    messages.error(request, f"سند '{obj.target_document.title}' متنی ندارد.")
                    return
                ai_answer = LLMService.ask_llm_about_document(obj.target_document.content, obj.question)
            else:
                # اگر روی کل اسناد بود، متد جدید پاسخ و شناسه سند کشف‌شده را برمی‌گرداند
                ai_answer, detected_doc_id = LLMService.ask_llm_about_all_documents(obj.question)

            obj.answer = ai_answer

            # 🚀 اگر در حالت «کل اسناد» بودیم و هوش مصنوعی سند را تشخیص داد، آن را به مدل وصل کن
            if not obj.target_document and detected_doc_id:
                try:
                    from .models import Document
                    obj.target_document = Document.objects.get(pk=detected_doc_id)
                except Document.DoesNotExist:
                    pass

            # ۲. تولید تگ‌های موضوعی در حافظه (بدون تگ اسم فایل)
            tag_objects = []
            if ai_answer:
                raw_tags = LLMService.generate_tags_for_chat(obj.question, ai_answer)
                if raw_tags:
                    tag_list = [t.strip() for t in raw_tags.split(',') if t.strip()]
                    
                    # ذخیره تگ‌های صرفاً موضوعی
                    for tag_name in tag_list:
                        # حذف تگ‌هایی که علامت 📄 دارند (برای پاکسازی تگ‌های قدیمی احتمالی)
                        if "📄" in tag_name:
                            continue
                        tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                        tag_objects.append(tag_obj)

            # ۳. ذخیره نهایی و یک‌باره چت در دیتابیس
            super().save_model(request, obj, form, change)

            # ۴. متصل کردن برچسب‌ها
            if tag_objects:
                obj.tags.set(tag_objects)

            messages.success(request, "پاسخ هوش مصنوعی با موفقیت تولید و سند مربوطه شناسایی شد.")
            
        except Exception as e:
            messages.error(request, f"خطا در پردازش: {e}")
            
    def question_preview(self, obj):
        return obj.question[:40] + "..." if len(obj.question) > 40 else obj.question
    question_preview.short_description = "متن سوال"

    def answer_preview(self, obj):
        if obj.answer:
            return obj.answer[:50] + "..." if len(obj.answer) > 50 else obj.answer
        return "در حال پردازش..."
    answer_preview.short_description = "خلاصه پاسخ"

    def get_scope(self, obj):
        return obj.target_document.title if obj.target_document else "🎯 تمام اسناد"
    get_scope.short_description = "محدوده چت"

    def tags_display(self, obj):
        tags = obj.tags.all()
        if tags:
            from django.utils.safestring import mark_safe
            tag_html = "".join([f'<span style="background: #e0f2f1; color: #00695c; padding: 3px 8px; margin: 0 3px; border-radius: 4px; font-size: 11px; font-weight: bold;">{tag.name}</span>' for tag in tags])
            return mark_safe(tag_html)
        return "-"
    tags_display.short_description = "🏷️ برچسب‌ها"