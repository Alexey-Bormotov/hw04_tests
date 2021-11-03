from time import sleep

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug2',
            description='Тестовое описание 2',
        )

        for i in range(12):
            Post.objects.create(
                author=cls.user,
                group=cls.group2,
                text=f'Тестовый пост №{i+1} тестового '
                     f'пользователя в тестовой группе 2',
            )
            # Без sleep посты слишком быстро создаются и их сортировка
            # по дате беспорядочна при каждом новом запуске тестов.
            # Этот костыль оправдан или есть другое решение?!
            sleep(0.01)

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text=f'{"Тестовый пост №13 тестового"}'
                 f' пользователя в тестовой группе',
        )

    def setUp(self):
        self.auth_client = Client()

        self.auth_client.force_login(PostsViewsTests.user)

    def test_posts_pages_uses_correct_templates(self):
        """URL-адреса используют соответствующие шаблоны в приложении Posts."""
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}
            ): 'posts/create_post.html',
        }

        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Не знаю, правильно ли я сделал нижеследующий тест,
    # но ощущения такие, будто достал шляпу из кролика :)
    # P.S. Ни один кролик при тестах не пострадал.
    def test_posts_pages_show_correct_contexts(self):
        """Проверка правильности контекстов страниц приложения Posts."""
        group = PostsViewsTests.group
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        pages_contexts_names = {
            reverse('posts:index'): ('page_obj',),
            reverse(
                'posts:group_posts',
                kwargs={'slug': group.slug}
            ): ('page_obj', 'group'),
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ): ('page_obj', 'author', 'posts_count'),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.pk}
            ): ('post', 'posts_count'),
            reverse('posts:post_create'): ('form',),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.pk}
            ): ('form', 'post_id'),
        }

        for reverse_name, context in pages_contexts_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)

                for context_obj in context:
                    if context_obj == 'page_obj':
                        context_post = response.context['page_obj'][0]
                        post_author = context_post.author.username
                        post_group = context_post.group.title
                        post_text = context_post.text

                        self.assertEqual(post_author, 'test_user')
                        self.assertEqual(post_group, 'Тестовая группа')
                        self.assertEqual(
                            post_text,
                            ('Тестовый пост №13 тестового пользователя'
                             ' в тестовой группе')
                        )
                        continue

                    if context_obj == 'group':
                        context_group = response.context['group'].title

                        self.assertEqual(context_group, 'Тестовая группа')
                        continue

                    if context_obj == 'author':
                        context_author = response.context['author'].username

                        self.assertEqual(context_author, 'test_user')
                        continue

                    if context_obj == 'posts_count':
                        context_posts_count = response.context['posts_count']

                        self.assertEqual(context_posts_count, 13)
                        continue

                    if context_obj == 'post':
                        context_post = response.context['post']
                        post_author = context_post.author.username
                        post_group = context_post.group.title
                        post_text = context_post.text

                        self.assertEqual(post_author, 'test_user')
                        self.assertEqual(post_group, 'Тестовая группа')
                        self.assertEqual(
                            post_text,
                            'Тестовый пост №13 тестового пользователя'
                            ' в тестовой группе'
                        )
                        continue

                    if context_obj == 'form':
                        form_fields = {
                            'text': forms.fields.CharField,
                            'group': forms.fields.ChoiceField,
                        }

                        for value, expected in form_fields.items():
                            with self.subTest(value=value):
                                form_field = (
                                    response.context.get('form').
                                    fields.get(value)
                                )
                                self.assertIsInstance(form_field, expected)
                        continue

                    if context_obj == 'post_id':
                        context_post_id = response.context['post_id']

                        self.assertEqual(context_post_id, 13)

    def test_posts_pages_correct_paginator_work(self):
        """Проверка работы паджинатора в шаблонах приложения Posts."""
        group = PostsViewsTests.group2
        user = PostsViewsTests.user

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        ]

        for page in pages_names:
            with self.subTest(page=page):
                response_page_1 = self.auth_client.get(page)
                response_page_2 = self.auth_client.get(page + '?page=2')
                self.assertEqual(len(response_page_1.context['page_obj']), 10)

                if page == '/group/test-slug2/':
                    self.assertEqual(
                        len(response_page_2.context['page_obj']), 2
                    )
                    continue

                self.assertEqual(len(response_page_2.context['page_obj']), 3)

    def test_posts_post_correct_creation(self):
        """Проверка, что созданный пост появляется только
        на нужных страницах."""
        group = PostsViewsTests.group
        group2 = PostsViewsTests.group2
        user = PostsViewsTests.user
        post = PostsViewsTests.post

        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': group.slug}),
            reverse('posts:group_posts', kwargs={'slug': group2.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        ]

        for page in pages_names:
            with self.subTest(page=page):
                response = self.auth_client.get(page)
                context_post = response.context['page_obj'][0]

                if page == '/group/test-slug2/':
                    self.assertNotEqual(context_post, post)
                    continue

                self.assertEqual(context_post, post)
