from fastapi import Depends
from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from project.core import (
    oauth2_scheme,
    logger,
    get_db,
    decode_token,
    get_redis,
    TokenExpiredException,
    NotAuthenticatedException,
    BadRequestException,
)
from project.models import User
from project.services.is_token_in_redis import (
    is_token_blacklisted_in_redis,
    is_token_active_in_redis,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:

    try:

        payload = decode_token(token)

        if not isinstance(payload, dict):
            raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

        username: str = payload.get("sub")
        iat: int = payload.get("iat")  # وقت إصدار التوكن

        if not username:
            raise TokenExpiredException("اسم المستخدم غير موجود داخل التوكن")
        if not iat:
            raise TokenExpiredException("وقت إصدار التوكن مفقود")

        if await is_token_blacklisted_in_redis(payload, token, redis):
            raise NotAuthenticatedException(
                "تم تسجيل الخروج من هذا التوكن أو تم إلغاؤه"
            )

        if not await is_token_active_in_redis(payload, token, redis):
            raise NotAuthenticatedException("التوكن غير نشط، الرجاء تسجيل الدخول مجددًا")

        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()

        # التحقق من وجود المستخدم
        if user is None:
            raise BadRequestException()
        
        # التحقق من أن حساب المستخدم نشط
        if not user.isActive:
            logger.warning("حساب هذا المستخدم غير نشط")
            raise NotAuthenticatedException()

        # التحقق من أن التوكن لم يصدر قبل تغيير كلمة المرور
        if user.last_password_change and iat < user.last_password_change.timestamp():
            raise TokenExpiredException("تم تغيير كلمة المرور بعد إصدار هذا التوكن")

        return user

    except ExpiredSignatureError as e:
        logger.warning("انتهت صلاحية التوكن.")
        raise TokenExpiredException("انتهت صلاحية التوكن")

    except JWTClaimsError as e:
        logger.error("المحتوى الداخلي للتوكن غير صالح.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    except JWTError as e:
        logger.error("توكن غير صالح.")
        raise TokenExpiredException("توكن غير صالح")
