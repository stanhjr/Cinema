import datetime
from django.db import transaction
from django.db.models import Q, F
from django.contrib import messages, auth
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from stanhjr_project.settings import SESSION_COOKIE_AGE_ADMIN, SESSION_COOKIE_AGE
from .forms import SignUpForm, ChoiceForm, ProductBuyForm, CinemaHallCreateForm, \
    MovieShowCreateForm, MovieShowUpdateForm
from .models import MovieShow, PurchasedTicket, CinemaHall


class CinemaHallCreateView(PermissionRequiredMixin, UserPassesTestMixin, CreateView):
    permission_required = 'is_superuser'
    model = CinemaHall
    form_class = CinemaHallCreateForm
    success_url = '/hall-list/'
    template_name = 'create_cinema_hall.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('login/')


class MovieShowCreateView(PermissionRequiredMixin, UserPassesTestMixin, CreateView):
    permission_required = 'is_superuser'
    model = MovieShow
    form_class = MovieShowCreateForm
    success_url = '/'
    template_name = 'create_movie.html'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('login/')

    def get_form_kwargs(self):
        kw = super(MovieShowCreateView, self).get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse_lazy('create-movie'))


class CinemaHallUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'is_superuser'
    model = CinemaHall
    form_class = CinemaHallCreateForm
    template_name = 'update_cinema_hall.html'
    success_url = '/hall-list/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('login/')

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.get_tickets():
            messages.warning(self.request, 'В этот зал уже куплены билеты, изменить нельзя')
            return super().form_invalid(form=form)
        obj.save()
        return super().form_valid(form=form)


class CinemaHallListView(PermissionRequiredMixin, ListView):
    permission_required = 'is_superuser'
    model = CinemaHall
    template_name = 'cinema_list.html'
    paginate_by = 6

    def handle_no_permission(self):
        return redirect('login/')


class MovieShowUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = 'is_superuser'
    model = MovieShow
    form_class = MovieShowUpdateForm
    template_name = 'update_movie_show.html'
    success_url = '/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('login/')

    def form_valid(self, form):
        obj = form.save(commit=False)
        if obj.get_purchased():
            messages.warning(self.request, 'На этот сеанс уже куплены билеты, изменить нельзя')
            return super().form_invalid(form=form)

        enter_start_date = Q(start_date__range=(obj.start_date, obj.finish_date))
        enter_finish_date = Q(finish_date__range=(obj.start_date, obj.finish_date))
        enter_start_time = Q(start_time__range=(obj.start_time, obj.finish_time))
        enter_finish_time = Q(finish_time__range=(obj.start_time, obj.finish_time))

        if MovieShow.objects.filter(cinema_hall=obj.cinema_hall).exclude(id=obj.id).filter(
                enter_start_date | enter_finish_date).filter(enter_start_time | enter_finish_time):
            messages.warning(self.request, 'Сеансы в одном зале не могут накладываться друг на друга')
            return super().form_invalid(form=form)

        obj.save()
        return super().form_valid(form=form)

    def get_form_kwargs(self):
        kw = super(MovieShowUpdateView, self).get_form_kwargs()
        kw['request'] = self.request
        return kw


class PurchasedListView(LoginRequiredMixin, ListView):
    model = PurchasedTicket
    template_name = 'purchased.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(PurchasedListView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['all_purchases'] = self.request.user.money_spent
            return context
        return context

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().filter(user=self.request.user.id)
        return super().get_queryset()

    def handle_no_permission(self):
        return redirect('/login/')


class MovieListView(ListView):
    model = MovieShow
    template_name = 'index.html'
    paginate_by = 6
    extra_context = {'ticket_buy_form': ProductBuyForm}

    def get_context_data(self, **kwargs):
        context = super(MovieListView, self).get_context_data(**kwargs)
        context['sort_form'] = ChoiceForm

        if self.request.GET.get('filter_by'):
            context['filter'] = self.request.GET.get('filter_by')

        if self.request.GET.get('show_date') == 'Tomorrow':
            context['date'] = str(datetime.date.today() + datetime.timedelta(days=1))
            context['day'] = 'Tomorrow'

        elif self.request.GET.get('show_date') == 'Today':
            context['date'] = str(datetime.date.today())
            context['day'] = 'Today'
        else:
            context['date'] = str(datetime.date.today())
        return context

    def get_ordering(self):
        filter_by = self.request.GET.get('filter_by')
        if filter_by == 'start_time':
            self.ordering = ['start_time']
        elif filter_by == 'price_max':
            self.ordering = ['ticket_price']
        elif filter_by == 'price_min':
            self.ordering = ['-ticket_price']
        return self.ordering

    def get_queryset(self):
        if self.request.GET.get('show_date') == 'Tomorrow':
            return super().get_queryset().filter(start_date__lte=datetime.date.today() + datetime.timedelta(days=1),
                                                 finish_date__gt=datetime.date.today())
        elif self.request.GET.get('show_date') == 'Today':
            return super().get_queryset().filter(start_date__lte=datetime.date.today(),
                                                 finish_date__gt=datetime.date.today())
        else:
            return super().get_queryset().filter(start_date__lte=datetime.date.today(),
                                                 finish_date__gt=datetime.date.today())


class ProductBuyView(LoginRequiredMixin, CreateView):
    login_url = 'login/'
    http_method_names = ['post', ]
    form_class = ProductBuyForm
    success_url = '/'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        number_of_ticket = int(self.request.POST.get('number_of_ticket'))
        movie_show_id = self.request.POST.get('movie-id')
        obj.movie_show = MovieShow.objects.get(id=movie_show_id)
        obj.user.money_spent += obj.movie_show.ticket_price * number_of_ticket

        if self.request.POST.get('date-buy'):
            obj.date = self.request.POST.get('date-buy')
        else:
            obj.date = str(datetime.date.today())
            obj.purchase_amount = obj.movie_show.ticket_price * number_of_ticket
        with transaction.atomic():
            obj.user.save()
            obj.save()
        return super().form_valid(form=form)

    def get_form_kwargs(self):
        kw = super(ProductBuyView, self).get_form_kwargs()
        kw['request'] = self.request
        return kw

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse_lazy('index'))


class Login(LoginView):
    success_url = '/'
    template_name = 'login.html'

    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        if self.request.user.is_superuser:
            self.request.session.set_expiry(SESSION_COOKIE_AGE_ADMIN)
            return super().form_valid(form)
        else:
            self.request.session.set_expiry(SESSION_COOKIE_AGE)
            return super().form_valid(form)


class Register(CreateView):
    form_class = SignUpForm
    template_name = 'register.html'
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('login')


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = reverse_lazy('login')


def real_time_movie(request):
    current_time = datetime.datetime.now().time()
    count_day = MovieShow.objects.filter(start_time__lte=current_time, finish_time__gte=current_time).count()
    count_night_movie_until_midnight = MovieShow.objects.filter(start_time__gt=F('finish_time'),
                                                                start_time__lte=current_time).count()

    count_night_movie_after_midnight = MovieShow.objects.filter(start_time__gt=F('finish_time'),
                                                                finish_time__gte=current_time).count()

    count = count_day + count_night_movie_after_midnight + count_night_movie_until_midnight

    return HttpResponse(f"Количество активных сеансов {count}")
