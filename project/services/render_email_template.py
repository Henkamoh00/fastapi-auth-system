from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from project.core import logger
from typing import Dict

# إعداد بيئة Jinja2 لتحميل القوالب
jinja_env = Environment(loader=FileSystemLoader('project/templates'))

def render_email_template(template_name: str, **kwargs) -> str:
    """توليد محتوى HTML باستخدام Jinja2"""
    try:
        logger.debug("بدء توليد قالب البريد الإلكتروني: %s", template_name)
        template = jinja_env.get_template(template_name)
    except TemplateNotFound:
        logger.error("قالب البريد '%s' غير موجود", template_name)
        raise
    except Exception as e:
        logger.error("فشل في تحميل قالب البريد الإلكتروني: %s", template_name, exc_info=True)
        raise

    logger.info("تم توليد محتوى البريد الإلكتروني بنجاح: %s", template_name)
    return template.render(**kwargs)