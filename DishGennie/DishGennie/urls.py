"""
URL configuration for DishGennie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from home import views  # Correctly import views from the home app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signin/', views.signin, name='signin'),  # Sign-in page
    path('signup/', views.signup, name='signup'),  # Sign-up page
    path('', views.home, name='home'),  # Home page
    path('about/', views.about, name='about'),  # About page
    path('contactus/', views.contact, name='contact'),  # Contact page
    path('service/', views.service, name='service'),  # Service page
    path('receipegen/', views.receipegen, name='receipegen'),  # Recipe generator
]
