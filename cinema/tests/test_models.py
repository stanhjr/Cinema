import unittest
from datetime import date, time
from django.test import TestCase
from cinema.models import CinemaHall, MovieShow, PurchasedTicket, MyUser, TokenExpired
from freezegun import freeze_time


@unittest.skip
class TokenExpiredTest(TestCase):

    def setUp(self):
        TokenExpired.objects.create(last_action='2022-01-22', token_ptr_id='98fe0336e35153393f3bfee2910ce2342d41b435')

    def test_create_token(self):
        my_token = TokenExpired.objects.get(last_action='2022-01-22')
        self.assertEqual(my_token.token_ptr_id, '98fe0336e35153393f3bfee2910ce2342d41b435')


class MyUserTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        MyUser.objects.create(username="StanNew", password='123', id=5)

    def test_create_user(self):
        my_user = MyUser.objects.get(id=5)
        self.assertEqual(my_user.username, "StanNew")
        self.assertEqual(my_user.password, '123')


class CinemaHallTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        CinemaHall.objects.create(hall_name="StanHallNew", number_of_seats=111, id=5)

    def test_create_cinema_hall(self):
        test_hall = CinemaHall.objects.get(id=5)
        self.assertEqual(test_hall.hall_name, "StanHallNew")
        self.assertEqual(test_hall.number_of_seats, 111)

    @freeze_time('2022-01-22')
    def test_cinema_hall_methods(self):

        stan_hall = CinemaHall.objects.get(id=1)
        alice_hall = CinemaHall.objects.get(id=2)
        purchase_obj = PurchasedTicket.objects.get(id=1)
        self.assertEqual(stan_hall.get_tickets(), purchase_obj)
        self.assertEqual(alice_hall.get_tickets(), None)


class MovieShowTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):

        MovieShow.objects.create(movie_name='TestMovie',
                                 ticket_price=50,
                                 start_time='08:00',
                                 finish_time='10:00',
                                 start_date='2022-01-22',
                                 finish_date='2022-01-30',
                                 cinema_hall=CinemaHall.objects.get(id=1),
                                 id=6)

    def test_create_movie_show(self):
        stan_hall = CinemaHall.objects.get(id=1)
        test_movie = MovieShow.objects.get(id=6)
        self.assertEqual(test_movie.movie_name, 'TestMovie')
        self.assertEqual(test_movie.ticket_price, 50)
        self.assertEqual(test_movie.start_time,  time.fromisoformat('08:00'))
        self.assertEqual(test_movie.finish_time, time.fromisoformat('10:00'))
        self.assertEqual(test_movie.start_date, date.fromisoformat('2022-01-22'))
        self.assertEqual(test_movie.finish_date, date.fromisoformat('2022-01-30'))
        self.assertEqual(test_movie.cinema_hall, stan_hall)

    @freeze_time('2022-01-22')
    def test_movie_get_purchased_methods(self):
        batman_movie = MovieShow.objects.get(id=1)
        superman_movie = MovieShow.objects.get(id=2)
        purchase_obj = PurchasedTicket.objects.get(id=1)
        self.assertEqual(batman_movie.get_purchased(), purchase_obj)
        self.assertEqual(superman_movie.get_purchased(), None)

    def test_movie_get_tickets_count_methods(self):
        batman_movie = MovieShow.objects.get(id=1)
        self.assertEqual(batman_movie.get_tickets_count("2022-01-22"), 95)
        self.assertEqual(batman_movie.get_tickets_count("2022-01-23"), 100)


class PurchasedTicketTestCase(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):

        PurchasedTicket.objects.create(date='2022-01-22',
                                       number_of_ticket=5,
                                       movie_show=MovieShow.objects.get(id=1),
                                       user=MyUser.objects.get(id=1),
                                       id=5)

    def test_create_purchase_ticket(self):
        movie_show = MovieShow.objects.get(id=1)
        user = MyUser.objects.get(id=1)
        purchase_obj = PurchasedTicket.objects.get(id=1)
        self.assertEqual(purchase_obj.date, date.fromisoformat('2022-01-22'))
        self.assertEqual(purchase_obj.number_of_ticket, 5)
        self.assertEqual(purchase_obj.movie_show, movie_show)
        self.assertEqual(purchase_obj.user, user)

    def test_method_purchase_ticket(self):
        purchase_obj = PurchasedTicket.objects.get(id=1)
        self.assertEqual(purchase_obj.get_purchase_amount(), 250)












