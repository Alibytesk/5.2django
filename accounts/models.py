from django.db import models
from django.contrib.auth.models import AbstractBaseUser
import itertools
import re

class UserManager(models.Manager):
    def create_user(self, phone, username=None, email=None, password=None, **extra_fields):
        phone = self.normalize_phone(phone)
        if not email and not username:
            user = self.model(phone=phone, username=None, email=None, **extra_fields)
        else:
            if not email:
                username = self.normalize_username(username)
                user = self.model(phone=phone, username=username, email=None, **extra_fields)
            elif not username:
                email = self.normalize_email(email)
                user = self.model(phone=phone, username=None, email=email, **extra_fields)
            elif email and username:
                username = self.normalize_username(username)
                email = self.normalize_email(email)
                user = self.model(phone=phone, username=username, email=email, **extra_fields)
        password = self.normalize_password(password)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, phone, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(phone, username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    async def aget_by_natural_key(self, username):
        return await self.aget(**{self.model.USERNAME_FIELD: username})

    @staticmethod
    def normalize_password(password: str):
        errors, special_char = list(), '!@#$%^&*'
        if not password:
            raise ValueError('users must have a strong password')
        else:
            if not any(i.isdigit() for i in password):
                errors.append('password must contain at least one number')
            if not any(i in special_char for i in password):
                errors.append('password must contain at least one special character')
            if not any(i.isupper() for i in password):
                errors.append('password must contain at least one uppercase character')
            if not any(i.islower() for i in password):
                errors.append('password must contain at least one lowercase character')
            if len(password) < 8:
                errors.append('password must be at least 8 character')
            if not errors:
                return password
            else:
                raise ValueError(errors)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        if not phone:
            raise ValueError('users must have a valid Phone Number!')
        phone = UserManager.convert_persian_to_english(phone=phone)
        phone = re.sub(r'\D', '', phone)
        if phone.isdigit() and phone.startswith('09') and len(phone) == 11:
            return phone
        raise ValueError('invalid phone number')

    @staticmethod
    def convert_persian_to_english(phone: str) -> str:
        PER_EN_DIGITS: locals = dict({
            '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'
        })
        for per, en in PER_EN_DIGITS.items():
            phone = str(phone.replace(per, en))
        return phone

    @staticmethod
    def normalize_username(username: str):
        username = username.strip().lower()
        allowed = set('abcdefghijklmnopqrstuvwxyz0123456789')
        clean = (i if i in allowed else '_' for i in username)
        gp = (i for i, _ in itertools.groupby(clean))
        result = ''.join(gp).strip('_')
        return result

    @staticmethod
    def normalize_email(email):
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name + "@" + domain_part.lower()
        return email


class User(AbstractBaseUser):
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    objects = UserManager()
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_email_verify = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    @property
    def is_staff(self):
        return self.is_admin

    phone = models.CharField(
        unique=True,
        max_length=11,
        verbose_name='Phone Number',
        null=False,
        blank=False,
    )
    username = models.CharField(unique=True, max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=255, blank=True, null=True)
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='users_images', null=True, blank=True)

    def __str__(self):
        return f"{self.phone} {self.username} {self.email}|{self.is_email_verify}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True