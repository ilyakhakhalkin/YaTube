from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        verbose_name='Адрес группы',
        unique=True,
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
        blank=False,
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.text[:settings.POST_TEXT_SYMB_TO_DISPLAY_COUNT]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
        blank=False,
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарии'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = ('Подписки')
        verbose_name_plural = ('Подписки')

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='user_cannot_be_equal_author'
            ),
        ]

    def __str__(self):
        return self.name
