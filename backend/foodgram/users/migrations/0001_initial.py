# Generated by Django 4.0 on 2021-12-29 12:00

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [('auth', '0012_alter_user_first_name_max_length')]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'password',
                    models.CharField(max_length=128, verbose_name='password'),
                ),
                (
                    'last_login',
                    models.DateTimeField(
                        blank=True, null=True, verbose_name='last login'
                    ),
                ),
                (
                    'is_superuser',
                    models.BooleanField(
                        default=False,
                        help_text='Designates that this user has all permissions without explicitly assigning them.',
                        verbose_name='superuser status',
                    ),
                ),
                (
                    'is_staff',
                    models.BooleanField(
                        default=False,
                        help_text='Designates whether the user can log into this admin site.',
                        verbose_name='staff status',
                    ),
                ),
                (
                    'is_active',
                    models.BooleanField(
                        default=True,
                        help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                        verbose_name='active',
                    ),
                ),
                (
                    'date_joined',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name='date joined',
                    ),
                ),
                (
                    'email',
                    models.EmailField(
                        max_length=254, unique=True, verbose_name='Почта'
                    ),
                ),
                (
                    'username',
                    models.CharField(
                        max_length=150, unique=True, verbose_name='Логин'
                    ),
                ),
                (
                    'first_name',
                    models.CharField(max_length=150, verbose_name='Имя'),
                ),
                (
                    'last_name',
                    models.CharField(max_length=150, verbose_name='Фамилия'),
                ),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.Group',
                        verbose_name='groups',
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True,
                        help_text='Specific permissions for this user.',
                        related_name='user_set',
                        related_query_name='user',
                        to='auth.Permission',
                        verbose_name='user permissions',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('username',),
            },
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created_at',
                    models.DateField(
                        auto_now_add=True,
                        validators=[
                            django.core.validators.MinValueValidator(
                                1, message='Значение не может быть меньше 1'
                            )
                        ],
                        verbose_name='Создан',
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='following',
                        to='users.customuser',
                        verbose_name='Подписки',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='follower',
                        to='users.customuser',
                        verbose_name='Пользователь',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Подписки',
                'verbose_name_plural': 'Подписки',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(
                fields=('author', 'user'), name='unique_follow'
            ),
        ),
    ]