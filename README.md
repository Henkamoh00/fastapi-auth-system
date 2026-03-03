# 🛡️ FastAPI Authentication System

A comprehensive authentication system built using FastAPI, designed according to global best practices, and equipped as a starter point for any modern web project requiring user account management.

📌 Key Features
✅ User registration  
✅ Login using JWT  
✅ Logout (with token invalidation in Redis)  
✅ Fetch current user data  
✅ Update account details  
✅ Disable account (instead of deletion)  
✅ Protect all routes using Depends and JWT  
✅ Deny access to inactive accounts  
✅ Complete separation of concerns (Endpoints, Services, Exceptions, etc.)

🔐 What the System Does Not Include
❌ Two-Factor Authentication (2FA): Not integrated due to current usage needs  
❌ Permanent account deletion: "Account disabling" is adopted instead of deletion  
❌ Resending verification email: Not included due to lack of necessity  
❌ This project does not include schemas, models, database: left blank for each developer to utilize according to their own structure

⚙️ Requirements
Python 3.10+  
FastAPI  
SQLAlchemy  
Alembic  
Redis  
PyJWT

🧩 Folder Structure
project/
├── apis/
│   └── v1/
│       └── auth_system.py     # All authentication-related routes
├── main.py                    # Application entry point
└── README.md                  # This file

🧠 Important Technical Aspects
All routes are protected with Depends(get_current_user) which verifies the token's validity and account status.  
If a user's account is disabled, they cannot log in or perform any operations.  
Redis is used as a medium for token invalidation (Blacklisting).  
JWT is employed for user authentication without sessions.

🎯 Usage
This project is suitable for you if:
- You want a fast, secure, and modifiable authentication system.  
- You're looking for a ready-made starting point for your project.  
- You do not need two-factor authentication or additional complexities initially.

📄 License
MIT License – Open-source, feel free to use it in your personal or commercial projects.  

✉️ Contact
For any inquiries or suggestions, please open an Issue on GitHub or reach out via LinkedIn.

---

Quick Guide to Creating a FastAPI Project Using Poetry

1. Verify Installation
Ensure Python and Poetry are installed:
python --version    # Should be ≥ 3.7
poetry --version

If Poetry is not installed:
curl -sSL https://install.python-poetry.org | python3 -

2. Create a Project Folder
mkdir my_fastapi_project
cd my_fastapi_project

3. Initialize the Project with Poetry
poetry init -n

4. Install Core Libraries
# If there are existing poetry.lock and pyproject.toml files, use this command to install necessary packages:
poetry install

# If neither poetry.lock nor pyproject.toml exists, install the core packages by executing:
poetry add fastapi uvicorn
# 💡 "uvicorn: is an ASGI server for running FastAPI applications"
# 🔁 "--reload: to automatically reload the server when code changes (suitable for development only)"

5. Create the Application File (e.g., main.py)
You can create the file manually or execute the following command:
cat > main.py << EOL
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
EOL

6. Run the Server
# First method (without activating the environment):
poetry run uvicorn main:app --reload

# Second method (after activating the environment):
eval $(poetry env activate) # Use deactivate to stop the environment
uvicorn main:app --reload

# ⚠️ "If you encounter a command not found error when running poetry env activate, you may need to update Poetry:"
poetry self update

# "Open the link in your browser: http://127.0.0.1:8000"

7. (Optional) Add a Shortcut Command for Running
# Modify the pyproject.toml file and add:
[tool.poetry.scripts]
start = "uvicorn main:app --reload"

# Then simply run the project:
poetry run start

✅ And that's how you set up a Poetry environment for your FastAPI project!


********************************************************************************************

🛡️ نظام المصادقة FastAPI

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
```



## 🧠 أمور تقنية مهمة

جميع المسارات محمية بـ Depends(get_current_user) الذي يتحقق من صلاحية التوكن وفعالية الحساب.

إذا تم تعطيل حساب المستخدم، فلا يمكنه تسجيل الدخول ولا تنفيذ أي عملية.

تم استعمال Redis كوسيط لتعطيل التوكنات (Blacklisting).

تم اعتماد JWT لتوثيق المستخدمين بدون جلسات.




## 🎯 الاستخدام

هذا المشروع مناسب لك إذا:

كنت تريد نظام مصادقة سريع وآمن وقابل للتعديل.

تبحث عن نقطة انطلاق جاهزة لمشروعك.

لا تحتاج في البداية للتحقق بخطوتين أو تعقيدات إضافية.




## 📄 الرخصة

MIT License – مفتوح المصدر، يمكنك استخدامه بحرية في مشاريعك الشخصية أو التجارية.





## ✉️ تواصل

لأي استفسار أو اقتراح، يرجى فتح Issue على GitHub أو التواصل عبر LinkedIn.
https://www.linkedin.com/in/mohammed-bachir-henka-it/







# دليل سريع لإنشاء مشروع FastAPI باستخدام Poetry

## 1. التحقق من التثبيت
### تأكد من وجود Python و Poerty مثبتين:
```bash
python --version    # يجب أن تكون ≥ 3.7
poetry --version
```

### إذا لم يكن Poetry مثبتًا:
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
يمكنك إنشاء الملف يدويًا أو تنفيذ الأمر التالي لإنشائه تلقائيًا:
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







