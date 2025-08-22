import os
from fastapi import FastAPI
from redis.asyncio import Redis
from project.apis.v1 import auth_system
from fastapi.middleware.cors import CORSMiddleware
from project.core import (
    settings,
    CustomException,
    SuccessResponse,
    create_tables,
    get_redis,
    custom_rate_limit_handler,
    custom_http_exception_handler,
)
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded


# إنشاء الجداول في قاعدة البيانات تلقائياً عند بدء التشغيل
# والتحقق من اتصال ريديس
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up...")
    await create_tables()
    try:
        redis_: Redis | None = get_redis()
        await redis_.ping()
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis not connected: {e}")
    yield
    print("🛑 Shutting down...")


# إنشاء تطبيق FastAPI
app = FastAPI(lifespan=lifespan, title=settings.APP_NAME, version=settings.VERSION)

# تضمين إعداد استثناءات المقيّد بعدد مرات المحاولات
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# تضمين إعداد استثناءات HTTP مخصصة
app.add_exception_handler(CustomException, custom_http_exception_handler)

# إعدادات CORS للسماح بالوصول من الواجهة الأمامية
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # أو ضع الدومين الخاص بالواجهة الأمامية فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تضمين مسارات نظام المصادقة
app.include_router(auth_system.auth_router, prefix="/api")


# لإجبار الطلبات على استخدام HTTPS.
# from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
# app.add_middleware(HTTPSRedirectMiddleware)

# للسماح فقط بطلبات من نطاقات محددة (أمان إضافي).
# from starlette.middleware.trustedhost import TrustedHostMiddleware
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com", "*.example.com"])


@app.get("/")
async def root():
    return SuccessResponse(
        message="Welcome to the FastAPI Project",
        data={"environment": settings.ENVIRONMENT},
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)


# أمرالتنفيذ:
# poetry run python main.py