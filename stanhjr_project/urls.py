"""stanhjr_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
import datetime

from cinema.api.resources import MovieShowViewSet, LogoutAPI, RegisterAPI, GetToken, \
    CinemaHallList, CinemaHallUpdate, PurchaseList, MovieShowPOST, MovieShowUpdate
from cinema.views import Login, Register, Logout, MovieListView, ProductBuyView, PurchasedListView, \
    CinemaHallCreateView, CinemaHallUpdateView, MovieShowUpdateView, MovieShowCreateView, CinemaHallListView, \
    real_time_movie
from stanhjr_project.settings import MEDIA_URL, MEDIA_ROOT
from rest_framework import routers
from rest_framework.authtoken import views

router = routers.SimpleRouter()
# router.register(r'hall', CinemaHallViewSet)
router.register(r'session', MovieShowViewSet)
# router.register(r'sell', SellViewSet)
# tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MovieListView.as_view(), name='index'),
    path('ticket-buy/', ProductBuyView.as_view(), name='ticket-buy'),
    path('purchased/', PurchasedListView.as_view(), name='purchased'),
    path('create-hall/', CinemaHallCreateView.as_view(), name='create-hall'),
    path('create-movie/', MovieShowCreateView.as_view(), name='create-movie'),
    path('hall-list/', CinemaHallListView.as_view(), name='hall-list'),
    path('update-hall/<int:pk>/', CinemaHallUpdateView.as_view(), name='update-hall'),
    path('update_movie_show/<int:pk>/', MovieShowUpdateView.as_view(), name='update-movie'),
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('logout/', Logout.as_view(), name='logout'),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += router.urls
urlpatterns += [
    path('api/login/', GetToken.as_view(), name='api_login'),
    path('api/registration/', RegisterAPI.as_view(), name='api_register'),
    path('api/logout/', LogoutAPI.as_view(), name='api_logout'),
    path('api/update_hall/<int:pk>/', CinemaHallUpdate.as_view(), name='cinema_hall_update'),
    path('api/create_hall/', CinemaHallList.as_view(), name='cinema_hall_list'),
    path('api/session/<str:show_day>/', MovieShowViewSet.as_view({'get': 'list',
                                                                'post': 'create'}), name='show_day'),
    path('api/session/', MovieShowViewSet.as_view({'get': 'list',
                                                                'post': 'create'}), name='show_day'),

    path('api/session/<int:pk>/', MovieShowViewSet.as_view({'get': 'list',
                                                          'put': 'update'}), name='show_day'),

    path('api/session_create/', MovieShowPOST.as_view(), name='api-movie_show_create'),
    path('api/session_update/<int:pk>/', MovieShowUpdate.as_view(), name='api-movie_show_update'),
    path('api/purchased/', PurchaseList.as_view(), name='api-purchased'),
    path('realtime/', real_time_movie, name='real-time'),

]

