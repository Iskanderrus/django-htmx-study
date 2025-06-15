from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import ListView

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

class CheckFilmNameView(View):
    def post(self, request):
        user = request.user
        film_name = request.POST.get('filmname', '').strip()
        if not film_name:
            return HttpResponse(
                """
                <div id='film-errors' style='color:grey;'>Please start typing a film name above</div>
                """
            )
        if user.films.filter(title__icontains=film_name).exists():
            return HttpResponse(
                """
                <div id='film-errors' style='color:red;'>Film probably already exists in your list</div>
                """
            )
        return HttpResponse(
            """
            <div id='film-errors' style='color:green;'>This film is not in your list</div>
            """
        )

class FilmsView(ListView, LoginRequiredMixin):
    template_name = 'films.html'
    model = Film
    context_object_name = 'films'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return user.films.all()
        return Film.objects.none()

class AddFilmView(View):
    def post(self, request):
        film_name = request.POST.get('filmname', '').strip()
        film, _ = Film.objects.get_or_create(title=film_name)
        request.user.films.add(film)
        films = request.user.films.all()
        return render(request, 'partials/film-list.html', {'films': films})
