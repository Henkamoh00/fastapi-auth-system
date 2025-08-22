from redis.asyncio import Redis
from project.core import (
    logger,
    TokenExpiredException,
    ServerErrorException,
    BadRequestException,
)
from project.services.token_key_format import token_key_format


async def add_token_to_redis(
    redis: Redis,
    payload: dict,
    token: str,
    expire_in: int = 604800,
) -> bool:
    logger.debug("بدء تخزين التوكن في Redis")

    username: str = payload.get("sub")

    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    try:
        logger.debug("محاولة تحويل قيمة مدة الصلاحية إلى عدد صحيح")
        expire_in = int(expire_in)
    except ValueError as e:
        logger.warning("فشل في تحويل مدة الصلاحية: قيمة غير صحيحة", exc_info=True)
        raise BadRequestException("قيمة مدة الصلاحية تحتوي على حروف أو صيغة غير صحيحة.")
    except TypeError as e:
        logger.warning("فشل في تحويل مدة الصلاحية: قيمة مفقودة", exc_info=True)
        raise BadRequestException("قيمة مدة الصلاحية مفقودة أو من نوع غير مقبول.")

    # تخزين التوكن في Redis مع مدة صلاحية (TTL)

    token_key = token_key_format(username, token)
    logger.debug("تم توليد مفتاح Redis للتوكن")

    try:
        logger.debug("محاولة تخزين التوكن في Redis بالحالة: active")
        await redis.setex(token_key, expire_in, "active")
    except Exception as e:
        logger.error("فشل أثناء تخزين التوكن في Redis", exc_info=True)
        raise ServerErrorException("حدث خطأ أثناء محاولة تخزين التوكن في Redis")

    logger.info("تم تخزين التوكن في Redis بنجاح")
    return True
