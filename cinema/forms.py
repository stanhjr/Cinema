from datetime import date, time, datetime
from django import forms
from django.forms.widgets import TextInput
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.db.models import Q
from cinema.models import MyUser, PurchasedTicket, MovieShow, CinemaHall


class NumberInput(TextInput):
    input_type = 'number'


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class CinemaHallCreateForm(ModelForm):
    class Meta:
        model = CinemaHall
        fields = ["hall_name", "number_of_seats"]


class MovieShowCreateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MovieShowCreateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MovieShow
        fields = '__all__'

        widgets = {
            'start_date': DateInput(),
            'finish_date': DateInput(),
            'start_time': TimeInput(),
            'finish_time': TimeInput,
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        finish_time = cleaned_data.get('finish_time')
        start_date = cleaned_data.get('start_date')
        finish_date = cleaned_data.get('finish_date')
        cinema_hall_obj = cleaned_data.get('cinema_hall')

        if start_date > finish_date:
            messages.warning(self.request, 'Дата конца сеанса не может быть раньше чем дата начала сеанса')
            raise ValidationError('Дата конца сеанса не может быть раньше чем дата начала сеанса')
        if start_date == finish_date and start_time >= finish_time:
            messages.warning(self.request, 'Фильм всё так должен идти какое то количество времени)))')
            raise ValidationError('Фильм всё так должен идти какое то количество времени)))')
        if start_date < date.today() or finish_date < date.today():
            messages.warning(self.request, 'Нельзя создавать сеансы "от вчера"!')
            raise ValidationError('Нельзя создавать сеанcы "от вчера"!')

        if start_date == date.today() and start_time < datetime.now().time():
            messages.warning(self.request, 'Нельзя создавать сеансы "от вчера"!')
            raise ValidationError('Нельзя создавать сеанcы "от вчера"!')

        enter_start_date = Q(start_date__range=(start_date, finish_date))
        enter_finish_date = Q(finish_date__range=(start_date, finish_date))
        middle_date_start = Q(start_date__lte=start_date, finish_date__gte=finish_date)
        enter_start_time = Q(start_time__range=(start_time, finish_time))
        enter_finish_time = Q(finish_time__range=(start_time, finish_time))

        movie_obj = MovieShow.objects.filter(cinema_hall=cinema_hall_obj.pk).filter(
            enter_start_date | enter_finish_date | middle_date_start).filter(enter_start_time | enter_finish_time).all()

        if start_time > finish_time:
            enter_start_time_until_midnight = Q(start_time__range=(start_time, '23:59:59'))
            enter_start_time_after_midnight = Q(start_time__range=('00:00:00', finish_time))
            enter_finish_time_until_midnight = Q(finish_time__range=(start_time, '23:59:59'))
            enter_finish_time_after_midnight = Q(finish_time__range=('00:00:00', finish_time))

            movie_obj = MovieShow.objects.filter(cinema_hall=cinema_hall_obj.pk).filter(
                enter_start_date | enter_finish_date | middle_date_start).\
                filter(enter_start_time_until_midnight | enter_start_time_after_midnight |
                       enter_finish_time_until_midnight | enter_finish_time_after_midnight).all()

        if movie_obj:
            messages.warning(self.request, 'Сеансы в одном зале не могут накладываться друг на друга')
            raise ValidationError('Сеансы в одном зале не могут накладываться друг на друга')


class MovieShowUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(MovieShowUpdateForm, self).__init__(*args, **kwargs)

    class Meta:
        model = MovieShow
        fields = '__all__'

        widgets = {
            'start_date': DateInput(),
            'finish_date': DateInput(),
            'start_time': TimeInput(),
            'finish_time': TimeInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        finish_time = cleaned_data.get('finish_time')
        start_date = cleaned_data.get('start_date')
        finish_date = cleaned_data.get('finish_date')

        if start_date > finish_date:
            messages.warning(self.request, 'Дата конца сеанса не может быть раньше чем дата начала сеанса')
            raise ValidationError('Дата конца сеанса не может быть раньше чем дата начала сеанса')
        if start_date == finish_date and start_time >= finish_time:
            messages.warning(self.request, 'Фильм всё так должен идти какое то количество времени)))')
            raise ValidationError('Фильм всё так должен идти какое то количество времени)))')
        if start_date < date.today():
            messages.warning(self.request, 'Нельзя создавать сеансы "от вчера"!')
            raise ValidationError('Нельзя создавать сеанcы "от вчера"!')


class SignUpForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2')


class ChoiceForm(forms.Form):
    sort_by_price_max = 'price_max'
    sort_by_price_min = 'price_min'
    sort_by_start_time = 'start_time'
    sort_movies = [
        (sort_by_start_time, 'For start movie'),
        (sort_by_price_max, 'Price range up'),
        (sort_by_price_min, 'Price range down')
    ]
    filter_by = forms.ChoiceField(choices=sort_movies, label='Filter')


class ProductBuyForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductBuyForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PurchasedTicket
        fields = ["number_of_ticket", ]
        widgets = {"number_of_ticket": NumberInput(attrs={'min': '1', 'step': '1'})}

    def clean(self):
        cleaned_data = super().clean()
        movie_show_id = self.request.POST.get('movie-id')
        movie_show_obj = MovieShow.objects.get(id=movie_show_id)
        count_of_buy = int(cleaned_data.get('number_of_ticket'))
        tickets_left = int(self.request.POST.get('tickets_left'))

        if count_of_buy == 0:
            messages.warning(self.request, 'Вы не выбрали нужного количества билетов')
            raise ValidationError('Вы не выбрали нужного количества билетов')

        if movie_show_obj.start_time < datetime.now().time() and self.request.POST.get('date-buy') == str(date.today()):
            messages.warning(self.request, 'Онлайн продажи для этого сеанса на сегодня закрыты')
            raise ValidationError('Этот сеанс сегодня уже завершился')

        if count_of_buy > tickets_left:
            messages.warning(self.request, 'Такого количества свободных мест нет')
            raise ValidationError('Такого количества свободных мест нет')
