import unittest
from datetime import date, time
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from cinema.api.serializers import CinemaHallSerializer, RegisterSerializer, MovieShowSerializer, PurchaseSerializer, \
    PurchaseSerializerCreate
from cinema.models import CinemaHall, MovieShow, PurchasedTicket, MyUser, TokenExpired
from freezegun import freeze_time


# api/registration/


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













# @freeze_time('2022-01-22')
# class MovieShowSerializerPOSTTestCase(TestCase):
#     fixtures = ['initial_data.json', ]
#
#     def test_create_movie_show_valid(self):
#         cinema_hall_obj = CinemaHall.objects.get(id=2)
#         movie_data = {'movie_name': 'TestMovie',
#                       'ticket_price': 77,
#                       'start_time': '19:00',
#                       'finish_time': '20:00',
#                       'start_date': '2022-01-22',
#                       'finish_date': '2022-01-30',
#                       'cinema_hall': cinema_hall_obj}
#
#         new_movie = MovieShow.objects.create(**movie_data)
#
#         serializer_data = MovieShowSerializer(new_movie).data
#         expected_data = {'movie_name': 'TestMovie',
#                          'ticket_price': 77,
#                          'start_time': '19:00',
#                          'finish_time': '20:00',
#                          'start_date': '2022-01-22',
#                          'finish_date': '2022-01-30',
#                          'cinema_hall': 2,
#                          'id': new_movie.id}
#         self.assertEqual(serializer_data.get('id'), new_movie.id)
#         self.assertEqual(serializer_data.get('cinema_hall').data, expected_data)
#
#     def test_create_movie_show_invalid(self):
#         cinema_hall_obj = CinemaHall.objects.get(id=1)
#         movie_data = {'movie_name': 'TestMovie',
#                       'ticket_price': 77,
#                       'start_time': '9:00',
#                       'finish_time': '10:00',
#                       'start_date': '2022-01-22',
#                       'finish_date': '2022-01-30',
#                       'cinema_hall': cinema_hall_obj}
#
#         new_movie = MovieShow.objects.create(**movie_data)
#
#         serializer_data = MovieShowSerializer(new_movie).data
#         expected_data = {'start_date, finish_date': 'Сеансы в одном зале не могут накладываться друг на друга'}
#         self.assertEqual(serializer_data, expected_data)
#


