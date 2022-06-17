from django.conf import settings
from django.test import TestCase

from ..models import Group, Post, User


class PostsModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг'
        )

        cls.post = Post.objects.create(
            text='Testing text field /  Тестирование поля с текстом',
            author=cls.user,
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        current_post_name = str(self.post)
        required_post_name = (
            self.post.text[:settings.POST_TEXT_SYMB_TO_DISPLAY_COUNT]
        )
        self.assertEquals(current_post_name, required_post_name)

    def test_post_model_verbose_names(self):
        """Проверка verbose names полей модели Post """

        post = PostsModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_model_help_text(self):
        """Проверка help text полей модели Post"""

        post = PostsModelTest.post
        field_help_textes = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, expected_value in field_help_textes.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='Тестовый слаг'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        currend_group_name = str(self.group)
        required_group_name = self.group.title
        self.assertEquals(currend_group_name, required_group_name)
