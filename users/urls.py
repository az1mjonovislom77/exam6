from django.urls import path
from users import views
from users.views import RegisterView, EmailPageView

app_name = 'users'

urlpatterns = [
    path('login/', views.login_page, name='login_page'),
    path('register/', RegisterView.as_view(), name='register_page'),
    path('logout/', views.logout_page, name='logout_page'),
    path('email-page/', EmailPageView.as_view(), name='email_page'),
]
