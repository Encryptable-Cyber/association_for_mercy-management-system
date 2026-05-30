"""Custom email backend with SSL context support."""
import ssl
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend


class CustomEmailBackend(SMTPBackend):
    """Custom SMTP backend that accepts a custom SSL context."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = ssl._create_unverified_context()