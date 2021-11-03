from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()

        self.auth_client.force_login(UsersURLTests.user)

    def test_urls_exists_at_desired_location(self):
        """Проверяем доступность страниц приложения Users."""

        url_names = [
            '/auth/login/',
            '/auth/signup/',
            '/auth/password_change/',
            '/auth/password_reset/',
            '/auth/logout/',
        ]

        for adress in url_names:
            with self.subTest(adress=adress):
                guest_response = self.guest_client.get(adress, follow=True)
                auth_response = self.auth_client.get(adress)

                if adress == '/auth/password_change/':
                    self.assertRedirects(
                        guest_response,
                        f'{"/auth/login/?next=/auth/password_change/"}'
                    )
                    self.assertEqual(auth_response.reason_phrase, 'OK')

                self.assertEqual(guest_response.reason_phrase, 'OK')
                self.assertEqual(auth_response.reason_phrase, 'OK')

    def test_urls_uses_correct_template(self):
        """Проверяем шаблоны приложения Users."""

        url_templates_names = {
            '/auth/login/': 'users/login.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for adress, template in url_templates_names.items():
            with self.subTest(adress=adress):
                response = self.auth_client.get(adress)
                self.assertTemplateUsed(response, template)
