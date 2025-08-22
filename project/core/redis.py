from redis.asyncio import Redis
from project.core.config import settings
from functools import lru_cache



# دالة لإنشاء والاحتفاظ باتصال واحد فقط بـ Redis طوال مدة تشغيل التطبيق.
# تُستخدم async_lru_cache لتخزين نتيجة الاتصال الأول وإعادة استخدامها في كل استدعاء لاحق،
# مما يُجنّب إنشاء عدة اتصالات ويُحسّن الأداء.
# الاتصال يتم بشكل غير متزامن باستخدام Redis.asyncio، وهو مناسب لتطبيقات FastAPI.
@lru_cache()
def get_redis() -> Redis:

    if settings.ENVIRONMENT == "production" and getattr(settings, "REDIS_URL", None):
        return Redis.from_url(
            url=settings.REDIS_URL,
            decode_responses=True,
        )

    # fallback في حال عدم توفر URL
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
