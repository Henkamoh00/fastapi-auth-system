from redis.asyncio import Redis
from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from project.services.add_token_to_blacklist import add_token_to_blacklist
from project.services.get_remaining_time import get_remaining_time
from project.services.is_token_in_redis import is_token_active_in_redis
from project.core import logger, TokenExpiredException, decode_token


async def process_logout(token: str, redis: Redis) -> bool:
    if not token:
        logger.warning("طلب تسجيل خروج بدون توكن")
        raise TokenExpiredException("توكن غير صالح")

    try:
        payload = decode_token(token)
        logger.info("تم فك التوكن بنجاح أثناء تسجيل الخروج.")

        if not await is_token_active_in_redis(payload, token, redis):
            logger.warning("محاولة تسجيل خروج بتوكن غير مفعل في Redis.")
            raise TokenExpiredException("التوكن غير مفعل على ريديس")

        deleted = await add_token_to_blacklist(
            redis,
            payload,
            token,
            get_remaining_time(token),
        )

    except ExpiredSignatureError as e:
        logger.warning("انتهت صلاحية التوكن.")
        raise TokenExpiredException("انتهت صلاحية التوكن")

    except JWTClaimsError as e:
        logger.error("المحتوى الداخلي للتوكن غير صالح.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    except JWTError as e:
        logger.error("توكن غير صالح.")
        raise TokenExpiredException("توكن غير صالح")

    if deleted:
        logger.info("تم تسجيل الخروج بنجاح.")
        return True
    else:
        logger.error("فشل في تسجيل الخروج: لم يتم إضافة التوكن إلى القائمة السوداء.")
        return False
