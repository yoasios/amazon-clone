from passlib.context import CryptContext
from ..services.settings import settings

pwd_context = CryptContext(schemes=[settings.scheme], deprecated="auto")