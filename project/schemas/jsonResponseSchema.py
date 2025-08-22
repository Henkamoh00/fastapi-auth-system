from pydantic import BaseModel
from typing import Optional, Dict, Literal


# نموذج استجابة JSON أساسي
# يحتوي على الحقول المشتركة لجميع الاستجابات
# يمكن استخدامه كأساس لنماذج استجابة أخرى
# أو يمكن استخدامه مباشرة في الاستجابات العامة
# يمكن تعديل الحقول حسب الحاجة
# يمكن استخدام Literal لتحديد القيم الثابتة للحقول
# يمكن استخدام Optional لتحديد الحقول الاختيارية
# يمكن استخدام Dict لتحديد نوع البيانات في الحقل data
class jsonResponseSchema(BaseModel):
    ok: bool
    status: Literal[
        "SUCCESS",
        "CREATED",
        "BAD_REQUEST",
        "UNAUTHORIZED",
        "FORBIDDEN",
        "NOT_FOUND",
        "INTERNAL_SERVER_ERROR"
    ]
    statusCode: int
    data: Optional[Dict] = {}
    message: str


# لم نستخدم أي من الحالات الموالية في المشروع انما اكتفينا بالشكل العام

class SuccessResponseSchema(jsonResponseSchema):
    ok: Literal[True] = True
    status: Literal["SUCCESS"] = "SUCCESS"
    statusCode: Literal[200] = 200
    message: str = "تمت العملية بنجاح"


class CreatedResponseSchema(jsonResponseSchema):
    ok: Literal[True] = True
    status: Literal["CREATED"] = "CREATED"
    statusCode: Literal[201] = 201
    message: str = "تم الإنشاء بنجاح"


class BadRequestResponseSchema(jsonResponseSchema):
    ok: Literal[False] = False
    status: Literal["BAD_REQUEST"] = "BAD_REQUEST"
    statusCode: Literal[400] = 400
    message: str = "طلب غير صالح"


class UnauthorizedResponseSchema(jsonResponseSchema):
    ok: Literal[False] = False
    status: Literal["UNAUTHORIZED"] = "UNAUTHORIZED"
    statusCode: Literal[401] = 401
    message: str = "غير مصرح"


class ForbiddenResponseSchema(jsonResponseSchema):
    ok: Literal[False] = False
    status: Literal["FORBIDDEN"] = "FORBIDDEN"
    statusCode: Literal[403] = 403
    message: str = "ممنوع"


class NotFoundResponseSchema(jsonResponseSchema):
    ok: Literal[False] = False
    status: Literal["NOT_FOUND"] = "NOT_FOUND"
    statusCode: Literal[404] = 404
    message: str = "غير موجود"


class InternalErrorResponseSchema(jsonResponseSchema):
    ok: Literal[False] = False
    status: Literal["INTERNAL_SERVER_ERROR"] = "INTERNAL_SERVER_ERROR"
    statusCode: Literal[500] = 500
    message: str = "خطأ في الخادم"
