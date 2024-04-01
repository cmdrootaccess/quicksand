"""
URL configuration for quicksand project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from quicksand.settings import MEDIA_URL, MEDIA_ROOT
from quicksand_auth.views.auth.views import Register, VerifyRegistrationToken, Login, UsernameCheck, EmailCheck, \
    EmailVerify, PasswordResetRequest, PasswordResetVerify
from quicksand_auth.views.authenticated_user.views import AuthenticatedUser
from quicksand_common.views import Health

auth_auth_patterns = [
    path('register/', Register.as_view(), name='register-user'),
    path('register/verify-token/', VerifyRegistrationToken.as_view(), name='verify-register-token'),
    path('login/', Login.as_view(), name='login-user'),
    path('username-check/', UsernameCheck.as_view(), name='username-check'),
    path('email-check/', EmailCheck.as_view(), name='email-check'),
    path('email/verify/', EmailVerify.as_view(), name='email-verify'),
    path('password/reset/', PasswordResetRequest.as_view(), name='request-password-reset'),
    path('password/verify/', PasswordResetVerify.as_view(), name='verify-reset-password'),
]

auth_user_patterns = [
    path('', AuthenticatedUser.as_view(), name='authenticated-user'),
]

auth_patterns = [
    path('', include(auth_auth_patterns)),
    path('user/', include(auth_user_patterns)),
]

api_patterns = [
    path('auth/', include(auth_patterns)),
]

urlpatterns = [
    path('api/', include(api_patterns)),
    path('admin/', admin.site.urls),
    path('health/', Health.as_view(), name='health'),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
