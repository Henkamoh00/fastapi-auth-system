from fastapi.responses import JSONResponse


class StandardJSONResponse(JSONResponse):
    def __init__(
        self,
        status: str,
        status_code: int,
        ok: bool = True,
        data: dict = None,
        message: str = "",
        headers: dict = None,
    ):

        content = {
            "ok": ok,
            "status": status,
            "statusCode": status_code,
            "data": data or {},
            "message": message,
        }
        super().__init__(
            status_code=status_code, content=content, headers=headers or {}
        )


class SuccessResponse(StandardJSONResponse):
    def __init__(self, message: str = "تمت العملية بنجاح", data: dict = None):
        super().__init__(
            status="SUCCESS",
            status_code=200,
            ok=True,
            data=data,
            message=message,
        )


class CreatedResponse(StandardJSONResponse):
    def __init__(self, message: str = "تم الإنشاء بنجاح", data: dict = None):
        super().__init__(
            status="CREATED",
            status_code=201,
            ok=True,
            data=data,
            message=message,
        )


class BadRequestResponse(StandardJSONResponse):
    def __init__(self, message: str = "طلب غير صالح", data: dict = None):
        super().__init__(
            status="BAD_REQUEST",
            status_code=400,
            ok=False,
            data=data,
            message=message,
        )


class UnauthorizedResponse(StandardJSONResponse):
    def __init__(self, message: str = "غير مصرح", data: dict = None):
        super().__init__(
            status="UNAUTHORIZED",
            status_code=401,
            ok=False,
            data=data,
            message=message,
        )


class ForbiddenResponse(StandardJSONResponse):
    def __init__(self, message: str = "ممنوع", data: dict = None):
        super().__init__(
            status="FORBIDDEN",
            status_code=403,
            ok=False,
            data=data,
            message=message,
        )


class NotFoundResponse(StandardJSONResponse):
    def __init__(self, message: str = "غير موجود", data: dict = None):
        super().__init__(
            status="NOT_FOUND",
            status_code=404,
            ok=False,
            data=data,
            message=message,
        )


class InternalErrorResponse(StandardJSONResponse):
    def __init__(self, message: str = "خطأ في الخادم", data: dict = None):
        super().__init__(
            status="INTERNAL_SERVER_ERROR",
            status_code=500,
            ok=False,
            data=data,
            message=message,
        )
