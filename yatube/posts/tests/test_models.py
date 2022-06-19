from attr import field
from django.conf import settings
from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


def compare_verboses(self, expected, model_obj):
    for field, expected_value in expected.items():
            with self.subTest(field=field):
                self.assertEqual(
                    model_obj._meta.get_field(field).verbose_name,
                    expected_value
                )


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')

        cls.post = Post.objects.create(
            text='Testing text field /  Тестирование поля с текстом',
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        current_post_name = str(self.post)
        required_post_name = (
            self.post.text[:settings.POST_TEXT_SYMB_TO_DISPLAY_COUNT]
        )

        self.assertEquals(current_post_name, required_post_name)

    def test_post_model_verbose_names(self):
        """Проверка verbose name полей модели Post """

        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }

        compare_verboses(self, field_verboses, self.post)

    def test_post_model_help_text(self):
        """Проверка help text полей модели Post"""

        field_help_textes = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }

        for field, expected_value in field_help_textes.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание', 
            slug='Тестовый слаг',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""

        currend_group_name = str(self.group)
        required_group_name = self.group.title
        self.assertEquals(currend_group_name, required_group_name)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='tester')

        cls.post = Post.objects.create(
            text='Testing text field /  Тестирование поля с текстом',
            author=cls.user,
        )

        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.user,
            post=cls.post,
        )

    def test_comment_model_verbose_names(self):
        """Проверка verbose name полей модели Comment """

        field_verboses = {
            'post': 'Публикация',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }

        compare_verboses(self, field_verboses, self.comment)

    def test_comment_model_help_text(self):
        """Проверка help text полей модели Comment"""

        field_help_textes = {
            'text': 'Введите текст комментария',
        }

        self.assertEqual(
            self.comment._meta.get_field('text').help_text, 
            field_help_textes['text']
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.follower = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='author')

        cls.follow_entry = Follow.objects.create(
            user=cls.follower,
            author=cls.author,
        )

    def test_follow_model_verbose_names(self):
        """Проверка verbose name полей модели Follow"""

        field_verboses = {
            'author': 'Автор',
            'user': 'Подписчик',
        }

        compare_verboses(self, field_verboses, self.follow_entry)
