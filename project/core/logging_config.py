import logging
import os
from logging.handlers import TimedRotatingFileHandler
from project.core.config import settings
# تهيئة سجل الأحداث

LOG_LEVEL = logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING

# إعداد المجلد
os.makedirs("project/logs", exist_ok=True)

# المُسجّل الأساسي
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# منع التكرار في حالة إعادة الاستيراد
if not logger.hasHandlers():
    # معالج افتراضي (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    stream_handler.setLevel(LOG_LEVEL)
    logger.addHandler(stream_handler)

    # معالج للأخطاء الحرجة، يدور يوميًا
    critical_handler = TimedRotatingFileHandler(
        filename="project/logs/critical.log",
        when="midnight",  # تدوير يومي
        interval=1,
        backupCount=30,  # احتفاظ بـ 30 يومًا
        encoding="utf-8",
    )
    critical_handler.setLevel(logging.ERROR)
    critical_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(critical_handler)

# معالج لتخزين debug و info و warning في وضع التطوير فقط
    if settings.ENVIRONMENT == "development":
        dev_handler = TimedRotatingFileHandler(
            filename="project/logs/dev.log",
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        dev_handler.setLevel(logging.DEBUG)
        dev_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(dev_handler)