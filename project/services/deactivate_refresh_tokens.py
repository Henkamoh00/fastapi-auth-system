from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from project.core import logger, BadRequestResponse, ServerErrorException
from project.models import Token


async def deactivate_all_user_refresh_tokens(
    user_id: int,
    db: AsyncSession,
):
    """
    تعطيل جميع توكنات التحديث النشطة الخاصة بالمستخدم.
    """

    try:
        logger.debug("بدء تعطيل جميع توكنات التحديث النشطة للمستخدم")
        query = update(Token).where(Token.user_id == user_id).values(is_active=False)
        await db.execute(query)
        await db.commit()
        logger.info("تم تعطيل جميع توكنات التحديث النشطة للمستخدم بنجاح")
    except Exception as e:
        logger.error("فشل أثناء تعطيل جميع توكنات التحديث", exc_info=True)
        raise ServerErrorException("فشل أثناء تعطيل جميع توكنات التحديث")


async def deactivate_user_refresh_tokens(
    user_id: int,
    db: AsyncSession,
    max_tokens: int = 3,
):
    """
    تعطيل توكنات التحديث النشطة الخاصة بالمستخدم اذا تجاوزت العدد المسموح.
    """

    logger.debug("بدء فحص عدد توكنات التحديث النشطة للمستخدم")
    if max_tokens <= 0:
        logger.warning("الحد الأقصى للتوكنات غير صالح (أقل من أو يساوي صفر)")
        raise BadRequestResponse("الحد الأقصى للتوكنات يجب أن يكون أكبر من صفر")

    query = (
        select(Token)
        .where(Token.user_id == user_id, Token.is_active == True)
        .order_by(Token.created_at.asc())
    )
    result = await db.execute(query)
    active_tokens = result.scalars().all()

    try:
        logger.debug("عدد التوكنات النشطة الحالية: %d", len(active_tokens))
        if len(active_tokens) > max_tokens:
            tokens_to_deactivate = active_tokens[: len(active_tokens) - max_tokens]
            logger.debug("عدد التوكنات التي سيتم تعطيلها: %d", len(tokens_to_deactivate))
            for token in tokens_to_deactivate:
                token.is_active = False
            await db.commit()
            logger.info("تم تعطيل التوكنات الزائدة بنجاح")
        logger.debug("لم يتم تجاوز الحد الأقصى، لا حاجة لتعطيل أي توكن")
    except Exception as e:
        logger.error("فشل أثناء التحقق أو تعطيل التوكنات", exc_info=True)
        raise ServerErrorException("فشل أثناء التحقق أو تعطيل التوكنات")
