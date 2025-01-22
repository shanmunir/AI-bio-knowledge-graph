from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('documentation/', documentation, name='documentation'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('tutorial/', tutorial, name='tutorial'),
    path('network/', network, name='network'),
    path('network/get_species/', get_species, name='get_species'),
    path('network/get_sources/<str:species>/', get_sources, name='get_sources'),
    path('network/get_targets/<str:species>/<str:source>/', get_targets, name='get_targets'),
    path('network/get_dataset/<str:species>/<str:source>/<str:target>/', get_dataset, name='get_dataset'),
]