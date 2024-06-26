from django.urls import path
from .views import UserRegisterView, LoginView, LogoutView, UserProfileView, GoogleLoginView, LoginSuccessView

app_name = 'users'

urlpatterns = [
    # User registration endpoint
    path('register/', UserRegisterView.as_view(), name='register'),

    # User profile retrieval and update endpoint
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Login endpoint
    path('login/', LoginView.as_view(), name='login'),

    # Google OAuth2 login endpoint
    path('login/google/', GoogleLoginView.as_view(), name='google-login'),

    # Logout endpoint
    path("logout/", LogoutView.as_view(), name="logout"),

    path("login-success/", LoginSuccessView.as_view(), name="login-success")
]
