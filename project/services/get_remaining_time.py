from jose import JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from datetime import datetime, timezone
from project.core import (
    logger,
    TokenExpiredException,
    decode_token,
)


def get_remaining_time(token: str) -> float:
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")

        if not exp_timestamp:
            raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

        exp_time = datetime.fromtimestamp(
            exp_timestamp,
            tz=timezone.utc,
        )
        now = datetime.now(timezone.utc)
        remaining = exp_time - now

        if remaining.total_seconds() <= 0:
            raise TokenExpiredException("انتهت صلاحية التوكن")

        return remaining.total_seconds()
    except ExpiredSignatureError as e:
        logger.warning("انتهت صلاحية التوكن.")
        raise TokenExpiredException("انتهت صلاحية التوكن")

    except JWTClaimsError as e:
        logger.error("المحتوى الداخلي للتوكن غير صالح.")
        raise TokenExpiredException("المحتوى الداخلي للتوكن غير صالح")

    except JWTError as e:
        logger.error("توكن غير صالح.")
        raise TokenExpiredException("توكن غير صالح")
