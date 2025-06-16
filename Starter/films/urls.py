from django.urls import path
from films import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("films/", views.FilmsView.as_view(), name="film_list"),
]

htmx_urlpatterns = [
    path("check-username/", views.CheckUsernameView.as_view(), name="check-username"),
    path("add-film/", views.AddFilmView.as_view(), name="add_film"),
    path("delete-film/<int:pk>/", views.DeleteFilmView.as_view(), name="delete_film"),
]

urlpatterns += htmx_urlpatterns
