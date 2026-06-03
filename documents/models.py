from django.db import models
from .services import LLMService

class Document(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان سند")
    file = models.FileField(upload_to='documents/', verbose_name="فایل سند (docx)")
    content = models.TextField(blank=True, null=True, verbose_name="متن استخراج شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "سند"
        verbose_name_plural = "📚 مدیریت و آپلود اسناد"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if self.file and (is_new or not self.content):
            try:
                with self.file.open('rb') as f:
                    extracted_text = LLMService.extract_text_from_docx(f)
                Document.objects.filter(pk=self.pk).update(content=extracted_text)
                self.content = extracted_text
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"خطا در استخراج متن از سند {self.title}: {e}")


# 🌟 مدل جدید برای ذخیره تگ‌ها به صورت کاملاً مستقل و تکی
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام برچسب")

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "🏷️ مدیریت برچسب‌ها"

    def __str__(self):
        return self.name


class ChatSession(models.Model):
    question = models.TextField(verbose_name="متن پرسش شما")
    target_document = models.ForeignKey(
        Document, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="محدوده جست‌جو",
        help_text="اگر سندی را انتخاب نکنید، جست‌جو به صورت خودکار میان تمام اسناد انجام می‌شود."
    )
    answer = models.TextField(blank=True, null=True, verbose_name="پاسخ هوش مصنوعی")
    
    # 🌟 تبدیل فیلد تگ به رابطه چند-به-چند تا هر تگ تکی و مستقل ذخیره بشه
    tags = models.ManyToManyField(Tag, blank=True, related_name="sessions", verbose_name="برچسب‌های هوشمند")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان پرسش")

    class Meta:
        verbose_name = "پرسش و پاسخ"
        verbose_name_plural = "💬 پرسش از اسناد و تاریخچه گفتگوها"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرسش: {self.question[:30]}..."