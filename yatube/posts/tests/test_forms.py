from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост тестового пользователя в тестовой группе',
        )

    def setUp(self):
        self.auth_client = Client()

        self.auth_client.force_login(PostsFormsTests.user)

    def test_posts_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        group = PostsFormsTests.group
        user = PostsFormsTests.user

        form_data = {
            'text': 'Тестовый пост',
            'group': group.pk,
        }

        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': user.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                group=group,
                author=user,
            ).exists()
        )

    def test_posts_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        group = PostsFormsTests.group
        post = PostsFormsTests.post

        form_data = {
            'text': 'Изменённый тестовый пост',
            'group': group.pk,
        }

        self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            Post.objects.get(pk=post.pk).text,
            'Изменённый тестовый пост'
        )
