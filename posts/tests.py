from django import template
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls.base import reverse
from .models import Post, Group


User = get_user_model()


class TestViewMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.unauthorized_client = Client()
        self.user = User.objects.create(username='user')
        self.client.force_login(self.user)
        self.group_1 = Group.objects.create(
            title='test_title',
            slug='test_slug'
        )
        self.original_text = 'test_text'

    def test_profile(self):
        url = reverse('profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_authorized(self):
        url = reverse('new_post')
        self.client.post(
            url, {'text': self.original_text, 'group': self.group_1.id})
        post = Post.objects.first()
        self.assertEqual(self.original_text, post.text)
        self.assertEqual(self.user, post.author)
        self.assertEqual(self.group_1.title, post.group.title)
        self.assertEqual(Post.objects.all().count(), 1)

    def test_new_post_unauthorized(self):
        url = reverse('new_post')
        response = self.unauthorized_client.get(url)
        url_redirect = reverse('login') + '?next=' + reverse('new_post')
        self.assertEqual(Post.objects.count(), 0)
        self.assertRedirects(response, url_redirect)

    def check_posts(self, url, post, user):
        response = self.client.get(url)
        if 'page' in response.context:
            response_post = response.context['page'][0]
        else:
            response_post = response.context['post']
        self.assertEqual(response_post, post)
        self.assertEqual(response_post.author, user)
        self.assertEqual(response_post.group.title, post.group.title)

    def test_pages_contains_new_post(self):
        post_1 = Post.objects.create(
            text=self.original_text,
            author=self.user,
            group=self.group_1
        )
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={
                    'username': self.user.username, 'post_id': post_1.id}),
            reverse('group_posts', kwargs={'slug': self.group_1.slug})
        ]
        for url in urls:
            self.check_posts(url, post_1, self.user)

    def test_post_edit(self):
        post_1 = Post.objects.create(
            text=self.original_text,
            author=self.user,
            group=self.group_1
        )
        group_2 = Group.objects.create(
            title='test_title2',
            slug='test_slug2'
        )
        url_edit_post = reverse('post_edit',
                                kwargs={
                                    'username': self.user.username,
                                    'post_id': post_1.id}
                                )
        self.client.post(
            url_edit_post, {'text': 'test_text_updated', 'group': group_2.id})
        edited_post = Post.objects.last()
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={
                    'username': self.user.username, 'post_id': post_1.id}),
            reverse('group_posts', kwargs={'slug': group_2.slug}),
        ]
        for url in urls:
            self.check_posts(url, edited_post, self.user)
        response = self.client.get(
            reverse('group_posts', kwargs={'slug': self.group_1.slug}))
        self.assertEqual(response.context['paginator'].object_list.count(), 0)

    def test_page_not_found(self):
        url_not_found = '/unknown_adress/22123/'
        response = self.client.get(url_not_found)
        self.assertEqual(response.status_code, 404)
