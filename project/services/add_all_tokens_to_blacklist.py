from redis.asyncio import Redis
from project.services.get_remaining_time import get_remaining_time
from project.services.add_token_to_blacklist import add_token_to_blacklist
from project.services.is_token_in_redis import is_token_blacklisted_in_redis
from project.core import logger, TokenExpiredException, ServerErrorException


async def add_all_tokens_to_blacklist(
    redis: Redis,
    payload: dict,
) -> bool:
    logger.debug("بدء عملية إدراج جميع التوكنات في القائمة السوداء")

    username: str = payload.get("sub")

    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    try:
        logger.debug("بدء البحث عن مفاتيح الجلسات في Redis للمستخدم: [مخفي]")
        keys = []
        async for key in redis.scan_iter(match=f"user_token:{username}:*"):
            token_from_key = key.split(":")[-1]
            if not await is_token_blacklisted_in_redis(
                payload,
                token_from_key,
                redis,
            ):
                logger.debug("تم العثور على توكن لم يتم إدراجه في القائمة السوداء، سيتم إدراجه الآن")
                await add_token_to_blacklist(
                    redis,
                    payload,
                    token_from_key,
                    get_remaining_time(token_from_key),
                )
    except Exception as e:
        logger.error("حدث استثناء أثناء محاولة إدراج التوكنات في القائمة السوداء", exc_info=True)
        raise ServerErrorException("حدث خطأ أثناء محاولة إبطال جميع الجلسات السابقة")

    logger.info("تم إدراج جميع التوكنات في القائمة السوداء بنجاح")
    return True
