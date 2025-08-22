from email.message import EmailMessage
import smtplib
from project.core import logger, settings, ServerErrorException, SuccessResponse
from project.services.render_email_template import render_email_template

SENDER_EMAIL = settings.MAIL_USERNAME


def send_email(subject: str, recipient: str, html_content: str):
    logger.debug("بدء إعداد البريد الإلكتروني للإرسال")

    msg = EmailMessage()
    msg.set_content("This is a plain text message")
    msg.add_alternative(html_content, subtype="html")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    # الاتصال بـ SMTP وإرسال البريد
    try:
        logger.debug("محاولة الاتصال بخادم SMTP")

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            server.starttls()  # استخدام TLS
            server.login(SENDER_EMAIL, settings.MAIL_PASSWORD)
            logger.info("تم تسجيل الدخول بنجاح إلى خادم SMTP")
            server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
            logger.info("تم إرسال البريد الإلكتروني بنجاح")
    except Exception as e:
        logger.error(f"فشل إرسال البريد الإلكتروني: {e}")


def send_forgot_password_email(user_email: str, token: str):
    subject = "استعادة كلمة المرور - تطبيق حلوياتي"
    html_content = render_email_template(
        "reset_password_template.html",
        reset_link=token,
    )
    send_email(subject, user_email, html_content)


def send_account_confirmation_email(user_email: str, token: str):
    subject = "تأكيد الحساب - تطبيق حلوياتي"
    html_content = render_email_template(
        "account_confirmation_template.html",
        verify_link=token,
    )
    send_email(subject, user_email, html_content)
