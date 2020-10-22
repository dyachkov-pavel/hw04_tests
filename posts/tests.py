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
        self.user_1 = User.objects.create(username='user_1')
        self.client.force_login(self.user_1)
        self.group_1 = Group.objects.create(
            title='test_title',
            slug='test_slug'
        )
        self.group_2 = Group.objects.create(
            title='test_title2',
            slug='test_slug2'
        )
        self.original_text = 'test_text'
        self.post_1 = Post.objects.create(
            text=self.original_text,
            author=self.user_1,
            group=self.group_1
        )

    def test_profile(self):
        url = reverse('profile', kwargs={'username': self.user_1.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_new_post_authorized(self):
        url = reverse('new_post')
        self.client.post(
            url, {'text': self.original_text, 'group': self.group_1.id})
        post = Post.objects.first()
        self.assertEqual(self.original_text, post.text)
        self.assertEqual(self.user_1.username, post.author.username)
        self.assertEqual(self.group_1.title, post.group.title)

    def test_new_post_unauthorized(self):
        url = reverse('new_post')
        response = self.unauthorized_client.get(url)
        url_redirect = reverse('login') + '?next=' + reverse('new_post')
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(response, url_redirect)

    def check_posts(self, urls, post, user):
        for url in urls:
            response = self.client.get(url)
            if 'page' in response.context:
                self.assertEqual(
                    response.context['page'].object_list[0].text, post.text)
                self.assertEqual(
                    response.context['page'].object_list[0].author.username, user.username)
                self.assertEqual(
                    response.context['page'].object_list[0].group.title, post.group.title)
            else:
                self.assertEqual(
                    response.context['post'].text, post.text)
                self.assertEqual(
                    response.context['post'].author.username, user.username)
                self.assertEqual(
                    response.context['post'].group.title, post.group.title)

    def test_pages_contains_new_post(self):
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user_1.username}),
            reverse('post', kwargs={
                    'username': self.user_1.username, 'post_id': self.post_1.id}),
            reverse('group_posts', kwargs={'slug': self.group_1.slug})
        ]
        self.check_posts(urls, self.post_1, self.user_1)

    def test_post_edit(self):
        url_edit_post = reverse('post_edit',
                                kwargs={
                                    'username': self.user_1.username,
                                    'post_id': self.post_1.id}
                                )
        self.client.post(
            url_edit_post, {'text': 'test_text_updated', 'group': self.group_2.id})
        edited_post = Post.objects.last()
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': self.user_1.username}),
            reverse('post', kwargs={
                    'username': self.user_1.username, 'post_id': self.post_1.id}),
            reverse('group_posts', kwargs={'slug': self.group_2.slug}),
        ]
        self.check_posts(urls, edited_post, self.user_1)
        response = self.client.get(
            reverse('group_posts', kwargs={'slug': self.group_1.slug}))
        self.assertEqual(len(response.context['posts']), 0,)

    def test_page_not_found(self):
        url_not_found = '/unknown_adress/22123/'
        response = self.client.get(url_not_found)
        self.assertEqual(response.status_code, 404)


'''
class TestImg(TestCase):
    def SetUp(self):
        self.client = Client()
        self.user_1 = User.objects.create(username='user_1')
        self.client.force_login(self.user_1)
        

    def test_img_tag(self):
        with open('media/posts/alucard.jpg','rb') as img:
            self.client.post("<username>/<int:post_id>/edit/", 
                            {'author': self.user_1, 
                            'text': 'post with image', 
                            'image': img}
                            )
        created_post = Post.objects.get(pk=1)
        self.assertEqual(created_post.text, 'post with image')
        # response = self.client.get(reverse('index'))
        # self.assertContains(response, '<img')
'''
