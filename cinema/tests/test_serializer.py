import unittest
from datetime import date, time
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from cinema.api.serializers import CinemaHallSerializer, RegisterSerializer, MovieShowSerializer, PurchaseSerializer, \
    PurchaseSerializerCreate, MovieShowSerializerPost
from cinema.models import CinemaHall, MovieShow, PurchasedTicket, MyUser, TokenExpired
from freezegun import freeze_time


class RegisterSerializerTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def test_register_valid(self):
        user = {'username': 'NewUser', 'password': 'Power1Power2Power'}
        data = RegisterSerializer(user).data
        expected_data = {'username': 'NewUser', 'password': 'Power1Power2Power'}
        self.assertEqual(data, expected_data)


class CinemaHallSerializerTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def test_create_cinema_valid(self):
        new_cinema = CinemaHall.objects.create(hall_name='StanHallNew', number_of_seats=111, id=5)
        data = CinemaHallSerializer(new_cinema).data
        expected_data = {'hall_name': 'StanHallNew', 'number_of_seats': 111, 'id': 5}
        self.assertEqual(data, expected_data)


@freeze_time('2022-01-22')
class PurchaseSerializerCreateTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def test_purchase_valid(self):
        movie_show = MovieShow.objects.get(id=1)
        purchase_data = {'date': '2022-01-22', 'movie_show': movie_show, 'number_of_ticket': 5}
        data = PurchaseSerializerCreate(purchase_data).data
        expected_data = {'date': '2022-01-22', 'movie_show': 1, 'number_of_ticket': 5}
        self.assertEqual(data, expected_data)


@freeze_time('2022-01-22')
class MovieShowSerializerPostTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def test_create_movie_show_valid(self):
        data = {'movie_name': 'TestMovie',
                      'ticket_price': 77,
                      'start_time': '19:00',
                      'finish_time': '20:00',
                      'start_date': '2022-01-23',
                      'finish_date': '2022-01-30',
                      'cinema_hall': 2}

        serializer = MovieShowSerializerPost(data=data)
        self.assertTrue(serializer.is_valid())

    def test_create_movie_show_invalid_cross_sessions(self):
        data = {'movie_name': 'TestMovie',
                      'ticket_price': 188,
                      'start_time': '08:00',
                      'finish_time': '10:00',
                      'start_date': '2022-01-23',
                      'finish_date': '2022-01-30',
                      'cinema_hall': 1}

        serializer = MovieShowSerializerPost(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_movie_show_invalid_time(self):
        data = {'movie_name': 'TestMovie',
                      'ticket_price': 188,
                      'start_time': '11:00',
                      'finish_time': '10:00',
                      'start_date': '2022-01-22',
                      'finish_date': '2022-01-22',
                      'cinema_hall': 2}

        serializer = MovieShowSerializerPost(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_movie_show_invalid_date(self):
        data = {'movie_name': 'TestMovie',
                      'ticket_price': 188,
                      'start_time': '11:00',
                      'finish_time': '10:00',
                      'start_date': '2022-01-25',
                      'finish_date': '2022-01-24',
                      'cinema_hall': 2}

        serializer = MovieShowSerializerPost(data=data)
        self.assertFalse(serializer.is_valid())


@freeze_time('2022-01-22')
class PurchaseSerializerCreateTest(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = MyUser.objects.get(id=1)

    def test_create_purchase_valid_data(self):
        data = {'date': '2022-01-25', 'movie_show': 1, 'number_of_ticket': 10, 'user_id': 1}
        serializer = PurchaseSerializerCreate(data=data, user_id=1)
        self.assertTrue(serializer.is_valid())

    def test_create_purchase_invalid_max_tickets(self):
        data = {'date': '2022-01-25', 'movie_show': 1, 'number_of_ticket': 500, 'user_id': 1}
        serializer = PurchaseSerializerCreate(data=data, user_id=1)
        self.assertFalse(serializer.is_valid())

    def test_create_purchase_invalid_date(self):
        data = {'date': '2022-01-20', 'movie_show': 1, 'number_of_ticket': 5}
        serializer = PurchaseSerializerCreate(data=data, user_id=1)
        self.assertFalse(serializer.is_valid())

    def test_create_purchase_invalid_no_count_ticket(self):
        data = {'date': '2022-01-20', 'movie_show': 1, 'number_of_ticket': 0}
        serializer = PurchaseSerializerCreate(data=data, user_id=1)
        self.assertFalse(serializer.is_valid())















