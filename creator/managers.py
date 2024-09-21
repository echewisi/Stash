from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



class CustomUserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_('please enter a valid email!'))   

    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("Email required!")
        email = self.normalize_email(email)
        if not username:
            raise ValueError("firstname required!")
        
        user = self.model(email=self.normalize_email(email), username= username,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("is_staff must be true for superuser"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("is_superuser must be true for superuser"))

        if extra_fields.get("is_verified") is not True:
            raise ValueError(_("is_verified must be true for superuser"))
        
        if extra_fields.get("is_active") is not True:
            raise ValueError(_("is_active must be true for superuser"))

        return self.create_user(email= self.normalize_email(email), username= username, password= password, **extra_fields)