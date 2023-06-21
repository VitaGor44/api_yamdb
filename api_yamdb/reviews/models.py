from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.contrib.auth.models import AbstractUser

ADMIN = 'admin'
MODERATOR = 'moderator'
USER = 'user'

ROLES = (
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin')
)

MAX_LENGTH = 256
MAX_LENGTH_NAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_CONF_CODE = 120
MAX_LENGTH_SLUG = 50


class User(AbstractUser):
    USERNAME_VALIDATOR = RegexValidator(r'^[\w.@+-]+\Z')
    bio = models.TextField(
        'Дополнительная информация',
        blank=True,
    )
    username = models.CharField(
        validators=[USERNAME_VALIDATOR],
        max_length=MAX_LENGTH_NAME,
        unique=True
    )
    email = models.EmailField(
        unique=True,
        max_length=MAX_LENGTH_EMAIL
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=True
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        blank=True
    )
    confirmation_code = models.CharField(
        max_length=MAX_LENGTH_CONF_CODE,
        default='000000'
    )
    role = models.CharField(
        max_length=30,
        choices=ROLES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_user')
        ]

    def __str__(self):
        return self.username


class Category(models.Model):
    """Модель Категории"""
    SLUG_VALIDATOR = RegexValidator(r'^[-a-zA-Z0-9_]+$')
    name = models.CharField(
        verbose_name='Rатегория',
        max_length=MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        validators=[SLUG_VALIDATOR])

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель Жанры"""
    SLUG_VALIDATOR = RegexValidator(r'^[-a-zA-Z0-9_]+$')
    name = models.CharField(
        verbose_name='Название жанра',
        max_length=MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True,
        validators=[SLUG_VALIDATOR]
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель Произведения"""
    name = models.CharField(
        verbose_name='Название произведения',
        max_length=MAX_LENGTH,
    )
    year = models.IntegerField(
        verbose_name='Год выпуска', )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name="Жанр",
    )
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name='title',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    """Промежуточная модель для реализации отношения многие ко многим"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'date pablished',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.name


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        'date pablished',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Комментарии'

    def __str__(self):
        return self.name
