from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    "Класс переопределяет и расширяет стандартную модель User."

    USERNAME_ERR_MESS = (
        "Содержание поля 'username' не соответствует "
        "паттерну '^[\\w.@+-]+\\z'"
    )

    username = models.CharField(
        max_length=150,
        blank=False,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message=USERNAME_ERR_MESS,
            )
        ],
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        max_length=150,
        blank=False
    )
    password = models.CharField(
        max_length=150,
        blank=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ("-id",)

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    """Класс-модель описывает подписки пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="folower",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["user", "following"], name="unique_follow"
        )]

    def __str__(self):
        return f"Пользователь {self.user} подписан на {self.following}"
