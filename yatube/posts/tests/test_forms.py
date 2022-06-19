from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from http import HTTPStatus
import shutil
import tempfile

from .create_image import create_image
from ..models import Comment, Post, Group, User


MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class FormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.user_not_author = User.objects.create_user(username='not_author')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='testslug'
        )

        cls.group2 = Group.objects.create(
            title='Вторая Тестовая Группа',
            description='Тестовое описание второй группы',
            slug='testslug2'
        )

        cls.post = Post.objects.create(
            text='Новый пост',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        shutil.rmtree(settings.TEST_MEDIA_ROOT, ignore_errors=True)

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.guest_client = Client()
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.user_not_author)

    def tearDown(self):
        shutil.rmtree(settings.TEST_MEDIA_ROOT, ignore_errors=True)

        return super().tearDown()

    def test_create_post(self):
        """Создание поста при отправке валидной формы"""

        self.uploaded = create_image()

        form_data = {
            'text': 'Новый пост221321',
            'group': self.group.id,
            'image': self.uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.user,
                image=f'posts/{self.uploaded}'
            ).exists()
        )

    def test_create_post_no_group(self):
        """Создание поста при отправке валидной формы без группы"""

        form_data = {
            'text': 'Новый пост',
        }

        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )

        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=None,
            ).exists()
        )

    def test_update_post_new_group_authorized(self):
        """Изменение поста при отправке валидной формы"""

        count = Post.objects.count()
        old_post = Post.objects.get(pk=self.post.id)

        form_data = {
            'text': f'{self.post.text} UPDATED',
            'group': self.group2.id,
        }

        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )

        self.assertEquals(Post.objects.count(), count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=old_post.author,
                created=old_post.created,
                id=self.post.id,
            ).exists()
        )

    def test_update_post_keep_group_authorized(self):
        """Изменение поста при отправке валидной формы
        Группа не изменена"""

        count = Post.objects.count()
        old_post = Post.objects.get(pk=self.post.id)

        form_data = {
            'text': f'{self.post.text} UPDATED',
            'group': self.group.id,
        }

        self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )

        self.assertEquals(Post.objects.count(), count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=old_post.author,
                created=old_post.created,
                id=old_post.id,
            ).exists()
        )

    def test_update_post_not_author(self):
        """Изменение поста авторизованным пользователем, не автором"""

        count = Post.objects.count()
        old_post = Post.objects.get(pk=self.post.id)

        form_data = {
            'text': 'Мне нельзя но попробую',
            'group': self.group2.id,
        }

        response = self.authorized_not_author.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )

        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )

        self.assertEquals(Post.objects.count(), count)

        self.assertTrue(
            Post.objects.filter(
                text=old_post.text,
                group=old_post.group,
                author=old_post.author,
                created=old_post.created,
                id=old_post.id,
            ).exists()
        )

    def test_update_post_guest(self):
        """Изменение поста неавторизованным пользователем"""

        count = Post.objects.count()
        old_post = Post.objects.get(pk=self.post.id)

        form_data = {
            'text': 'Мне нельзя но попробую',
            'group': self.group2.id,
        }

        response = self.guest_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )

        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

        self.assertEquals(Post.objects.count(), count)

        self.assertTrue(
            Post.objects.filter(
                text=old_post.text,
                group=old_post.group,
                author=old_post.author,
                created=old_post.created,
                id=old_post.id,
            ).exists()
        )
    
    def test_comment_form_authorized(self):
        """Проверка формы комментария, пользователь авторизован"""

        form_data = {
            'text': 'тестовый коммент'
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
        )

        self.assertTrue(Comment.objects.filter(
                post=self.post,
                author=self.user,
                text=form_data['text'],
            ).exists()
        )

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
    
    def test_comment_form_guest(self):
        """Проверка формы комментария, гостевой пользователь"""

        form_data = {
            'text': 'тестовый коммент'
        }

        response = self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
        )

        self.assertFalse(Comment.objects.filter(
                post=self.post,
                author=self.user,
                text=form_data['text'],
            ).exists()
        )

        self.assertEquals(response.status_code, HTTPStatus.FOUND)
