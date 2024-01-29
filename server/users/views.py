from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.conf import settings

from rest_framework.views import APIView
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from oauth2_provider.models import Application
from oauthlib.common import generate_token
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import AccessToken, RefreshToken

from .serializers import UserRegisterSerializer, UserProfileSerializer

User = get_user_model()

class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        client_id = request.data.get("client_id")

        print(username)
        print(email)
        print(password)
        print(client_id)

        if username:
            if password is None or client_id is None:
                return Response(
                    {"error": "Missing password or client_id."}, status=status.HTTP_400_BAD_REQUEST
                )
            user = authenticate(request, username=username, password=password)
        else:
            if email is None or password is None or client_id is None:
                return Response(
                    {"error": "Missing email, password or client_id."}, status=status.HTTP_400_BAD_REQUEST
                )
            user = authenticate(request, email=email, password=password)
        
        if user is None:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_404_NOT_FOUND)
        
        # Application represents a client that wants to access resources on behalf of a user.
        try:
            app = Application.objects.get(client_id=client_id)
            # app=None
        except:
            return Response({"error": "Invalid client_id."}, status=status.HTTP_404_NOT_FOUND)
        access_token = generate_token()
        refresh_token = generate_token()

        AccessToken.objects.create(
            user=user,
            token=access_token,
            application=app,
            scope=oauth2_settings.DEFAULT_SCOPES,
            expires=timezone.now() + timezone.timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
        )

        RefreshToken.objects.create(
            user=user,
            token=refresh_token,
            application=app,
            access_token=AccessToken.objects.get(token=access_token)
        )
        context = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            # "expires_in": expires_in.total_seconds()
        }

        print(user)
        return Response(context, status=status.HTTP_200_OK)

# CreateAPIView handles POST requests: parse the request data, validate it against serializer and save the new User instance.
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        password = request.data.get("password")
        request.data['password'] = make_password(password)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        app = get_object_or_404(Application, name=settings.APPLICATION_NAME)
        access_token = generate_token()
        refresh_token = generate_token()

        AccessToken.objects.create(
            user=user,
            token=access_token,
            application=app,
            scope=oauth2_settings.DEFAULT_SCOPES,
            expires=timezone.now() + timezone.timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
        )

        RefreshToken.objects.create(
            user=user,
            token=refresh_token,
            application=app,
            access_token=AccessToken.objects.get(token=access_token)
        )

        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

        context = serializer.data.copy()
        context.update(tokens)

        return Response(context, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):
        user = serializer.save()
        if 'new_password' in self.request.data:
            user.set_password(self.request.data['new_password'])
            user.save()

class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        token = request.auth
        if token:
            access_token = AccessToken.objects.filter(token=token)
            if access_token.exists():
                access_token[0].delete()
                return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)
            
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    
class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        # Get the 'next' parameter from the request
        next_page = request.GET.get('next') or '/'
        
        # Pass the 'next' parameter as a query parameter in the redirect URL
        return redirect(f'/social-auth/login/google/?next={next_page}')
    
class LoginSuccessView(APIView):
    def get(self, request):
        next_page = request.GET.get('next') or '/'
        return redirect(next_page)