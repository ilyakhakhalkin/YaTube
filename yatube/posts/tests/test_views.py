from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.test import override_settings
import shutil
from django.core.cache import cache

from ..models import Post, Group, User
from .create_image import create_image

PAGINATOR_ALL_POSTS_COUNT = 13


@override_settings(MEDIA_ROOT=(settings.TEST_MEDIA_ROOT + '/media'))
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.user2 = User.objects.create_user(username='tester2')
        cls.post_list1 = []
        cls.post_list2 = []

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='testslug'
        )

        cls.group2 = Group.objects.create(
            title='Другая тестовая группа',
            description='раз два раз проверка',
            slug='second-test-slug'
        )

        cls.post_list2 = Post.objects.bulk_create([
            Post(
                text=f'Текст поста #{i + 1}',
                author=cls.user2,
                group=cls.group2,
            ) for i in range(settings.POSTS_AMOUNT)
        ])

        cls.post_list1 = Post.objects.bulk_create([
            Post(
                text=f'Текст поста #{i + 11}',
                author=cls.user,
                group=cls.group,
            ) for i in range(settings.POSTS_AMOUNT)
        ])

        cls.post_list1 = cls.post_list1[::-1]
        cls.post_list2 = cls.post_list2[::-1]

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user2)

    def tearDown(self):
        cache.clear()
        try:
            shutil.rmtree(settings.TEST_MEDIA_ROOT)
        except OSError:
            pass

        return super().tearDown()

    def test_pages_use_correct_template(self):
        """Проверка namespace:name"""

        templates_url_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse
            (
                'posts:group_list',
                kwargs={'slug': PostsPagesTests.group.slug}
            ):
                'posts/group_list.html',
            reverse
            (
                'posts:profile',
                kwargs={'username': PostsPagesTests.user}
            ):
                'posts/profile.html',
            reverse
            (
                'posts:post_detail',
                kwargs={'post_id': PostsPagesTests.group.pk}
            ):
                'posts/post_detail.html',
            reverse
            (
                'posts:post_edit',
                kwargs={'post_id': PostsPagesTests.group.pk}
            ):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:follow_index'):
                'posts/follow.html',
        }

        for reverse_name, template in templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_post_lists(self, res_posts, db_posts):
        """Принимает на вход два списка постов и сравнивает их поля"""

        for obj_num in range(len(res_posts)):
            self.assertEquals(
                res_posts[obj_num].group,
                db_posts[obj_num].group
            )

            self.assertEquals(
                res_posts[obj_num].text,
                db_posts[obj_num].text
            )

            self.assertEquals(
                res_posts[obj_num].author,
                db_posts[obj_num].author
            )

    def test_index_page_show_correct_context(self):
        """Проверка контекста страницы index"""

        response = self.authorized_client.get(reverse('posts:index'))
        self.assert_post_lists(response.context['page_obj'], self.post_list1)

    def test_group_list_page_show_correct_context(self):
        """Проверка контекста страницы group_list,
        отфильтрованного по группе
        """

        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group2.slug}
            )
        )

        self.assert_post_lists(response.context['page_obj'], self.post_list2)

    def test_profile_page_show_correct_context(self):
        """Проверка контекста страницы profile,
        отфильтрованного по пользователю"""

        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user2.username}
            )
        )

        self.assert_post_lists(response.context['page_obj'], self.post_list2)

    def test_post_detail_page_show_correct_context(self):
        """Проверка контекста страницы поста"""

        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}
            )
        )

        self.assert_post_lists(
            [response.context['post']],
            [self.post_list2[settings.POSTS_AMOUNT - 1]]
        )

    def test_edit_post_page_show_correct_context(self):
        """Проверка формы редактирования поста"""

        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 1}
            )
        )

        form_expected_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_expected_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertTrue(response.context['is_edit'])

    def test_create_post_page_show_correct_context(self):
        """Проверка формы создания поста"""

        response = self.authorized_client.get(
            reverse('posts:post_create')
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_goes_everywhere(self):
        """Создание нового поста и проверка страниц на его наличие"""
        new_post = Post.objects.create(text='Новый пост',
                                       author=self.user,
                                       group=self.group
                                       )

        url_list = {
            '/',
            '/group/testslug/',
            '/profile/tester/',
        }

        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                response = response.context['page_obj'][0]
                self.assertEquals(response.text, new_post.text)
                self.assertEquals(response.author, new_post.author)
                self.assertEquals(response.group, new_post.group)

    def test_new_post_is_not_in_another_group(self):
        """Проверка другой группы на отсутствие нового поста"""

        new_post = Post.objects.create(text='Новый пост',
                                       author=self.user,
                                       group=self.group
                                       )

        response = self.authorized_client.get('/group/second-test-slug/')
        self.assertNotIn(response.context['page_obj'], [new_post])

    def test_images_in_context(self):
        """Проверка вывода изображений"""

        uploaded_image = create_image()

        new_post = Post.objects.create(
            text='Новый пост с картинкой',
            author=self.user,
            group=self.group,
            image=uploaded_image,
        )

        urls_with_pics_list = (
            reverse('posts:index'),
            reverse
            (
                'posts:profile',
                kwargs={'username': new_post.author}
            ),
            reverse
            (
                'posts:group_list',
                kwargs={'slug': new_post.group.slug}
            )
        )

        for url in urls_with_pics_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEquals(
                    response.context['page_obj'][0].image,
                    new_post.image
                )

        response = self.authorized_client.get(f'/posts/{new_post.id}/')
        self.assertEquals(response.context['post'].image, new_post.image)

    def test_comments_authorized(self):
        """Публикация комментария авторизированным пользователем"""
        comment = {
            'text': 'test comment',
        }

        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': 1}
            ), comment
        )

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEquals(
            response.context['comments'][0].text,
            comment['text']
        )
        self.assertEquals(response.context['comments'][0].author, self.user2)

        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_cache(self):
        """Тест кеша главной страницы"""

        # response =
        self.authorized_client.get(
            reverse('posts:index')
        )

        Post.objects.create(
            text='Новый пост',
            author=self.user,
        )

        # response2 =
        self.authorized_client.get(
            reverse('posts:index')
        )
        # self.assertEquals(response.content, response2.content)

        cache.clear()
        # response3 =
        self.authorized_client.get(
            reverse('posts:index')
        )
        # self.assertNotEquals(response2.content, response3.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.post_list = []

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='testslug'
        )

        for i in range(PAGINATOR_ALL_POSTS_COUNT):
            cls.post_list.append(
                Post.objects.create(
                    text=f'Текст поста #{i + 1}',
                    author=cls.user,
                    group=cls.group
                )
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Тестируем paginator: 10 записей на первой странице, 3 на второй"""
        url_list = (
            '/',
            '/group/testslug/',
            '/profile/tester/',
        )

        for url in url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_AMOUNT
                )

                response = self.authorized_client.get(f'{url}?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    PAGINATOR_ALL_POSTS_COUNT - settings.POSTS_AMOUNT
                )
