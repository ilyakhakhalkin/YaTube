from urllib import response
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post, User


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='subscriber1')
        cls.user2 = User.objects.create_user(username='subscriber2')
        cls.post = Post.objects.create(text='Текст поста',
                                       author=cls.user_author,)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def follow_author(self, author, user):
        temp_auth_client = Client()
        temp_auth_client.force_login(user)

        return temp_auth_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': author.username}
            )
        )

    def test_follow(self):
        """Проверка подписок"""

        self.follow_author(author=self.user_author, user=self.user)

        self.assertTrue(
            Follow.objects.filter(
                author=self.user_author,
                user=self.user
            ).exists()
        )

        count = Follow.objects.filter(
            author=self.user_author,
            user=self.user
        ).count()

        self.follow_author(author=self.user_author, user=self.user)

        should_be_the_same_count = Follow.objects.filter(
            author=self.user_author,
            user=self.user,
        ).count()

        self.assertEquals(count, should_be_the_same_count)

    def test_follow_index_context(self):
        """Проверка содержимого страницы с подписками"""

        Follow.objects.create(author=self.user_author, user=self.user)
        response = self.authorized_client.get('/follow/')
        self.assertEquals(
            response.context['page_obj'][0].author,
            self.user_author
        )

    def test_unfollow(self):
        """Проверка отписок"""

        Follow.objects.create(
            author=self.user_author,
            user=self.user,
        )

        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_author,
            ).exists()
        )

        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_author}
            )
        )

        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_author,
            ).exists()
        )

    def test_new_post_for_subscribers(self):
        """Проверка выдачи нового поста подписчикам"""

        self.follow_author(author=self.user_author, user=self.user)
        self.follow_author(author=self.user_author, user=self.user2)

        new_post = Post.objects.create(text='пост для подписчиков',
                                       author=self.user_author)

        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEquals(response.context['page_obj'][0].id, new_post.id)

        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEquals(response.context['page_obj'][0].id, new_post.id)

    def test_no_subscription_no_post(self):
        """Проверка - без подписки нет поста в ленте"""

        new_post = Post.objects.create(text='пост для подписчиков',
                                       author=self.user_author)

        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )

        self.assertNotIn(new_post, response.context['page_obj'])

        self.authorized_client.force_login(self.user2)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )

        self.assertNotIn(new_post, response.context['page_obj'])
