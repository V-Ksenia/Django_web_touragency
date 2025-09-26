from django.test import TestCase, Client
from django.urls import reverse
from .models import Tour, Promocode, Order
from .forms import OrderForm
from django.contrib.auth.models import User
from touragency.views import *


class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="name")
        self.hotel = Hotel.objects.create(name="hotel", stars=5, country_id=1, price_per_night=100)
        self.user_client = User.objects.create_user(username='client', password='password', status='client', phone_number = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)
        self.user_staff = User.objects.create_user(username='staff', password='password', status='staff', phone_number = "+375(29)1214223", first_name = "Afjdfj", last_name="Hjhxd", address = "ul.shjhds132", age=20)
        self.tour = Tour.objects.create(name='Test Tour', trips=10, price=100, country_id=1, hotel_id=1, duration=2)
        self.promocode = Promocode.objects.create(code='TEST123', discount=10)

    def test_get_auth_client_tour_exists(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('create_order', kwargs={'pk': self.tour.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_create_form.html')

    def test_get_auth_client_tour_nonexist(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('create_order', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_get_auth_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('create_order', kwargs={'pk': self.tour.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_unauth(self):
        response = self.client.get(reverse('create_order', kwargs={'pk': self.tour.pk}))
        self.assertEqual(response.status_code, 404) 

    def test_post_auth_client_valid_data(self):
        self.client.force_login(self.user_client)
        data = {'amount': 2,
            'departure_date': '2024-07-01',
            'promocode': 'TEST123'}
        response = self.client.post(reverse('create_order', kwargs={'pk': self.tour.pk}), data)
        self.assertEqual(response.status_code, 302)  

    def test_post_auth_client_invalid_data(self):
        self.client.force_login(self.user_client)
        data = {'amount': 20,  
            'departure_date': '2024-05-01',
            'promocode': 'TEST123'
        }
        response = self.client.post(reverse('create_order', kwargs={'pk': self.tour.pk}), data)
        self.assertEqual(response.status_code, 200) 

    def test_post_auth_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.post(reverse('create_order', kwargs={'pk': self.tour.pk}))
        self.assertEqual(response.status_code, 404)

    def test_post_unauth(self):
        response = self.client.post(reverse('create_order', kwargs={'pk': self.tour.pk}))
        self.assertEqual(response.status_code, 200) 


class SpecificOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country = Country.objects.create(name="name")
        self.hotel = Hotel.objects.create(name="hotel", stars=5, country_id=1, price_per_night=100)
        self.tour = Tour.objects.create(name='Test Tour', trips=10, price=100, country_id=1, hotel_id=1, duration=2)
        self.user = User.objects.create(username='client', password='password', status='client', phone_number = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)
        self.order = Order.objects.create(number=1, amount=2, price=200, departure_date='2024-06-01', user_id=self.user.id, tour_id=self.tour.id)

    def test_get_auth_user_and_order_exists(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': self.order.number}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_delete_form.html')

    def test_get_auth_user_and_order_nonexist(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_get_unauth(self):
        response = self.client.get(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': self.order.number}))
        self.assertEqual(response.status_code, 404)  

    def test_post_auth_user_and_order_exists_invalid_data(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': self.order.number}), {'confirm': True})
        self.assertEqual(response.status_code, 404)  

    def test_post_auth_user_and_order_nonexist(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': 999}), {'confirm': True})
        self.assertEqual(response.status_code, 404)

    def test_post_unauth(self):
        response = self.client.post(reverse('user_spec_order', kwargs={'pk': self.user.pk, 'jk': self.order.number}), {'confirm': True})
        self.assertEqual(response.status_code, 404)  


class ReviewCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='client', password='password', status='client', phone_number = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)

    def test_get_auth_client(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('add_review'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_create_form.html')

    def test_get_unauth(self):
        response = self.client.get(reverse('add_review'))
        self.assertEqual(response.status_code, 302)

    def test_post_auth_client_valid_data(self):
        self.client.force_login(self.user_client)
        data = {'title': 'Test Review', 'rating': 5, 'text': 'This is a test review.'}
        response = self.client.post(reverse('add_review'), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Review.objects.filter(title='Test Review').exists())

    def test_post_auth_client_invalid_data(self):
        self.client.force_login(self.user_client)
        data = {'title': 'Test Review', 'rating': 6, 'text': 'This is a test review.'} 
        response = self.client.post(reverse('add_review'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(title='Test Review').exists())

    def test_post_unauth(self):
        data = {'title': 'Test Review', 'rating': 5, 'text': 'This is a test review.'}
        response = self.client.post(reverse('add_review'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(title='Test Review').exists())


class ReviewEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='client', password='password', status='client', phone_number = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)
        self.review = Review.objects.create(title='Test Review', rating=5, text='Initial text', user=self.user_client)

    def test_get_auth_user_and_review_exists(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': self.review.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'review_edit_form.html')

    def test_get_auth_user_and_review_nonexist(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_get_unauth(self):
        response = self.client.get(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': self.review.pk}))
        self.assertEqual(response.status_code, 404) 

    def test_post_auth_user_and_review_exists_valid_data(self):
        self.client.force_login(self.user_client)
        data = {'title': 'Updated Review', 'rating': 4, 'text': 'Updated text'}
        response = self.client.post(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': self.review.pk}), data)
        self.assertEqual(response.status_code, 302) 
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, 'Updated Review')

    def test_post_auth_user_and_review_exists_invalid_data(self):
        self.client.force_login(self.user_client)
        data = {'title': 'Updated Review', 'rating': 6, 'text': 'Updated text'} 
        response = self.client.post(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': self.review.pk}), data)
        self.assertEqual(response.status_code, 302) 
        self.review.refresh_from_db()
        self.assertNotEqual(self.review.title, 'Updated Review')

    def test_post_unauth(self):
        data = {'title': 'Updated Review', 'rating': 4, 'text': 'Updated text'}
        response = self.client.post(reverse('edit_review', kwargs={'pk': self.user_client.pk, 'jk': self.review.pk}), data)
        self.assertEqual(response.status_code, 302) 
        self.review.refresh_from_db()
        self.assertNotEqual(self.review.title, 'Updated Review')


class UserRegistrationViewTest(TestCase):
    def test_get_view(self):
        client = Client()
        response = client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration_form.html')

    def test_post_valid_data(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 25,
            'phone_number': '+375(33)3456789',
            'address': 'Test Address',
            'password1': 'dssdsfd123',
            'password2': 'dssdsfd123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_post_invalid_age(self):
        client = Client()
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 16,
            'phone_number': '+375(33)3456789',
            'address': 'Test Address',
            'password1': 'dssdsfd123',
            'password2': 'dssdsfd123'  
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_post_invalid_data(self):
        client = Client()
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'age': 23,
            'phone_number': '123456789',
            'address': 'Test Address',
            'password1': 'dssdsfd123',
            'password2': 'dssdsfd123'  
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='testuser').exists())


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='client', password='password', status='client', phone_number = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)
        
    def test_login_auth_user(self):
        response = self.client.post(reverse('login'), {'username': 'client', 'password': 'password'})
        self.assertEqual(response.status_code, 200)

    def test_login_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login_form.html')

    def test_login_success_url(self):
        view = UserLoginView()
        self.assertEqual(view.get_success_url(), reverse('home'))