import os
import docx2txt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LLMService:

    @staticmethod
    def extract_text_from_docx(file_path):
        """
        استخراج متن کامل از فایل‌های docx
        """
        try:
            text = docx2txt.process(file_path)
            return text.strip()
        except Exception as e:
            raise Exception(f"خطا در خواندن فایل word: {str(e)}")

    @staticmethod
    def _retrieve_relevant_chunks(document_content, question, k=3):
        """
        بازیابی پیشرفته: تکه‌تکه کردن متن سند و پیدا کردن مرتبط‌ترین بخش‌ها با پرسش کاربر
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len
        )
        chunks = text_splitter.split_text(document_content)
        
        question_words = set(question.lower().split())
        scored_chunks = []
        
        for chunk in chunks:
            score = sum(1 for word in question_words if word in chunk.lower())
            scored_chunks.append((score, chunk))
            
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [chunk for score, chunk in scored_chunks[:k]]
        
        return "\n---\n".join(top_chunks)

    @classmethod
    def ask_llm_about_document(cls, document_content, question):
        """
        پرسش از هوش مصنوعی درباره یک سند خاص (با استفاده از RAG و بازیابی تکه‌ها)
        """
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise Exception("کلید API هوش مصنوعی (.env) تنظیم نشده است.")

        # بهینه‌سازی متن سند با استفاده از سیستم تکه‌تکه‌سازی برای ارسال نکردن کل متن سنگین
        context = cls._retrieve_relevant_chunks(document_content, question)

        llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model="openrouter/free",
            temperature=0.7
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", "شما یک دستیار هوش مصنوعی هوشمند هستید. با توجه به متن سند زیر، به سوال کاربر به زبان فارسی پاسخ دقیق بدهید:\n\n{context}"),
            ("human", "{question}")
        ])

        chain = prompt | llm
        response = chain.invoke({"context": context, "question": question})
        return response.content.strip()

    @classmethod
    def ask_llm_about_all_documents(cls, question):
        """
        🎯 نسخه اصلاح‌شده و هوشمند:
        جست‌جو در تمام اسناد با قابلیت RAG و استخراج خودکار شناسه (ID) سند منبع
        """
        from .models import Document
        
        # دریافت تمام اسنادی که محتوا دارند
        all_docs = Document.objects.exclude(content__isnull=True).exclude(content="")
        if not all_docs.exists():
            return "هنوز هیچ سندی با محتوای متنی در سیستم آپلود نشده است.", None

        # ترکیب متون اسناد به همراه تزریق ID و عنوان جهت ردیابی توسط هوش مصنوعی
        combined_context = ""
        for doc in all_docs:
            # برای اینکه توکن اضافه مصرف نشود، ابتدا مرتبط‌ترین بخش‌های هر سند را برمی‌داریم
            relevant_chunks = cls._retrieve_relevant_chunks(doc.content, question, k=2)
            if relevant_chunks.strip():
                combined_context += f"[ID: {doc.pk} | TITLE: {doc.title}]\n{relevant_chunks}\n\n"

        if not combined_context.strip():
            return "متنی متناسب با سوال شما در اسناد یافت نشد.", None

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise Exception("کلید API هوش مصنوعی (.env) تنظیم نشده است.")

        llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model="openrouter/free",
            temperature=0.7
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "شما یک دستیار هوش مصنوعی هوشمند هستید. با توجه به متن اسناد زیر، به سوال کاربر به زبان فارسی پاسخ دقیق بدهید.\n"
                "بسیار مهم: حتماً بررسی کنید پاسخ را دقیقاً از کدام سند پیدا کرده‌اید. در آخرین خط پاسخ خود، دقیقاً فرمت زیر را بنویسید (بجای X شناسه عددی یا همان ID سند را قرار دهید):\n"
                "SOURCE_DOC_ID: X\n"
                "اگر پاسخ در هیچ سندی نبود یا به طور مشترک در همه بود، بنویسید SOURCE_DOC_ID: NONE\n\n"
                f"محتوای بازیابی شده اسناد:\n{combined_context}"
            )),
            ("human", "{question}")
        ])

        chain = prompt | llm
        response = chain.invoke({"question": question})
        raw_output = response.content.strip()

        # استخراج هوشمندانه ID سند از خروجی هوش مصنوعی
        detected_doc_id = None
        clean_answer = raw_output

        if "SOURCE_DOC_ID:" in raw_output:
            try:
                parts = raw_output.split("SOURCE_DOC_ID:")
                clean_answer = parts[0].strip()  # جدا کردن بدنه اصلی پاسخ از کد ردیابی
                id_str = parts[1].strip().split()[0]
                if id_str != "NONE":
                    detected_doc_id = int(id_str)
            except Exception:
                pass

        return clean_answer, detected_doc_id

    @classmethod
    def generate_tags_for_chat(cls, question, answer):
        """
        تولید خودکار تگ‌های کلیدی بر اساس متن سوال و جواب
        """
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            return ""

        llm = ChatOpenAI(
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model="openrouter/free",
            temperature=0.1
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an AI that categorizes chat conversations. "
                "Based on the user's question and AI's answer, generate 1 to 3 relevant, very short keyword tags in Persian. "
                "Separate the tags with a comma (,). Do NOT write any introduction or extra words. Only output the tags.\n"
                "Example output: #مالی, #قرارداد, #حقوقی"
            )),
            ("human", f"Question: {question}\nAnswer: {answer}")
        ])

        chain = prompt | llm

        try:
            response = chain.invoke({})
            return response.content.strip()
        except Exception:
            return ""