from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from project.core import (
    logger,
    CredentialsValidationException,
    verify_password,
)
from project.models import User
from project.schemas import TokenSchema
from project.services.create_access_token import create_access_token
from project.services.create_and_store_refresh_token import create_and_store_refresh_token


# عملية تسجيل الدخول تنشئ رمز وصول جديد وتخزنها في Redis،
# وتقوم أيضًا بإنشاء رمز تحديث جديد وتخزينه في قاعدة البيانات.
# ترجع فقط رمز الوصول في الاستجابة.
async def process_login(
    username: str, password: str, db: AsyncSession, redis: Redis
) -> TokenSchema:
    logger.debug("بدء معالجة تسجيل الدخول للمستخدم: %s", username)

    query = select(User).where(User.username == username)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        logger.warning("المستخدم غير موجود: %s", username)
        raise CredentialsValidationException("اسم المستخدم أو كلمة المرور غير صحيحة")
    
    if not verify_password(password, user.hashed_password):
        logger.warning("كلمة مرور غير صحيحة للمستخدم: %s", username)
        raise CredentialsValidationException("اسم المستخدم أو كلمة المرور غير صحيحة")
    
    if not user.isActive:
        logger.warning("محاولة تسجيل دخول بحساب غير مفعل.")
        raise CredentialsValidationException("اسم المستخدم أو كلمة المرور غير صحيحة")

    access_token = await create_access_token(user, redis)
    logger.debug("تم إنشاء access token للمستخدم: %s", username)

    # لإنشاء وحفظ refresh token
    refresh_token = await create_and_store_refresh_token(user, db)
    logger.debug("تم إنشاء وتخزين refresh token للمستخدم: %s", username)

    logger.info("تسجيل دخول ناجح للمستخدم: %s", username)
    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
    )
