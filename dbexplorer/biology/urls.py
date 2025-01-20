from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('documentation/', documentation, name='documentation'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('tutorial/', tutorial, name='tutorial'),
]