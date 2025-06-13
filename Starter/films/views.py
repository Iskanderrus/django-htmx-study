from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
import time

from films.forms import RegisterForm
from films.models import User

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
        exists = UserModel.objects.filter(username__iexact=username).exists()
        if exists:
            return HttpResponse("<div id='username-errors' style='color:red;'>Username already exists</div>")
        return HttpResponse("<div id='username-errors' style='color:green;'>Username is available</div>")
