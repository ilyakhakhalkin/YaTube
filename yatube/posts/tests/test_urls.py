from http import HTTPStatus
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Post, Group, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Author777')
        cls.user2 = User.objects.create_user(username='Not_author')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{PostsURLTests.group.pk}/': 'posts/post_detail.html',
            f'/posts/{PostsURLTests.group.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_access_guest(self):
        """Проверка доступа гостя"""

        url_access = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.FOUND,
            '/unexisting-page/': HTTPStatus.NOT_FOUND,
        }

        for url, access in url_access.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEquals(response.status_code, access)

    def test_url_access_not_author(self):
        """Проверка доступа не-автора"""

        self.authorized_client.force_login(self.user2)

        url_access = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.user2.username}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/unexisting-page/': HTTPStatus.NOT_FOUND,
        }

        for url, access in url_access.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEquals(response.status_code, access)

    def test_url_access_author(self):
        """Проверка доступа автора"""

        self.authorized_client.force_login(self.user)

        url_access = {
            '/': HTTPStatus.OK,
            '/group/test-slug/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostsURLTests.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/unexisting-page/': HTTPStatus.NOT_FOUND,
        }

        for url, access in url_access.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEquals(response.status_code, access)

    def test_redirects(self):
        url_redirects = {
            f'/posts/{self.post.id}/edit/':
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }

        for url, redirect_url in url_redirects.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
