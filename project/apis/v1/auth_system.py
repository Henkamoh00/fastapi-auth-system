from datetime import timedelta
from redis.asyncio import Redis
from fastapi import Request, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.background import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_
from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from project.core import (
    settings,
    oauth2_scheme,
    limiter,
    logger,
    verify_password,
    get_db,
    get_password_hash,
    decode_token,
    get_redis,
    generate_token_link,
    verify_token_link,
    BadRequestException,
    PermissionDeniedException,
    NotAuthenticatedException,
    TokenExpiredException,
    CredentialsValidationException,
    ServerErrorException,
    SuccessResponse,
    CreatedResponse,
)
from project.models import User, Token
from project.schemas import (
    UserSchema,
    UserCreationSchema,
    UserLoginSchema,
    UserUpdateSchema,
    PasswordChangingSchema,
    TokenSchema,
    RefreshTokenRequest,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    VerifyEmailSchema,
    jsonResponseSchema,
)
from project.services import (
    create_access_token,
    create_and_store_refresh_token,
    get_current_user,
    add_token_to_blacklist,
    add_all_tokens_to_blacklist,
    process_logout,
    get_remaining_time,
    process_login,
    send_forgot_password_email,
    send_account_confirmation_email,
)


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login-form", response_model=jsonResponseSchema)
@limiter.limit("0/day")
async def login_form(
    request: Request,
    data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    logger.info(f"محاولة تسجيل دخول عبر login-form من IP: {request.client.host}")
    if request.client.host != "127.0.0.1":
        logger.warning(f"محاولة وصول غير مصرح بها من IP: {request.client.host}")
        raise PermissionDeniedException()
    data = await process_login(data.username, data.password, db, redis)
    logger.info(f"تسجيل دخول ناجح للمستخدم: {data['username']}")
    return SuccessResponse(
        message="تم تسجيل الدخول بنجاح",
        data=data,
    )


@auth_router.post("/login", response_model=jsonResponseSchema)
@limiter.limit("10/minute")
@limiter.limit("30/day")
async def login_json(
    request: Request,
    data: UserLoginSchema,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    logger.info("محاولة تسجيل دخول للمستخدم")
    data = await process_login(data.username, data.password, db, redis)
    logger.info("تسجيل دخول ناجح للمستخدم")
    return SuccessResponse(
        message="تم تسجيل الدخول بنجاح",
        data=data.model_dump(),
    )


@auth_router.get("/me", response_model=jsonResponseSchema)
async def read_users_me(current_user: User = Depends(get_current_user)):
    if not current_user:
        logger.warning("محاولة غير مصرح بها للوصول إلى /me")
        raise NotAuthenticatedException()
    data = UserSchema.model_validate(current_user)
    logger.info("تم جلب بيانات المستخدم {current_user.username} بنجاح")
    return SuccessResponse(
        message="تم جلب بيانات المستخدم بنجاح",
        data=data,
    )


@auth_router.post("/register", response_model=jsonResponseSchema)
@limiter.limit("5/day")
async def register_user(
    request: Request,
    user_create: UserCreationSchema,
    db: AsyncSession = Depends(get_db),
):
    logger.info("محاولة تسجيل مستخدم جديد")
    query = select(User).where(
        or_(User.username == user_create.username, User.email == user_create.email)
    )
    logger.debug("التحقق من وجود مستخدم مسبق")
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        if (
            existing_user.username == user_create.username
            and existing_user.email == user_create.email
        ):
            logger.warning("اسم المستخدم والبريد الإلكتروني مستخدمَين مسبقًا")
            raise CredentialsValidationException(
                "اسم المستخدم والبريد الإلكتروني مستخدَمين فعلا"
            )
        elif existing_user.username == user_create.username:
            logger.warning("اسم المستخدم مستخدَم مسبقًا")
            raise CredentialsValidationException("اسم المستخدم مستخدَم فعلا")
        elif existing_user.email == user_create.email:
            logger.warning("البريد الإلكتروني مستخدَم مسبقًا")
            raise CredentialsValidationException("البريد الإلكتروني مستخدَم فعلا")

    hashed_password = get_password_hash(user_create.hashed_password)
    new_user = User(
        firstName=user_create.firstName,
        lastName=user_create.lastName,
        username=user_create.username,
        gender=user_create.gender,
        email=user_create.email,
        phoneNumber=user_create.phoneNumber,
        locations=user_create.locations,
        birthDate=user_create.birthDate,
        birthPlace=user_create.birthPlace,
        profilePhoto=user_create.profilePhoto,
        hashed_password=hashed_password,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        logger.error("فشل في إنشاء مستخدم جديد - خطأ في قاعدة البيانات")
        raise ServerErrorException("حدث خطأ أثناء إنشاء المستخدم")
    user_schema = UserCreationSchema.model_validate(new_user)
    logger.info("تم إنشاء مستخدم جديد بنجاح")
    return CreatedResponse(
        message="تم إنشاء المستخدم بنجاح",
        data=user_schema.model_dump(),
    )


@auth_router.put("/change-password", response_model=jsonResponseSchema)
@limiter.limit("3/day")
async def change_password(
    request: Request,
    password_change: PasswordChangingSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
):
    if not verify_password(password_change.old_password, current_user.hashed_password):
        logger.warning(
            "محاولة تغيير كلمة مرور فاشلة: كلمة المرور القديمة غير صحيحة للمستخدم."
        )
        raise CredentialsValidationException("كلمة المرور القديمة خاطئة")

    # تحديث كلمة المرور
    try:
        current_user.hashed_password = get_password_hash(password_change.new_password)
        current_user.last_password_change = func.now()  # تحديث وقت آخر تغيير
        await db.commit()
    except Exception as e:
        logger.error("فشل في تحديث كلمة المرور: %s", e)
        raise ServerErrorException("حدث خطأ أثناء تحديث كلمة المرور")

    payload = decode_token(token)

    # وضع التوكن الحالي في القائمة السوداء وحذف جميع الجلسات السابقة
    deleted1 = await add_token_to_blacklist(
        redis, payload, token, get_remaining_time(token)
    )
    deleted2 = await add_all_tokens_to_blacklist(redis, payload)

    if deleted1 and deleted2:
        logger.info(
            "تم تغيير كلمة المرور بنجاح وإبطال الجلسات للمستخدم: %s",
            current_user.username,
        )
        return SuccessResponse(
            message="تم تحديث كلمة المرور بنجاح وتم إبطال جميع الجلسات السابقة",
        )


@auth_router.post("/logout", response_model=jsonResponseSchema)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis),
):
    logger.info("محاولة تسجيل خروج")

    if await process_logout(token, redis):
        logger.info("تم تسجيل الخروج بنجاح")
        return SuccessResponse(
            message="تم تسجيل الخروج بنجاح",
        )


@auth_router.post("/refresh-token", response_model=jsonResponseSchema)
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    logger.info("طلب تحديث توكن")
    try:
        refresh_token = payload.refresh_token

        payload = decode_token(refresh_token)

        username = payload.get("sub")

        query = select(User).where((User.username == username))

        result = await db.execute(query)
        user = result.scalars().first()

        query = select(Token).where(
            (Token.user_id == user.id)
            & (Token.is_active == True)
            & (Token.token == refresh_token)
        )
        result = await db.execute(query)
        the_token = result.scalars().first()
        logger.debug("تم العثور على المستخدم المطابق للتوكن")

        if not the_token or the_token.is_active is False:
            logger.warning("فشل التحقق من رمز التحديث: غير موجود أو غير نشط")
            raise TokenExpiredException("رمز التحديث منتهي الصلاحية أو غير صالح")

    except ExpiredSignatureError as e:
        logger.warning("انتهت صلاحية التوكن.")
        raise TokenExpiredException("انتهت صلاحية التوكن")

    except JWTClaimsError as e:
        logger.error("المحتوى الداخلي للتوكن غير صالح.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    except JWTError as e:
        logger.error("توكن غير صالح.")
        raise TokenExpiredException("توكن غير صالح")

    new_access_token = await create_access_token(user, redis)
    logger.debug("تم إنشاء access token جديد")

    # توليد refresh token جديد
    new_refresh_token = await create_and_store_refresh_token(user, db)
    logger.debug("تم إنشاء refresh token جديد")

    data = TokenSchema(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
    )
    logger.info("تم تحديث توكن الوصول لمستخدم بنجاح")
    return SuccessResponse(
        message="تم تحديث رمز الوصول بنجاح",
        data=data.model_dump(),
    )


@auth_router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordSchema,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    logger.info("طلب استعادة كلمة المرور")
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user:
        logger.warning("تم استلام طلب استعادة كلمة المرور لبريد غير مرتبط بأي حساب")
        return SuccessResponse(
            message="تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني إن وُجد حساب مرتبط به.",
            data=None,
        )

    reset_token = generate_token_link(user.email, "reset-password", settings.BASE_URL)
    logger.debug("تم إنشاء رمز إعادة تعيين كلمة المرور")

    background_tasks.add_task(send_forgot_password_email, user.email, reset_token)
    logger.info("تم إرسال تعليمات إعادة تعيين كلمة المرور")
    return SuccessResponse(
        message="تم إرسال تعليمات إعادة تعيين كلمة المرور إلى بريدك الإلكتروني إن وُجد حساب مرتبط به.",
        data=None,
    )


@auth_router.patch("/reset-password")
async def reset_password(
    data: ResetPasswordSchema,
    db: AsyncSession = Depends(get_db),
):
    logger.info("طلب إعادة تعيين كلمة المرور")
    try:
        email = verify_token_link(data.token, "reset-password")
    except BadRequestException as e:
        raise e

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        logger.warning("فشل التحقق من التوكن - المستخدم غير موجود")
        raise BadRequestException()

    user.hashed_password = get_password_hash(data.new_password)
    logger.debug("تم تحديث كلمة مرور المستخدم")
    try:
        await db.commit()
        logger.info("تم تغيير كلمة المرور بنجاح")
    except Exception as e:
        logger.error("فشل في استعادة كلمة المرور - خطأ في قاعدة البيانات")
        raise ServerErrorException("حدث خطأ أثناء استعادة كلمة المرور")

    return SuccessResponse(message="تم تغيير كلمة المرور بنجاح.", data=None)


@auth_router.post("/account-verification")
async def send_verification_email(
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    redis: Redis = Depends(get_redis),
):
    logger.info("طلب إرسال بريد تحقق من الهوية.")
    if not current_user:
        logger.warning("فشل في إرسال بريد التحقق - مستخدم غير معروف")
        raise BadRequestException()

    if current_user.emailIsVerified:
        logger.info("البريد الإلكتروني مؤكد مسبقًا")
        return SuccessResponse(message="تم التحقق من بريدك الإلكتروني مسبقًا", data=None)

    verify_link = generate_token_link(
        current_user.email,
        "account-verification",
        settings.BASE_URL,
    )
    logger.debug("تم إنشاء رابط التحقق")

    background_tasks.add_task(
        send_account_confirmation_email, current_user.email, verify_link
    )
    logger.info("تم إرسال رابط التحقق")

    return SuccessResponse(
        message="تم إرسال رابط التحقق إلى بريدك الإلكتروني",
        data=None,
    )


@auth_router.patch("/account-confirmation")
async def verify_email(
    data: VerifyEmailSchema,
    db: AsyncSession = Depends(get_db),
):
    logger.info("محاولة تأكيد البريد الإلكتروني")
    try:
        email = verify_token_link(data.token, "account-verification")
    except BadRequestException as e:
        raise e

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        logger.warning("فشل تأكيد البريد الإلكتروني - المستخدم غير موجود")
        raise BadRequestException()

    if user.emailIsVerified:
        logger.info("البريد الإلكتروني مؤكد مسبقًا")
        return SuccessResponse(
            message="تم التحقق من هذا البريد الإلكتروني بالفعل",
            data=data.dict(),
        )

    user.emailIsVerified = True
    logger.debug("تم تعيين البريد كمؤكد")
    try:
        await db.commit()
        logger.info("تم تأكيد البريد الإلكتروني بنجاح")
    except Exception as e:
        logger.error("فشل في التحقق من البريد الإلكتروني - خطأ في قاعدة البيانات")
        raise ServerErrorException("حدث خطأ أثناء التحقق من البريد الإلكتروني")
    return SuccessResponse(
        message="تم التحقق من البريد الإلكتروني بنجاح",
        data=data.dict(),
    )


@auth_router.patch("/update-profile", response_model=jsonResponseSchema)
@limiter.limit("7/day")
async def update_profile(
    request: Request,
    updated_data: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info("طلب تعديل بيانات الحساب")

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalars().first()

    if not user:
        logger.warning("فشل تعديل البيانات - المستخدم غير موجود")
        raise BadRequestException()

    update_fields = updated_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(user, field, value)

    try:
        await db.commit()
        await db.refresh(user)
        logger.info("تم تعديل بيانات الحساب بنجاح")
    except Exception as e:
        logger.error("فشل في تعديل البيانات - خطأ: %s", e)
        raise ServerErrorException("حدث خطأ أثناء تعديل بيانات الحساب")

    response_data = UserSchema.model_validate(user)
    return SuccessResponse(
        message="تم تعديل بيانات الحساب بنجاح",
        data=jsonable_encoder(response_data),
    )


@auth_router.patch("/deactivate-account", response_model=jsonResponseSchema)
@limiter.limit("1/day")
async def deactivate_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info("طلب تعطيل الحساب")

    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalars().first()

    if not user:
        logger.warning("فشل تعطيل الحساب - المستخدم غير موجود")
        raise BadRequestException()

    if user.isActive is False:
        logger.info("المستخدم حاول تعطيل حسابه وهو معطّل بالفعل")
        return SuccessResponse(message="تم تعطيل الحساب مسبقًا", data=None)

    user.isActive = False

    try:
        await db.commit()
        logger.info("تم تعطيل الحساب بنجاح")
    except Exception as e:
        logger.error("فشل في تعطيل الحساب - خطأ: %s", e)
        raise ServerErrorException("حدث خطأ أثناء تعطيل الحساب")

    return SuccessResponse(message="تم تعطيل الحساب بنجاح", data=None)
