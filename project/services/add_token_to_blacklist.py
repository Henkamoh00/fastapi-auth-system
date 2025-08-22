from redis.asyncio import Redis
from project.core import (
    logger,
    TokenExpiredException,
    ServerErrorException,
    BadRequestException,
)
from project.services.token_key_format import token_key_format


async def add_token_to_blacklist(
    redis: Redis,
    payload: dict,
    token: str,
    expire_in: int = 604800,
) -> bool:
    logger.debug("بدء إدراج توكن في القائمة السوداء")

    username: str = payload.get("sub")

    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    # حذف التوكن في Redis مع مدة صلاحية (TTL)

    token_key = token_key_format(username, token)
    logger.debug("تم توليد مفتاح Redis للتوكن")

    try:
        logger.debug("محاولة تحويل قيمة مدة الصلاحية إلى عدد صحيح")
        expire_in = int(expire_in)
    except ValueError as e:
        logger.warning("قيمة مدة الصلاحية تحتوي على صيغة غير صحيحة")
        raise BadRequestException("قيمة مدة الصلاحية تحتوي على حروف أو صيغة غير صحيحة.")
    except TypeError as e:
        logger.warning("قيمة مدة الصلاحية مفقودة أو من نوع غير صالح")
        raise BadRequestException("قيمة مدة الصلاحية مفقودة أو من نوع غير مقبول.")

    try:
        logger.debug("محاولة حذف التوكن من Redis")
        await redis.delete(token_key)
    except Exception as e:
        logger.error("فشل أثناء حذف التوكن من Redis", exc_info=True)
        raise ServerErrorException("حدث خطأ أثناء محاولة حذف التوكن النشط من Redis")

    try:
        logger.debug("محاولة تخزين التوكن كمحظور في Redis")
        await redis.setex(token_key, expire_in, "blacklisted")
    except Exception as e:
        logger.error("فشل أثناء تخزين التوكن المحظور في Redis", exc_info=True)
        raise ServerErrorException("حدث خطأ أثناء محاولة تخزين التوكن المحظور في Redis")

    logger.info("تم إدراج التوكن في القائمة السوداء بنجاح")
    return True
