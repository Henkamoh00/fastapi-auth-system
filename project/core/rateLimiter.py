from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
import re
import os
from project.core.config import settings


# إعداد معدل الطلبات باستخدام SlowAPI
ENVIRONMENT = settings.ENVIRONMENT or "development"

REDIS_HOST = settings.REDIS_HOST or "localhost"
REDIS_PORT = settings.REDIS_PORT or "6379"
REDIS_DB = settings.REDIS_DB or 0
if REDIS_HOST == "localhost":
    STORAGE_URI = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    STORAGE_URI = f"rediss://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

DEFAULT_LIMIT = "7/hour" if ENVIRONMENT == "production" else "3/minute"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["3/minute"],
    storage_uri=STORAGE_URI,
)


# دالة لتحويل الأرقام إلى وحدات زمنية باللغة العربية
def arabic_unit(number: int, unit: str) -> str:
    number = int(number)

    units = {
        "second": ["ثانية", "ثانيتين", "ثوانٍ"],
        "minute": ["دقيقة", "دقيقتين", "دقائق"],
        "hour": ["ساعة", "ساعتين", "ساعات"],
        "day": ["يوم", "يومين", "أيام"],
    }

    singular, dual, plural = units.get(unit, [unit, unit, unit])

    if number == 1:
        return f"{number} {singular}"
    elif number == 2:
        return f"{dual}"
    elif 3 <= number <= 10:
        return f"{number} {plural}"
    else:
        return f"{number} {singular}"


# استثناء مخصص لمعالجة تجاوز الحد المسموح به
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    detail = str(exc.detail)

    # استخراج العدد والفترة من الرسالة
    match = re.search(r"(\d+)\s+per\s+(\d+)?\s?(\w+)", detail)

    if match:
        count = int(match.group(1))
        period_num = match.group(2) or "1"
        period_unit = match.group(3)

        period_text = arabic_unit(period_num, period_unit)

        msg = f"لقد تجاوزت الحد المسموح به وهو {count} محاولة كل {period_text}. يرجى الانتظار ثم المحاولة مجددًا."
    else:
        msg = "لقد تجاوزت الحد المسموح به. يرجى المحاولة لاحقًا."

    return JSONResponse(
        status_code=429,
        content={
            "ok": False,
            "status": "WARNING",
            "data": {},
            "message": msg,
            "statusCode": 429,
        },
    )
