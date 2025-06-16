from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponsePermanentRedirect, HttpResponseNotAllowed
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DeleteView

from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin


from films.forms import RegisterForm
from films.models import Film, User

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'

class Login(LoginView):
    template_name = 'registration/login.html'

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add check_username_url to context for htmx username validation."""
        context = super().get_context_data(**kwargs)
        context['check_username_url'] = reverse_lazy('check-username')
        return context

class CheckUsernameView(View):
    """View to check if a username already exists using the current user model."""
    def post(self, request):
        username = request.POST.get('username', '').strip()
        UserModel = get_user_model()
        if UserModel.objects.filter(username__iexact=username).exists():
            return HttpResponse(
                """
                <div id='username-errors' style='color:red;'>Username already exists</div>
                <script>
                  document.getElementById('id_password1').setAttribute('disabled', 'disabled');
                  document.getElementById('id_password2').setAttribute('disabled', 'disabled');
                </script>
                """
            )
        return HttpResponse(
            """
            <div id='username-errors' style='color:green;'>Username is available</div>
            <script>
              document.getElementById('id_password1').removeAttribute('disabled');
              document.getElementById('id_password2').removeAttribute('disabled');
            </script>
            """
        )

class FilmsView(LoginRequiredMixin, ListView):
    template_name = 'films.html'
    model = Film
    context_object_name = 'films'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return user.films.all()
        return Film.objects.none()

class AddFilmView(LoginRequiredMixin, View):
    def post(self, request):
        film_name = request.POST.get('filmname', '').strip()
        film, _ = Film.objects.get_or_create(title=film_name)
        request.user.films.add(film)
        films = request.user.films.all()
        return render(request, 'partials/film-list.html', {'films': films})

class DeleteFilmView(LoginRequiredMixin,DeleteView):
    """
    Handles film deletion via DELETE or POST with method override.
    """
    model = Film
    success_url = reverse_lazy('film_list')
    template_name = 'partials/film-list.html'

    def get_queryset(self):
        # this method is being used by sef.get_object in the delete method
        return self.request.user.films.all()

    def delete(self, request, *args, **kwargs):
        request.user.films.remove(self.get_object())
        films = request.user.films.all()
        return render(request, 'partials/film-list.html', {'films': films})

    def dispatch(self, request, *args, **kwargs):
        # this method is being used to handle the DELETE method
        if request.method == 'DELETE':
            return self.delete(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

class SearchForFilmsView(LoginRequiredMixin, View):
    def get(self, request):
        film_name = request.GET.get('filmsearch', '').strip()
        if film_name:
            db_films = Film.objects.filter(title__icontains=film_name)
            return render(request, 'partials/db-film-list.html', {'db_films': db_films})
        else:
            return render(request, 'partials/db-film-list.html', {'db_films': []})

class SearchFilmsView(View):
    """
    Returns a list of films matching the search query for live search, excluding user's films.
    """
    def get(self, request):
        query = request.GET.get('filmsearch', '').strip()
        user_film_ids = request.user.films.values_list('pk', flat=True)
        db_films = Film.objects.filter(title__icontains=query).exclude(pk__in=user_film_ids) if query else []
        return render(request, 'partials/db-film-list.html', {'db_films': db_films})
