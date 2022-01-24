from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from stanhjr_project.settings import SESSION_COOKIE_AGE_ADMIN, SESSION_COOKIE_AGE
from cinema.models import TokenExpired


class TokenExpiredAuth(TokenAuthentication):
    model = TokenExpired

    def authenticate(self, request):
        auth = super().authenticate(request=request)
        if auth:
            user, token = auth
            if user.is_superuser and (timezone.now() - token.last_action).seconds > SESSION_COOKIE_AGE_ADMIN:
                msg = 'Admin session time to dead!'
                raise exceptions.AuthenticationFailed(msg)

            elif user.is_superuser:
                token.last_action = timezone.now()
                token.save()
                return user, token

            if (timezone.now() - token.last_action).seconds > SESSION_COOKIE_AGE:
                msg = 'User session time to dead!'
                raise exceptions.AuthenticationFailed(msg)
            token.last_action = timezone.now()
            token.save()
            return user, token
