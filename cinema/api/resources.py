import datetime
from datetime import timedelta, date
from django.db import transaction
from django.db.models import Q
from rest_framework import permissions, status, serializers
from rest_framework.authtoken.views import ObtainAuthToken
from django.utils import timezone
from rest_framework.generics import CreateAPIView, DestroyAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from cinema.api.serializers import RegisterSerializer, CinemaHallSerializer, PurchaseSerializer, MovieShowSerializer, \
    PurchaseSerializerCreate, MovieShowSerializerPost
from cinema.models import MyUser, TokenExpired, CinemaHall, MovieShow, PurchasedTicket
from stanhjr_project.settings import SESSION_COOKIE_AGE


class GetToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = TokenExpired.objects.get_or_create(user=user)
        token.last_action = timezone.now()
        token.save()

        return Response({'token': token.key})


class RegisterAPI(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer


class LogoutAPI(DestroyAPIView):
    queryset = TokenExpired.objects.all()

    def get_object(self):
        obj = self.queryset.filter(user=self.request.user)
        return obj


class MyUserViewSet(ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer
    http_method_names = ['post', ]
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return super().get_permissions()


class CinemaHallUpdate(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        cinema_hall = CinemaHall.objects.get(id=pk)
        serializer = CinemaHallSerializer(cinema_hall, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CinemaHallList(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        cinema_hall = CinemaHall.objects.all()
        serializer = CinemaHallSerializer(cinema_hall, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CinemaHallSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        purchase_list = PurchasedTicket.objects.filter(user=request.user.id)
        serializer = PurchaseSerializer(purchase_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PurchaseSerializerCreate(data=request.data, user_id=request.user.id)
        if serializer.is_valid():
            user = MyUser.objects.get(id=request.user.id)

            with transaction.atomic():
                obj = serializer.save()
                user.money_spent += obj.get_purchase_amount()
                user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieShowPost(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = MovieShowSerializerPost(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieShowUpdate(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        movie_show = MovieShow.objects.get(id=pk)
        serializer = MovieShowSerializerPost(movie_show, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieShowViewSet(ModelViewSet):
    queryset = MovieShow.objects.filter(finish_date__gt=timezone.now())
    serializer_class = MovieShowSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        start_time = self.request.query_params.get('start_time') or '00:00:00'
        finish_time = self.request.query_params.get('finish_time') or '23:59:59'
        hall_id = self.request.query_params.get('hall_id')
        show_day = self.request.query_params.get('show_day')
        enter_time_range = Q(start_time__range=(start_time, finish_time))

        if start_time >= finish_time:
            raise serializers.ValidationError(
                {'Error query params': 'Время начала не может быть больше или равно времени окончания поиска'})

        if show_day == 'today':
            return super().get_queryset().filter(start_date__lte=date.today(),
                                                 finish_date__gt=date.today())

        elif show_day == 'tomorrow':
            return super().get_queryset().filter(start_date__lte=date.today() + datetime.timedelta(days=1),
                                                 finish_date__gt=date.today())

        if hall_id:
            return super().get_queryset().filter(enter_time_range, start_date__lte=date.today(),
                                                 finish_date__gte=date.today(),
                                                 cinema_hall=hall_id)

        return super().get_queryset().filter(enter_time_range, start_date__lte=date.today(),
                                             finish_date__gte=date.today())

        # return super().get_queryset().filter(start_date__lte=date.today(), finish_date__gt=date.today())
