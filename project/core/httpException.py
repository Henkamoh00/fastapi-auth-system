from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(self, message: str, status_code: int = 400, headers: dict = None):
        self.custom_message = message
        super().__init__(status_code=status_code, detail=message, headers=headers)


# استثناءات شائعة برسائل جاهزة
class CredentialsValidationException(CustomException):
    def __init__(self, message="تعذر التحقق من صحة بيانات الاعتماد"):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(CustomException):
    def __init__(self, message="انتهت صلاحية التوكن"):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotAuthenticatedException(CustomException):
    def __init__(self, message="الرجاء تسجيل الدخول أولاً"):
        super().__init__(
            message,
            status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(CustomException):
    def __init__(self, message="المستخدم غير موجود"):
        super().__init__(
            message,
            status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedException(CustomException):
    def __init__(self, message="ليس لديك صلاحية للوصول"):
        super().__init__(
            message,
            status.HTTP_403_FORBIDDEN,
        )


class ResourceConflictException(CustomException):
    def __init__(self, message="المورد موجود مسبقًا"):
        super().__init__(
            message,
            status.HTTP_409_CONFLICT,
        )


class BadRequestException(CustomException):
    def __init__(self, message="طلب غير صالح"):
        super().__init__(
            message,
            status.HTTP_400_BAD_REQUEST,
        )


class ServerErrorException(CustomException):
    def __init__(self, message="خطأ في الخادم"):
        super().__init__(
            message,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RateLimitExceededException(CustomException):
    def __init__(self, message="تم تجاوز عدد المحاولات المسموح به"):
        super().__init__(
            message,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )


async def custom_http_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "status": "ERROR",
            "statusCode": exc.status_code,
            "data": {},
            "message": exc.detail,
        },
        headers=exc.headers or {},
    )
