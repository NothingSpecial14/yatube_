from urllib.parse import urljoin ,urlencode
import os
import sys
#import django
#BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(BASE_DIR)
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","yatube.settings")
#django.setup()
import unittest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from posts.models import Post, Group, Follow, Comment

class TestUserProfile(TestCase):
    def setUp(self):
        self.client=Client()
        self.username='alexeygavrilov'
        self.password='lexagav14'
        self.user=User.objects.create_user(first_name='Alexey',
                                           last_name='Gavrilov',
                                           username=self.username,
                                           email='lexagav000@ma.il',
                                           password=self.password)
        self.post=Post.objects.create(author=self.user,
                                      text='test post')
    def test_profile_creation(self):
        response=self.client.get(reverse("profile",kwargs={'username':self.username}))
        self.assertEqual(response.status_code, 200)

    def test_post_creation_auth(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        form_data={'text':'test text'}
        self.client.post(reverse('new_post'),urlencode(form_data),content_type='application/x-www-form-urlencoded')
        response=self.client.get(f'/{self.username}/')
        self.assertEqual(response.context['post_count'], 2)

    def test_post_creation_non_auth(self):   
        form_data={'text':'test text'}
        post=self.client.post(reverse('new_post'),urlencode(form_data),content_type='application/x-www-form-urlencoded')
        self.assertRedirects(post, '/auth/login/?next=/auth/new/')
        response=self.client.get(f'/{self.username}/')
        self.assertEqual(response.context['post_count'], 1)

    def test_post_exists(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        form_data={'text':'test text'}
        self.client.post(reverse('new_post'),urlencode(form_data),content_type='application/x-www-form-urlencoded')
        response_profile=self.client.get(f'/{self.username}/')
        self.assertContains(response_profile, 'test text')
        response_index=self.client.get('')
        self.assertContains(response_index, 'test text')
        post_obj=Post.objects.filter(text='test text').last()
        post_id=post_obj.id
        response_post=self.client.get(f'/{self.username}/{post_id}/')
        self.assertContains(response_post, 'test text')

    def test_edited_exists(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        form_data={'text':'test text'}
        self.client.post(reverse('new_post'),urlencode(form_data),content_type='application/x-www-form-urlencoded')
        post_obj=Post.objects.filter(text='test text').last()
        post_id=post_obj.id
        new_form_data={'text':'new text'}
        self.client.post(reverse('post_edit', kwargs={'username':self.username, 'post_id':post_id}),urlencode(new_form_data),content_type='application/x-www-form-urlencoded')
        response_profile=self.client.get(f'/{self.username}/')
        self.assertContains(response_profile, 'new text')
        response_index=self.client.get('')
        self.assertContains(response_index, 'new text')
        response_post=self.client.get(f'/{self.username}/{post_id}/')
        self.assertContains(response_post, 'new text')

    def test_img_on_postpage(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        with open('media/posts/holst.png', 'rb') as img:
            self.client.post(reverse('new_post'), data={'text':'test text',
                                                        'image':img, 
                                                        'author':self.user})
            post=Post.objects.filter(text='test text').last()
            response=self.client.post(reverse('post', kwargs={'username':self.username,
                                                              'post_id':post.id}))
            self.assertContains(response, '<img')


    def test_img_on_pages(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        self.group=Group.objects.create(slug='test_group')
        with open('media/posts/holst.png', 'rb') as img:
            self.client.post(reverse('new_post'), data={'text':'test text',
                                                        'image':img, 
                                                        'author':self.user,
                                                        'groups':self.group.id})
            post=Post.objects.filter(text='test text').last()
            urls=(reverse('post', kwargs={'username':self.username,
                                          'post_id':post.id}),
                  reverse('profile', kwargs={'username':self.username}),
                  reverse('index'))
            for url in urls:
                response=self.client.get(url)
                self.assertContains(response, '<img')
    def test_non_img_file(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        with open('media/posts/3.txt', 'rb') as img:
            post=self.client.post(reverse('new_post'), data={'text':'test text',
                                                        'image':img, 
                                                        'author':self.user})
            self.assertEqual(post.status_code, 200)
            self.assertEqual(Post.objects.count(), 1)

    def test_paginator_on_pages(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password},follow=True)
        self.group=Group.objects.create(slug='test_group')
        self.assertEqual(Group.objects.all().count(), 1)
        for p in range(1,15):
            p=self.client.post(reverse('new_post'), data={'text':'test text', 
                                                        'author':self.user,
                                                        'groups':self.group.id})
        urls=(reverse('profile', kwargs={'username':self.username}),
                  reverse('index'))
                  #reverse('group', kwargs={'slug':'test_group'}))
        for url in urls:
            response=self.client.get(url)
            print(response.context)
            self.assertIn('paginator', response.context)
        


    def test_index_cache(self):
        with self.assertNumQueries(8):
            response=self.client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)
            response=self.client.get(reverse('index'))
            self.assertEqual(response.status_code, 200)

    def test_auth_follow_unfollow(self):
        author=User.objects.create_user(first_name='test',
                                           last_name='aut',
                                           username='testaut',
                                           email='le000@ma.il',
                                           password=self.password)
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        self.assertTrue(self.user.is_authenticated)
        self.client.get(reverse('profile_follow', kwargs={'username':author.username}))
        self.assertEqual(Follow.objects.all().count(), 1)
        self.client.get(reverse('profile_unfollow', kwargs={'username':author.username}))
        self.assertEqual(Follow.objects.all().count(), 0)


    def test_following_post_on_page(self):
        author=User.objects.create_user(first_name='test',
                                           last_name='aut',
                                           username='testaut',
                                           email='le000@ma.il',
                                           password=self.password)
        self.client.post('/auth/login/',{'username':'testaut', 'password':self.password}, follow=True)
        self.assertTrue(author.is_authenticated)
        form_data={'text':'new testtext'}
        self.client.post(reverse('new_post'),urlencode(form_data),content_type='application/x-www-form-urlencoded')
        self.client.logout()
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        self.assertTrue(self.user.is_authenticated)
        self.client.get(reverse('profile_follow', kwargs={'username':author.username}))
        self.assertEqual(Follow.objects.all().count(), 1) 
        response=self.client.get(reverse('follow_index')) 
        self.assertContains(response, 'new testtext')
        self.client.get(reverse('profile_unfollow', kwargs={'username':author.username}))
        new_response=self.client.get(reverse('follow_index')) 
        self.assertNotContains(new_response, 'new testtext')

    def test_comments(self):
        self.client.post('/auth/login/',{'username':self.username, 'password':self.password}, follow=True)
        self.assertEqual(Comment.objects.all().count(), 0)
        url=self.client.post(reverse('add_comment', kwargs={'username':self.username, 'post_id':self.post.id}))
        data={'text':'new testtext'}
        self.client.post(url, data)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.client.logout()
        url=self.client.post(reverse('add_comment', kwargs={'username':self.username, 'post_id':self.post.id}))
        data={'text':'new testtext2'}
        self.client.post(url, data)
        self.assertEqual(Comment.objects.all().count(), 1)



        