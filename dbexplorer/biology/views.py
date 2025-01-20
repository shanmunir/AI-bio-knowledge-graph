from django.shortcuts import render

from .models import Species
from .utils import  *

# Create your views here.


def home(request):
    species_list  = get_all_species()
    # source_list = get_sources_by_specie_id(3)
    # target_list = get_target_by_source_and_specie_id(3,8)
    # data = get_unique_relations_list(3,8,5)
    if request.method == 'POST':
        return render(request, 'biology/extractedData.html')
    return render(request, 'biology/home.html', {'species_list': species_list})


def documentation(request):
    return render(request, 'biology/documentation.html')


def about(request):
    return render(request, 'biology/about.html')


def contact(request):
    return render(request, 'biology/contact.html')


def tutorial(request):
    return render(request, 'biology/tutorial.html')