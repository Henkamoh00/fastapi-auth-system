from datetime import timedelta
from redis.asyncio import Redis
from project.core import (
    logger,
    settings,
    create_token,
    decode_token,
)
from project.models import User
from project.services.add_token_to_redis import add_token_to_redis


async def create_access_token(
    user: User,
    redis: Redis,
) -> str:
    """
    انشاء رمز الوصول للمستخدم وتخزينه في ريديس.
    """

    logger.debug("بدء إنشاء رمز الوصول وتخزينه في Redis")
    access_token_expires = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_24HOURS)
    logger.debug("جاري إنشاء التوكن للمستخدم: %s", user.username)
    access_token = create_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    logger.debug("تم إنشاء التوكن بنجاح")
    payload = decode_token(access_token)
    logger.debug("تم فك تشفير التوكن بنجاح")

    expire_in = int(access_token_expires.total_seconds())

    logger.debug("محاولة تخزين التوكن في Redis")
    await add_token_to_redis(redis, payload, access_token, expire_in)

    logger.info("تم إنشاء وتخزين رمز الوصول.")
    return access_token
