from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(
            self,
            email,
            password,
            username,
            first_name,
            last_name,
            **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        user = self.model(
            email=self.normalize_email(email),
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_superuser'):
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True!'
            )
        return self.create_user(email, username, password, **extra_fields)
