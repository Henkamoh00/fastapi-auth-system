from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from project.core import (
    logger,
    settings,
    create_token,
    ServerErrorException,
)
from project.models import User
from project.services.deactivate_refresh_tokens import deactivate_user_refresh_tokens


# دالة منفصلة لإنشاء وحفظ refresh token في قاعدة البيانات
async def create_and_store_refresh_token(user: User, db: AsyncSession) -> str:
    logger.debug("بدء إنشاء وحفظ refresh token في قاعدة البيانات")

    refresh_token_expires = timedelta(weeks=settings.ACCESS_TOKEN_EXPIRE_WEEK)
    logger.debug("بدء إنشاء وحفظ refresh token في قاعدة البيانات")
    refresh_token = create_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires,
    )
    logger.debug("تم إنشاء refresh token بنجاح")

    expires_at = datetime.now(timezone.utc) + refresh_token_expires

    # تخزين التوكن في قاعدة البيانات
    from project.models import Token  # استيراد داخل الدالة لتفادي الدوران

    logger.debug("تجهيز كائن التوكن وتخزينه في قاعدة البيانات")
    token_obj = Token(
        user_id=user.id,
        token=refresh_token,
        is_active=True,
        expires_at=expires_at,
    )
    try:
        db.add(token_obj)
        await db.commit()
        logger.info("تم تخزين refresh token بنجاح في قاعدة البيانات")
    except Exception as e:
        logger.error(f"فشل في انشاء refresh token - خطأ في قاعدة البيانات: {e}")
        await db.rollback()
        raise ServerErrorException("حدث خطأ أثناء انشاء رمز التحديث. يرجى المحاولة مرة أخرى لاحقًا.")

    logger.debug("محاولة تعطيل جميع توكنات التحديث النشطة السابقة للمستخدم")
    # تعطيل جميع توكنات التحديث النشطة للمستخدم قبل إنشاء توكن جديد
    await deactivate_user_refresh_tokens(user.id, db)
    logger.info("تم تعطيل جميع توكنات التحديث النشطة السابقة بنجاح")

    return refresh_token
