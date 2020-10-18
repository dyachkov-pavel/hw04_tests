from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from .models import Post, Group


User = get_user_model()


class TestViewMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_1 = User.objects.create(username='user_1')
        self.client.force_login(self.user_1)

    def test_profile(self):
        url = reverse('profile', kwargs={'username': self.user_1.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_authorized(self):
        url = reverse('new_post')
        self.client.post(url, {'text': 'text'})
        post = Post.objects.get(pk=1)
        self.assertEqual('text', post.text)
        self.assertEqual('user_1', post.author.username)

    def test_new_post_unauthorized(self):
        self.unauthorized_client = Client()
        url = reverse('new_post')
        response = self.unauthorized_client.get(url)
        posts = Post.objects.all()
        url_redirect = reverse('login') + '?next=' + reverse('new_post')
        self.assertEqual(len(posts), 0)
        self.assertRedirects(response, url_redirect)

    def test_pages_contains_new_post(self):
        self.post_1 = Post.objects.create(
            text='test_text',
            author=self.user_1,
        )
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user_1.username}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(
                response.context['page'].object_list[0].text, 'test_text',)
            self.assertEqual(
                response.context['page'].object_list[0].author.username, 'user_1',)
        url_post = reverse(
            'post', kwargs={'username': self.user_1.username, 'post_id': self.post_1.id})
        response_post = self.client.get(url_post)
        self.assertEqual(response_post.context['post'].text, 'test_text')

    def test_post_edit(self):
        group_1 = Group.objects.create(
            title='test_title',
            slug='test_slug'
        )
        group_2 = Group.objects.create(
            title='test_title2',
            slug='test_slug2'
        )
        post_1 = Post.objects.create(
            text='test_text',
            author=self.user_1,
            group=group_1
        )
        url_edit_post = reverse('post_edit',
                                kwargs={
                                    'username': self.user_1.username,
                                    'post_id': post_1.id}
                                )
        self.client.post(
            url_edit_post, {'text': 'test_text_updated', 'group': group_2.id})
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user_1.username}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(
                response.context['page'].object_list[0].text, 'test_text_updated',)
            self.assertEqual(
                response.context['page'].object_list[0].group.title, 'test_title2',)
        url_post = reverse(
            'post', kwargs={'username': self.user_1.username, 'post_id': post_1.id})
        response_post = self.client.get(url_post)
        self.assertEqual(
            response_post.context['post'].text, 'test_text_updated')
        self.assertEqual(
            response_post.context['post'].group.title, 'test_title2')

    def test_page_not_found(self):
        url_not_found = '/unknown_adress/22123/'
        response = self.client.get(url_not_found)
        self.assertEqual(response.status_code, 404)
