import unittest
from freezegun import freeze_time
from django.test import TestCase
from cinema.forms import CinemaHallCreateForm, MovieShowCreateForm, MovieShowUpdateForm, ProductBuyForm, SignUpForm


class CinemaHallCreateFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def test_create_existing_hall_name(self):
        form_data = {'hall_name': 'StanHall', 'number_of_seats': 5}
        form = CinemaHallCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_create_new_hall_name(self):
        form_data = {'hall_name': 'NewHall', 'number_of_seats': 5}
        form = CinemaHallCreateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_update_hall(self):
        ...


class MovieShowCreateFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def test_overlay_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '08:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 1}

        form = MovieShowCreateForm(data=form_data)
        self.assertRaises(TypeError)
        self.assertRaisesMessage(TypeError, 'Сеансы в одном зале не могут накладываться друг на друга')

    def test_confused_time_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowCreateForm(data=form_data)
        self.assertRaises(TypeError)
        self.assertRaisesMessage(TypeError, 'Фильм всё так должен идти какое то количество времени)))')

    def test_confused_date_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '08:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowCreateForm(data=form_data)
        self.assertRaises(TypeError)
        self.assertRaisesMessage(TypeError, 'Дата конца сеанса не может быть раньше чем дата начала сеанса')

    @unittest.skip
    def test_equal_date_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-30',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowCreateForm(data=form_data)
        self.assertRaises(TypeError)

    @freeze_time('2022-01-22')
    def test_create_movie_show_valid(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '19:00',
                     'finish_time': '20:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowCreateForm(data=form_data)
        self.assertTrue(form.is_valid())


class MovieShowUpdateFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    @unittest.skip
    def test_confused_time_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowUpdateForm(data=form_data)
        self.assertRaises(TypeError)

    def test_confused_date_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '08:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowUpdateForm(data=form_data)
        self.assertRaises(TypeError)

    @unittest.skip
    def test_equal_date_movie_show_create(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-30',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowUpdateForm(data=form_data)
        self.assertRaises(TypeError)

    @freeze_time('2022-01-22')
    def test_create_movie_show_valid(self):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '19:00',
                     'finish_time': '20:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        form = MovieShowUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())


@unittest.skip
class ProductBuyFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def test_ticket_not_enough(self):
        form = ProductBuyForm(data={"number_of_ticket": 4, "tickets_left": 1})
        form.request.tickets_left = 1
        self.assertRaises(TypeError)

    def test_there_are_tickets(self):
        form = ProductBuyForm(data={"number_of_ticket": 4, "tickets_left": 10})
        form.request.tickets_left = 10
        self.assertTrue(form.is_valid())


class SignUpFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def test_sign_up_valid(self):
        form_data = {'username': 'Klim', 'password1': 'Power4Power6Treu7', 'password2': 'Power4Power6Treu7'}
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_sign_up_invalid_user(self):
        form_data = {'username': 'stan', 'password1': '1', 'password2': '1'}
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())





























