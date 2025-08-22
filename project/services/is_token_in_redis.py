from redis.asyncio import Redis

from project.services.token_key_format import token_key_format
from project.core import logger, TokenExpiredException


async def is_token_active_in_redis(
    payload: dict,
    token: str,
    redis: Redis,
) -> bool:
    logger.debug("التحقق مما إذا كان التوكن نشطًا في Redis")
    username: str = payload.get("sub")
    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")
    token_key = token_key_format(username, token)
    logger.debug("تم توليد مفتاح Redis للتحقق من النشاط")
    value = await redis.get(token_key)
    return value is not None and value == "active"


async def is_token_blacklisted_in_redis(
    payload: dict,
    token: str,
    redis: Redis,
) -> bool:
    logger.debug("التحقق مما إذا كان التوكن محظورًا في Redis")
    username: str = payload.get("sub")
    if username is None:
        logger.warning("التوكن لا يحتوي على اسم مستخدم.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")
    token_key = token_key_format(username, token)
    logger.debug("تم توليد مفتاح Redis للتحقق من الحظر")
    value = await redis.get(token_key)
    return value is not None and value == "blacklisted"
