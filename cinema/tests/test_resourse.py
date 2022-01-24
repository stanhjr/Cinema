import json
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from freezegun import freeze_time
from cinema.api.resources import PurchaseList, CinemaHallUpdate, MovieShowPost, MovieShowUpdate, MovieShowViewSet, \
    GetToken, RegisterAPI
from cinema.api.serializers import PurchaseSerializer
from cinema.models import MyUser, PurchasedTicket


@freeze_time('2022-01-23')
class MovieShowViewSetTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = MyUser.objects.get(username='stan')
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_movie_list_all_users(self):
        request = self.factory.get('/api/session/')
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_show_day_today(self):
        request = self.factory.get('/api/session/')
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request, show_day='today')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_show_day_tomorrow(self):
        request = self.factory.get('/api/session/')
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request, show_day='tomorrow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_show_cinema_hall_day_today(self):
        request = self.factory.get('/api/session/')
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request, show_day='tomorrow', cinema_hall=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_show_cinema_hall_only(self):
        request = self.factory.get('/api/session/')
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request, cinema_hall=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_movie_list_show_cinema_time_invalid(self):
        data = {'cinema_hall': 1, 'start_time': '11:00', 'finish_time': '08:00'}
        request = self.factory.get('/api/session/', data)
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Error query params': 'Время начала не может быть больше или равно времени окончания поиска'})

    def test_movie_list_show_cinema_time_valid(self):
        data = {'cinema_hall': '1', 'start_time': '08:00', 'finish_time': '12:00'}
        request = self.factory.get('/api/session/', data)
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowViewSet.as_view({'get': 'list'})(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with open(r'D:\0_cinema\Cinema\cinema\tests\data\test_movie_list_answer.json') as json_file:
            data = json.load(json_file)
        response.render()
        self.assertEqual(json.loads(response.content), data)


@freeze_time('2022-01-22')
class MovieShowUpdateTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = MyUser.objects.get(username='stan')
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_update_movie_superuser_valid(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '15:00',
                'finish_time': '16:00',
                'start_date': '2022-01-22',
                'finish_date': '2022-01-30',
                'cinema_hall': 1}

        request = self.factory.put('/api/session_update/', data)
        force_authenticate(request, user=self.superuser)
        response = MovieShowUpdate.as_view()(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_update_movie_superuser_invalid_pk(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '15:00',
                'finish_time': '16:00',
                'start_date': '2022-01-22',
                'finish_date': '2022-01-30',
                'cinema_hall': 1}

        request = self.factory.put('/api/session_update/', data)
        force_authenticate(request, user=self.superuser)
        response = MovieShowUpdate.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_movie_superuser_invalid_data(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '08:00',
                'finish_time': '11:00',
                'start_date': '2022-01-30',
                'finish_date': '2022-01-22',
                'cinema_hall': 1}

        request = self.factory.put('/api/session_update/', data)
        force_authenticate(request, user=self.superuser)
        response = MovieShowUpdate.as_view()(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_movie_user(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '15:00',
                'finish_time': '16:00',
                'start_date': '2022-01-22',
                'finish_date': '2022-01-30',
                'cinema_hall': 1}

        request = self.factory.put('/api/session_update/', data)
        force_authenticate(request, user=self.user)
        response = MovieShowUpdate.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_movie_anonimouseuser(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '15:00',
                'finish_time': '16:00',
                'start_date': '2022-01-22',
                'finish_date': '2022-01-30',
                'cinema_hall': 1}

        request = self.factory.put('/api/session_update/', data)
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowUpdate.as_view()(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@freeze_time('2022-01-22')
class MovieShowPostTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.superuser = MyUser.objects.get(username='stan')
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_create_movie_superuser(self):
        data = {'movie_name': 'TestMovie',
                    'ticket_price': 77,
                    'start_time': '08:00',
                    'finish_time': '11:00',
                    'start_date': '2022-01-22',
                    'finish_date': '2022-01-30',
                    'cinema_hall': 2}

        request = self.factory.post('/api/session_create/', data)
        force_authenticate(request, user=self.superuser)
        response = MovieShowPost.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_movie_superuser_invalid(self):
        data = {'movie_name': 'TestMovie',
                'ticket_price': 77,
                'start_time': '08:00',
                'finish_time': '11:00',
                'start_date': '2022-01-22',
                'finish_date': '2022-01-30',
                'cinema_hall': 1}

        request = self.factory.post('/api/session_create/', data)
        force_authenticate(request, user=self.superuser)
        response = MovieShowPost.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_movie_user(self):
        data = {'movie_name': 'TestMovie',
                    'ticket_price': 77,
                    'start_time': '08:00',
                    'finish_time': '11:00',
                    'start_date': '2022-01-22',
                    'finish_date': '2022-01-30',
                    'cinema_hall': 2}

        request = self.factory.post('/api/session_create/', data)
        force_authenticate(request, user=self.user)
        response = MovieShowPost.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie_anonimouseuser(self):
        data = {'movie_name': 'TestMovie',
                    'ticket_price': 77,
                    'start_time': '08:00',
                    'finish_time': '11:00',
                    'start_date': '2022-01-22',
                    'finish_date': '2022-01-30',
                    'cinema_hall': 2}

        request = self.factory.post('/api/session_create/', data)
        force_authenticate(request, user=AnonymousUser())
        response = MovieShowPost.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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
    def test_create_purchase_superuser(self):
        request = self.factory.post('/api/purchased/', {'movie_show': 1, 'number_of_ticket': 2, 'date': '2022-01-22'})
        force_authenticate(request, user=self.superuser)
        response = PurchaseList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'movie_show': 1, 'number_of_ticket': 2, 'date': '2022-01-22'})

    @freeze_time('2022-01-22')
    def test_create_purchase_user(self):
        request = self.factory.post('/api/purchased/', {'movie_show': 1, 'number_of_ticket': 2, 'date': '2022-01-22'})
        force_authenticate(request, user=self.user)
        response = PurchaseList.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'movie_show': 1, 'number_of_ticket': 2, 'date': '2022-01-22'})


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


@freeze_time('2022-01-22')
class GetTokenTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = MyUser.objects.create_user(username='alice', password='1')

    def test_login_superuser(self):
        request = self.factory.post('/api/login/', {'username': 'stan', 'password': '1'})
        response = GetToken.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user(self):
        data = {'username': 'alice', 'password': '1'}
        request = self.factory.post('/api/login/', data=data)
        response = GetToken.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_user_invalid(self):
        data = {'username': 'alice', 'password': '3'}
        request = self.factory.post('/api/login/', data=data)
        response = GetToken.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RegisterApiTestCase(APITestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = APIRequestFactory()

    def test_register_valid(self):
        data = {'username': 'alice', 'password': 'Power1Power2Power3'}
        request = self.factory.post('api/registration/', data=data)
        response = RegisterAPI.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid(self):
        data = {'username': 'stan', 'password': '1'}
        request = self.factory.post('api/registration/', data=data)
        response = RegisterAPI.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)










