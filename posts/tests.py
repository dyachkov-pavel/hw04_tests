from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from .models import Post


User = get_user_model()


class TestViewMethods(TestCase):
    def setUp(self):
        self.client = Client()

    def test_profile(self):
        user_1 = User.objects.create(
            username='user_1')
        self.client.force_login(user_1)
        url = reverse('profile', kwargs={'username': user_1.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_authorized(self):
        user_1 = User.objects.create(
            username='user_1')
        self.client.force_login(user_1)
        url = reverse('new_post')
        response = self.client.post(url, {'text': 'text'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_new_post_unauthorized(self):
        url = reverse('new_post')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_pages_contains_new_post(self):
        user_1 = User.objects.create(
            username='user_1')
        self.client.force_login(user_1)
        self.post_1 = Post.objects.create(
            text='test_text',
            author=user_1,
        )
        url_index = reverse('index')
        response_index = self.client.get(url_index)
        self.assertContains(response_index, 'test_text',)
        url_profile = reverse('profile', kwargs={'username': user_1.username})
        response_profile = self.client.get(url_profile)
        self.assertContains(response_profile, 'test_text')
        url_post = reverse(
            'post', kwargs={'username': user_1.username, 'post_id': self.post_1.id})
        response_post = self.client.get(url_post)
        self.assertContains(response_post, 'test_text')

    def test_post_edit(self):
        user_1 = User.objects.create(
            username='user_1')
        self.client.force_login(user_1)
        post_1 = Post.objects.create(
            text='test_text',
            author=user_1,
        )
        url_edit_post = reverse('post_edit',
                                kwargs={
                                    'username': user_1.username,
                                    'post_id': post_1.id}
                                )
        self.client.post(url_edit_post, {'text': 'test_text_updated', })
        edited_post = Post.objects.get(pk=1)
        self.assertEqual(edited_post.text, 'test_text_updated',)
        url_index = reverse('index')
        response_index = self.client.get(url_index)
        self.assertContains(response_index, 'test_text_updated',)
        url_profile = reverse('profile', kwargs={'username': user_1.username})
        response_profile = self.client.get(url_profile)
        self.assertContains(response_profile, 'test_text_updated')
        url_post = reverse(
            'post', kwargs={'username': user_1.username, 'post_id': post_1.id})
        response_post = self.client.get(url_post)
        self.assertContains(response_post, 'test_text_updated')
