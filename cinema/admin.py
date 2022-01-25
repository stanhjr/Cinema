from django.contrib import admin
from django.contrib.auth.signals import user_logged_in
from stanhjr_project import settings
from .models import CinemaHall, PurchasedTicket, MovieShow


def login_hook(sender, **kwargs):
    settings.SESSION_COOKIE_AGE = settings.SESSION_COOKIE_AGE_ADMIN


admin.site.register(CinemaHall)
admin.site.register(PurchasedTicket)
admin.site.register(MovieShow)
user_logged_in.connect(login_hook)
