from unittest.mock import patch
from django.test import RequestFactory
from freezegun import freeze_time
from django.test import TestCase
from cinema.forms import CinemaHallCreateForm, MovieShowCreateForm, MovieShowUpdateForm, ProductBuyForm, SignUpForm
from cinema.models import MovieShow


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


@freeze_time('2022-01-22 07:30')
class MovieShowCreateFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_overlay_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '08:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 1}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Сеансы в одном зале не могут накладываться друг на друга']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_invalid_time_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__':  ['Нельзя создавать сеанcы "от вчера"!']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_invalid_date_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '05:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Нельзя создавать сеанcы "от вчера"!']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_equal_date_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-30',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        self.assertFalse(form.is_valid())
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Фильм всё так должен идти какое то количество времени)))']})

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

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_invalid_midnight_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '23:00',
                     'finish_time': '21:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 1}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        self.assertFalse(form.is_valid())

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_invalid_midnight_movie_show_create_2(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '23:00',
                     'finish_time': '21:00',
                     'start_date': '2022-01-22',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 1}

        request = self.factory.post('create-movie/')
        form = MovieShowCreateForm(data=form_data, request=request)
        self.assertFalse(form.is_valid())


@freeze_time('2022-01-22 07:30')
class MovieShowUpdateFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_invalid_time_movie_show_create(self, warning):
        self.factory = RequestFactory()
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        request = self.factory.post('update_movie_show/1/')
        form = MovieShowUpdateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Нельзя создавать сеанcы "от вчера"!']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_confused_date_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '08:00',
                     'finish_time': '11:00',
                     'start_date': '2022-01-21',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}

        request = self.factory.post('update_movie_show/1/')
        form = MovieShowUpdateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Нельзя создавать сеанcы "от вчера"!']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_equal_date_movie_show_create(self, warning):
        form_data = {'movie_name': 'TestMovie',
                     'ticket_price': 77,
                     'start_time': '11:00',
                     'finish_time': '08:00',
                     'start_date': '2022-01-30',
                     'finish_date': '2022-01-30',
                     'cinema_hall': 2}
        request = self.factory.post('update_movie_show/1/')
        form = MovieShowUpdateForm(data=form_data, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Фильм всё так должен идти какое то количество времени)))']})

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


class ProductBuyFormTest(TestCase):
    fixtures = ['initial_data.json', ]

    def setUp(self):
        self.factory = RequestFactory()

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_ticket_not_enough(self, warning):
        movie_obj = MovieShow.objects.get(id=1)
        request = self.factory.post('ticket-buy/', {'tickets_left': 1, 'movie-id': 1})
        form = ProductBuyForm(data={"number_of_ticket": 4, "tickets_left": 1}, request=request)
        form.is_valid()
        self.assertEqual(form.errors, {'__all__': ['Такого количества свободных мест нет']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_there_are_tickets(self, warning):
        request = self.factory.post('ticket-buy/', {'tickets_left': 10, 'movie-id': 1})
        form = ProductBuyForm(data={"number_of_ticket": 4, "tickets_left": 1}, request=request)
        self.assertTrue(form.is_valid())

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_there_are_no_count_tickets(self, warning):
        request = self.factory.post('ticket-buy/', {'tickets_left': 10, 'movie-id': 1})
        form = ProductBuyForm(data={"number_of_ticket": 0, "tickets_left": 1}, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'__all__': ['Вы не выбрали нужного количества билетов']})

    @patch('cinema.forms.messages.warning', return_value=None)
    def test_date_time_invalid(self, warning):
        request = self.factory.post('ticket-buy/', {'tickets_left': 10, 'movie-id': 1})
        form = ProductBuyForm(data={"number_of_ticket": 0, "tickets_left": 1}, request=request)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'__all__': ['Вы не выбрали нужного количества билетов']})


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
