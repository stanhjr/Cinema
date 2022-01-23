import json
import unittest
from datetime import time, date
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from rest_framework.test import APIClient
from freezegun import freeze_time

from cinema.api.resources import PurchaseList, CinemaHallUpdate
from cinema.api.serializers import PurchaseSerializer
from cinema.models import MyUser, CinemaHall, MovieShow, PurchasedTicket



class PurchaseListViewTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):

        self.factory = APIRequestFactory()
        self.superuser = MyUser.objects.get(username='stan')
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_list_purchase_user(self):
        request = self.factory.get('/api/purchased/')
        force_authenticate(request, user=self.superuser)
        response = PurchaseList.as_view()(request)
        purchasets = PurchasedTicket.objects.filter(user=request.user)
        serializer = PurchaseSerializer(purchasets, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_purchase_anonimousmuser(self):
        request = self.factory.get('/api/purchased/')
        request.user = AnonymousUser()
        response = PurchaseList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @freeze_time('2022-01-22')
    def test_create_purchase_user(self):
        movie_show_obj = MovieShow.objects.get(id=2)
        request = self.factory.post('/api/purchased/', {'movie_show': movie_show_obj, 'number_of_ticket': 2, 'date': '2022-01-23'})
        force_authenticate(request, user=self.superuser)
        response = PurchaseList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'movie_show': movie_show_obj, 'number_of_ticket': 2, 'date': '2022-01-22'})


@freeze_time('2022-01-22')
class CinemaHallUpdateTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = MyUser.objects.get(username='stan')
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_update_cinema_valid(self):
        request = self.factory.put('/api/update_hall/', {'hall_name': 'StanHallNew', 'number_of_seats': 222})
        force_authenticate(request, user=self.superuser)
        response = CinemaHallUpdate.as_view()(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'hall_name': 'StanHallNew', 'number_of_seats': 222, 'id': 2})

    def test_update_cinema_invalid(self):
        request = self.factory.put('/api/update_hall/', {'hall_name': 'StanHallNew', 'number_of_seats': 222})
        force_authenticate(request, user=self.superuser)
        response = CinemaHallUpdate.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)













