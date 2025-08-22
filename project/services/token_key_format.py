from project.core import logger


def token_key_format(username: str, token: str) -> str:
    logger.debug("تم توليد المفتاح: user_token:%s:<token>", username)
    return f"user_token:{username}:{token}"
