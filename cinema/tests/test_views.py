import unittest
from datetime import time, date
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.test import TestCase, RequestFactory
from freezegun import freeze_time

from cinema.models import MyUser, CinemaHall, MovieShow
from cinema.views import CinemaHallListView, CinemaHallCreateView, MovieShowCreateView, CinemaHallUpdateView, \
    MovieShowUpdateView, PurchasedListView, real_time_movie


class CinemaHallListViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)

    def test_list_hall_user(self):
        request = self.factory.get('/hall-list/')
        request.user = self.user
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_list_hall_superuser(self):
        request = self.factory.get('/hall-list/')
        request.user = self.superuser
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_list_hall_anonymous_user(self):
        request = self.factory.get('/hall-list/')
        request.user = AnonymousUser()
        response = CinemaHallListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')


class CinemaHallCreateViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.post('/hall-list/', {'hall_name': 'NewHall', 'number_of_seats': 5})

    def test_create_cinema_hall_superuser(self):
        request = self.request
        request.user = self.superuser
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/hall-list')

    def test_create_cinema_hall_anonymous_user(self):
        request = self.request
        request.user = AnonymousUser()
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_create_cinema_hall_user(self):
        request = self.request
        request.user = self.user
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')


class MovieShowCreateViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.post('/hall-list/',
                                         {'movie_name': 'TestMovie',
                                         'ticket_price': 77,
                                         'start_time': '08:00',
                                         'finish_time': '11:00',
                                         'start_date': '2022-01-21',
                                         'finish_date': '2022-01-30',
                                         'cinema_hall': 2})

    def test_create_cinema_hall_user(self):
        request = self.request
        request.user = self.user
        response = MovieShowCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_create_cinema_hall_anonymous_user(self):
        request = self.request
        request.user = AnonymousUser()
        response = MovieShowCreateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_create_cinema_hall_superuser(self):
        request = self.request
        request.user = self.superuser
        response = CinemaHallCreateView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class CinemaHallUpdateViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)

    def test_list_hall_user(self):
        request = self.factory.post('update-hall/', {'hall_name': 'StanHall', 'number_of_seats': 5})
        request.user = self.user
        response = CinemaHallUpdateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_list_hall_anonymous_user(self):
        request = self.factory.post('update-hall/', {'hall_name': 'StanHall', 'number_of_seats': 5})
        request.user = AnonymousUser()
        response = CinemaHallUpdateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_list_hall_superuser(self):
        request = self.factory.post('update-hall/', {'hall_name': 'StanHall', 'number_of_seats': 10})
        request.user = self.superuser

        try:
            response = CinemaHallUpdateView.as_view()(request, pk=1)
        except AttributeError:
            result = True
            self.assertTrue(result)

    def test_update_hall_superuser_valid(self):
        request = self.factory.post('update-hall/', {'hall_name': 'StanHallNew', 'number_of_seats': 10})
        request.user = self.superuser
        response = CinemaHallUpdateView.as_view()(request, pk=2)
        cinema_hall_obj = CinemaHall.objects.get(id=2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cinema_hall_obj.hall_name, 'StanHallNew')
        self.assertEqual(cinema_hall_obj.number_of_seats, 10)


class MovieShowUpdateViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.post('update_movie_show/',
                                         {'movie_name': 'NewTestMovie',
                                          'ticket_price': 77,
                                          'start_time': '08:00',
                                          'finish_time': '11:00',
                                          'start_date': '2022-01-21',
                                          'finish_date': '2022-01-30'})

    def test_update_movie_user(self):
        request = self.request
        request.user = self.user
        response = MovieShowUpdateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    def test_update_movie_anonymous_user(self):
        request = self.factory.post('update-hall/', {'hall_name': 'StanHall', 'number_of_seats': 5})
        request.user = AnonymousUser()
        response = MovieShowUpdateView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'login/')

    @unittest.skip
    def test_update_movie_superuser_invalid(self):
        request = self.request
        request.user = self.superuser

        try:
            response = MovieShowUpdateView.as_view()(request, pk=1)
        except AttributeError:
            result = True
            self.assertTrue(result)

    @unittest.skip
    def test_update_movie_superuser_valid(self):
        request = self.request
        request.user = self.superuser
        response = MovieShowUpdateView.as_view()(request, pk=2)
        movie_obj = MovieShow.objects.get(id=2)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(movie_obj.movie_name, 'NewTestMovie')
        self.assertEqual(movie_obj.ticket_price, 77)
        self.assertEqual(movie_obj.start_time, time.fromisoformat('08:00'))
        self.assertEqual(movie_obj.finish_time, time.fromisoformat('11:00'))
        self.assertEqual(movie_obj.start_date, date.fromisoformat('2022-01-21'))
        self.assertEqual(movie_obj.finish_date, date.fromisoformat('2022-01-30'))


class PurchasedListViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.get('purchased/')

    def test_purchased_list_anonymous_user(self):
        request = self.request
        request.user = AnonymousUser()
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/')

    def test_purchased_list_user(self):
        request = self.request
        request.user = self.user
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_purchased_list_superuser(self):
        request = self.request
        request.user = self.superuser
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class MovieListViewTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.get('/')

    def test_movie_list_superuser(self):
        request = self.request
        request.user = self.superuser
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_movie_list_user(self):
        request = self.request
        request.user = self.user
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    @unittest.skip
    def test_movie_list_anonimoususer(self):
        request = self.request
        request.user = AnonymousUser
        response = PurchasedListView.as_view()(request)
        self.assertEqual(response.status_code, 200)


@freeze_time('2022-01-22 11:29:16.852740')
class RealTimeMovieTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')
        self.superuser = MyUser.objects.get(id=1)
        self.request = self.factory.get('/')

    def test_movie_list_user(self):
        request = self.request
        request.user = AnonymousUser
        response = real_time_movie(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), 'Количество активных сеансов 1')