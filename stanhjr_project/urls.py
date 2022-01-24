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
from django.urls import path, include
from cinema.api.resources import MovieShowViewSet, LogoutAPI, RegisterAPI, GetToken, \
    CinemaHallList, CinemaHallUpdate, PurchaseList, MovieShowPost, MovieShowUpdate
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
    path('', include('cinema.urls')),
 ]
