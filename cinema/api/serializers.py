from datetime import date
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
# from cinema.forms import q_time
from cinema.models import MyUser, CinemaHall, PurchasedTicket, MovieShow, TokenExpired


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyUser
        fields = ['username', 'password']

    def save(self, **kwargs):
        self.validated_data["password"] = make_password(self.validated_data["password"])
        return super().save()


class CinemaHallSerializer(serializers.ModelSerializer):
    hall_name = serializers.CharField(max_length=200)
    number_of_seats = serializers.IntegerField(required=True)

    class Meta:
        model = CinemaHall
        fields = ['id', 'hall_name', 'number_of_seats']

    def create(self, validated_data):
        """
        Create and return a new `CinemaHall` instance, given the validated data.
        """

        if CinemaHall.objects.get(hall_name=validated_data.get('hall_name')):
            raise serializers.ValidationError(
                {'hall_name': 'Зал с таким именем уже существует'})

        return CinemaHall.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `CinemaHall` instance, given the validated data.
        """
        instance.hall_name = validated_data.get('hall_name', instance.hall_name)
        instance.number_of_seats = validated_data.get('number_of_seats', instance.number_of_seats)
        instance.save()
        return instance

    def validate(self, data):
        if self.instance:
            cinema_hall_obj = CinemaHall.objects.get(id=self.instance.id)
            if cinema_hall_obj.get_tickets():
                raise serializers.ValidationError(
                    {'cinema_hall': 'В этом зале куплены билеты, изменить нельзя'})
        return data


class MovieShowSerializer(serializers.ModelSerializer):

    cinema_hall = CinemaHallSerializer()

    class Meta:
        model = MovieShow
        fields = '__all__'


class MovieShowSerializerPOST(serializers.ModelSerializer):

    class Meta:
        model = MovieShow
        fields = '__all__'

    def create(self, validated_data):
        return MovieShow.objects.create(**validated_data)

    def update(self, instance, validated_data):
        return instance

    def validate(self, data):

        start_time = data.get('start_time')
        finish_time = data.get('finish_time')
        start_date = data.get('start_date')
        finish_date = data.get('finish_date')

        if start_date > finish_date:
            raise serializers.ValidationError(
                {'start_date, finish_date': 'Дата конца сеанса не может быть раньше чем дата начала сеанса'})
        if start_date == finish_date and start_time >= finish_time:
            raise serializers.ValidationError(
                {'start_date, finish_date': 'Фильм всё таки должен идти какое то количество времени'})

        if start_date < date.today():
            raise serializers.ValidationError(
                {'start_date, finish_date': 'Нельзя создавать сеанcы от вчера!'})

        cinema_hall_obj = CinemaHall.objects.get(id=data.get('cinema_hall').id)
        enter_start_date = Q(start_date__range=(start_date, finish_date))
        enter_finish_date = Q(finish_date__range=(start_date, finish_date))
        enter_start_time = Q(start_time__range=(start_time, finish_time))
        enter_finish_time = Q(finish_time__range=(start_time, finish_time))

        movie_obj = MovieShow.objects.filter(cinema_hall=cinema_hall_obj.pk).filter(
            enter_start_date | enter_finish_date).filter(enter_start_time | enter_finish_time)

        if self.instance:
            movie_show_obj = MovieShow.objects.get(id=self.instance.id)
            if movie_show_obj.get_purchased():
                raise serializers.ValidationError(
                    {'movie_show': 'На этот сеанс уже куплены билеты, изменить нелья'})

            elif MovieShow.objects.filter(cinema_hall=self.instance.cinema_hall).exclude(id=self.instance.id).filter(
                    enter_start_date | enter_finish_date).filter(enter_start_time | enter_finish_time):
                raise serializers.ValidationError(
                    {'start_date, finish_date': 'Сеансы в одном зале не могут накладываться друг на друга'})

        else:
            if movie_obj:
                raise serializers.ValidationError(
                    {'start_date, finish_date': 'Сеансы в одном зале не могут накладываться друг на друга'})

        return data


class PurchaseSerializerCreate(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super(PurchaseSerializerCreate, self).__init__(*args, **kwargs)

    class Meta:
        model = PurchasedTicket
        fields = ['date', 'movie_show', 'number_of_ticket']

    def create(self, validated_data):
        """
        Create and return a new `PurchasedTicket` instance, given the validated data.
        """

        return PurchasedTicket.objects.create(**validated_data)

    def validate(self, data):
        movie = data['movie_show']
        number_of_ticket = data['number_of_ticket']
        data['user'] = MyUser.objects.get(id=self.user_id)

        if movie.get_tickets_count(data['date']) - int(number_of_ticket) < 0:
            raise serializers.ValidationError({'number_of_ticket': 'Такого количества свободных мест нет'})
        return data


class PurchaseSerializer(serializers.ModelSerializer):

    movie_show = MovieShowSerializer()

    class Meta:
        model = PurchasedTicket
        fields = ['date', 'movie_show', 'number_of_ticket']

    def create(self, validated_data):
        """
        Create and return a new `PurchasedTicket` instance, given the validated data.
        """

        return PurchasedTicket.objects.create(**validated_data)




