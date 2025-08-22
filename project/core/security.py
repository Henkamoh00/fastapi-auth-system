from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from fastapi.security import OAuth2PasswordBearer
from project.core import settings
from passlib.context import CryptContext
from jose import JWTError, jwt

from project.core.httpException import BadRequestException, ServerErrorException, TokenExpiredException
from project.core.logging_config import logger


# ==============================
# تشفير كلمات المرور
# ==============================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    تحقق مما إذا كانت كلمة المرور العادية تتطابق مع النسخة المشفرة.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    إرجاع النسخة المشفرة لكلمة المرور.
    """
    return pwd_context.hash(password)


# ==============================
# إدارة JWT Token
# ==============================


def create_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    default_expire: timedelta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_24HOURS),
):
    """
    إنشاء JWT Token عام.

    :param data: البيانات التي سيتم تضمينها في التوكن.
    :param expires_delta: مدة صلاحية مخصّصة (اختياري).
    :param default_expire: مدة الصلاحية الافتراضية عند عدم تحديد expires_delta.
    :return: توكن مشفر.
    """
    logger.debug("بدء إنشاء JWT Token")
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (expires_delta or default_expire)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    logger.debug("تم إنشاء JWT Token بنجاح")
    return encoded_jwt


def decode_token(token: str) -> Union[dict, None]:
    """
    فك تشفير JWT Token.

    :param token: الـ JWT token
    :return: بيانات المستخدم أو None إذا كان التوكن غير صالح
    """
    logger.debug("محاولة فك JWT Token")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.debug("تم فك JWT Token بنجاح")
        return payload
    except JWTError as e:
        logger.warning("فشل فك JWT Token: توكن غير صالح")
        raise TokenExpiredException("توكن غير صالح")


# ==============================
# انشاء روابط التوكن المرسلة عبر البريد الإلكتروني
# ==============================

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_token_link(user_email: str, salt: str, base_url: str) -> str:
    logger.debug("بدء توليد رابط التوكن.")
    try:
        token = serializer.dumps(user_email, salt=salt)
        logger.debug("تم توليد رابط التوكن بنجاح")
        return f"{base_url}/{salt}?token={token}"
    except Exception as e:
        logger.error("فشل توليد رابط التوكن: خطأ غير متوقع")
        raise ServerErrorException("فشل توليد رابط إعادة تعيين كلمة المرور.")


def verify_token_link(token: str, salt: str, max_age: int = 10800) -> int:
    logger.debug("بدء التحقق من صحة رابط التوكن")
    try:
        user_id = serializer.loads(token, salt=salt, max_age=max_age)
        logger.debug("تم التحقق من صحة التوكن بنجاح")
        return user_id
    except SignatureExpired as e:
        logger.warning("انتهت صلاحية رابط التوكن")
        raise BadRequestException("انتهت صلاحية الرابط، الرجاء طلب رابط جديد.")
    except BadSignature as e:
        logger.warning("رابط التوكن غير صالح")
        raise BadRequestException("الرابط غير صالح.")


# أداة للحصول على التوكن من الطلب

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login-form")
