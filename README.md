# 🛡️ FastAPI Authentication System

نظام مصادقة (Authentication) متكامل مبني باستخدام FastAPI، مصمم وفقًا لأفضل الممارسات العالمية، ومجهز كنقطة انطلاق لأي مشروع ويب حديث يتطلب إدارة حسابات المستخدمين.

---

## 📌 الميزات الرئيسية

- ✅ تسجيل مستخدم جديد
- ✅ تسجيل الدخول باستخدام JWT
- ✅ تسجيل الخروج (مع تعطيل التوكن في Redis)
- ✅ جلب بيانات المستخدم الحالي
- ✅ تحديث بيانات الحساب
- ✅ تعطيل الحساب (بدل الحذف)
- ✅ حماية كافة المسارات باستخدام Depends وJWT
- ✅ رفض الوصول للحسابات غير المفعلة
- ✅ فصل كامل بين المهام (Endpoints، خدمات، استثناءات، الخ)

---

## 🔐 ما لا يتضمنه النظام

- ❌ التحقق بخطوتين (2FA): غير مدمج نظرًا لعدم الحاجة له في الاستخدام الحالي
- ❌ حذف الحساب نهائيًا: تم اعتماد "تعطيل الحساب" بدلًا من الحذف
- ❌ إعادة إرسال رسالة التحقق بالبريد: لم يتم اعتمادها لعدم الضرورة
- ❌ لا يحتوي هذا المشروع على ملفات `schemas`, `models`, `database`: تركت فارغة ليستغلها كل مطور حسب بنيته الخاصة

---

## ⚙️ المتطلبات

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- Redis
- PyJWT

---

## 🧩 هيكل المجلدات

```bash
project/
├── apis/
│   └── v1/
│       └── auth_system.py     # جميع المسارات الخاصة بالمصادقة
├── main.py                    # نقطة انطلاق التطبيق
└── README.md                  # هذا الملف




🧠 أمور تقنية مهمة

جميع المسارات محمية بـ Depends(get_current_user) الذي يتحقق من صلاحية التوكن وفعالية الحساب.

إذا تم تعطيل حساب المستخدم، فلا يمكنه تسجيل الدخول ولا تنفيذ أي عملية.

تم استعمال Redis كوسيط لتعطيل التوكنات (Blacklisting).

تم اعتماد JWT لتوثيق المستخدمين بدون جلسات.




🎯 الاستخدام

هذا المشروع مناسب لك إذا:

كنت تريد نظام مصادقة سريع وآمن وقابل للتعديل.

تبحث عن نقطة انطلاق جاهزة لمشروعك.

لا تحتاج في البداية للتحقق بخطوتين أو تعقيدات إضافية.




📄 الرخصة

MIT License – مفتوح المصدر، يمكنك استخدامه بحرية في مشاريعك الشخصية أو التجارية.





✉️ تواصل

لأي استفسار أو اقتراح، يرجى فتح Issue على GitHub أو التواصل عبر LinkedIn.
https://www.linkedin.com/in/mohammed-bachir-henka-it/



# auth-system-project


# دليل سريع لإنشاء مشروع FastAPI باستخدام Poetry

## 1. التحقق من التثبيت
# تأكد من وجود Python و Poerty مثبتين:
```bash
python --version    # يجب أن تكون ≥ 3.7
poetry --version
```

# إذا لم يكن Poetry مثبتًا:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## 2. إنشاء مجلد للمشروع
```bash
mkdir my_fastapi_project
cd my_fastapi_project
```

## 3. تهيئة المشروع مع Poetry
```bash
poetry init -n
```

## 4. تثبيت المكتبات الأساسية
```bash
# إذا كان موجود ملفي  poetry.lock و pyproject.toml نستخدم هذا الأمر لتثبيت الحزم اللازمة للمشروع:
poetry install

#إذا لم يكن هناك أي من  poetry.lock أو pyproject.toml نثبت الحزم الأساسية بتنفيذ:
poetry add fastapi uvicorn
#   💡" uvicorn: هو خادم ASGI لتشغيل تطبيقات FastAPI"
#   🔁" --reload: لتحديث الخادم تلقائيًا عند تعديل الكود (مناسب للتطوير فقط)"
```

## 5. إنشاء ملف التطبيق (مثلاً: main.py) 
# يمكنك إنشاء الملف يدويًا أو تنفيذ الأمر التالي لإنشائه تلقائيًا:
```bash
cat > main.py << EOL
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
EOL
```

##  6. تشغيل الخادم
```bash
# الطريقة الأولى (بدون تفعيل البيئة):
poetry run uvicorn main:app --reload


# الطريقة الثانية (بعد تفعيل البيئة):
eval $(poetry env activate) # استخدم deactivate لأيقاف تشغيل البيئة
uvicorn main:app --reload

#  ⚠️ " إذا ظهر لك خطأ مثل command not found عند تشغيل poetry env activate،
# فقد تحتاج إلى تحديث Poetry باستخدام الأمر التالي:"
poetry self update

# " افتح الرابط في المتصفح: http://127.0.0.1:8000"
```


## 7. (اختياري) إضافة أمر مختصر للتشغيل
```bash
# تعديل ملف pyproject.toml
# أضف السطر التالي داخل الملف:
[tool.poetry.scripts]
start = "uvicorn main:app --reload"

# ثم شغل المشروع ببساطة:
poetry run start
```

### ✅ وهكذا تكون لديك بيئة Poetry لمشروع FastAPI الذي سنعمل عليه!







