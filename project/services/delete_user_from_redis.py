from typing import Literal
from redis.asyncio import Redis
from project.services.is_token_in_redis import (
    is_token_active_in_redis,
    is_token_blacklisted_in_redis,
)
from project.services.token_key_format import token_key_format
from project.core import logger, TokenExpiredException, ServerErrorException


async def delete_user_from_redis(
    redis: Redis,
    payload: dict,
    token: str,
    status: Literal["any", "active", "blacklisted", "current_only"] = "any",
) -> bool:
    logger.debug("بدء عملية حذف التوكنات من Redis حسب الحالة المحددة: %s", status)

    username: str = payload.get("sub")

    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    token_key = token_key_format(username, token)
    logger.debug("تم توليد مفتاح Redis للتوكن الحالي")

    if status == "current_only":
        try:
            logger.debug("محاولة حذف التوكن الحالي فقط من Redis")
            await redis.delete(token_key)
            logger.info("تم حذف التوكن الحالي من Redis بنجاح")
        except Exception as e:
            logger.error("فشل أثناء حذف التوكن الحالي من Redis", exc_info=True)
            raise ServerErrorException(
                "حدث خطأ أثناء محاولة حذف التوكن الحالي من Redis"
            )
        return True

    try:
        logger.debug("بدء المسح عن جميع مفاتيح التوكنات الخاصة بالمستخدم")
        keys = []
        async for key in redis.scan_iter(match=f"user_token:{username}:*"):
            token_from_key = key.split(":")[-1]
            if status == "any":
                keys.append(key)
            elif status == "active" and await is_token_active_in_redis(
                payload, token_from_key, redis
            ):
                keys.append(key)
            elif status == "blacklisted" and await is_token_blacklisted_in_redis(
                payload, token_from_key, redis
            ):
                keys.append(key)

        logger.debug("عدد المفاتيح المطابقة التي سيتم حذفها: %d", len(keys))
        if keys:
            await redis.delete(*keys)
            logger.info("تم حذف التوكنات المطابقة من Redis بنجاح")
    except Exception as e:
        logger.error("فشل أثناء حذف التوكنات المطابقة من Redis", exc_info=True)
        raise ServerErrorException(
            "حدث خطأ أثناء محاولة حذف التوكنات المطابقة من Redis"
        )

    return True
