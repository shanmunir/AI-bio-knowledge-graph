from django.shortcuts import render
from django.http import JsonResponse
import csv
import os
import io

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


############################################################################

from django.shortcuts import render
from django.http import JsonResponse

def network(request):
    return render(request, 'biology/network.html')

all_species_with_ids = []
all_sources_with_ids = []
all_targets_with_ids = []

# Example species list
def get_species(request):
    # species_list = ["Human", "Mouse", "Dog", "Cat"]

    global all_species_with_ids
    species_list = get_all_species()
    all_species_with_ids = species_list

    species_names = [specie['specie_name'] for specie in species_list]
    # return JsonResponse({"nodes": species_list})
    return JsonResponse({"nodes": species_names})


# Example sources based on species
def get_sources(request, species):
    global all_species_with_ids
    global all_sources_with_ids
    species_id = int([i['id'] for i in all_species_with_ids if species in i['specie_name']][0])
    sources_data_list = get_sources_by_specie_id(species_id)
    all_sources_with_ids = sources_data_list
    species_data = [source['source_name'] for source in sources_data_list]
    # sources_data = {
    #     "Human": ["Source A", "Source B", "Source C"],
    #     "Mouse": ["Source X", "Source Y", "Source Z"],
    #     "Dog": ["Source 1", "Source 2", "Source 3"],
    #     "Cat": ["Source P", "Source Q", "Source R"]
    # }
    # sources = sources_data.get(species, [])
    # return JsonResponse({"sources": sources})
    return JsonResponse({"sources": species_data})


# Example targets based on species and source
def get_targets(request, species, source):
    global all_species_with_ids
    global all_sources_with_ids
    global all_targets_with_ids
    species_id = int([i['id'] for i in all_species_with_ids if species in i['specie_name']][0])
    source_id = int([i['id'] for i in all_sources_with_ids if source in i['source_name']][0])
    target_data_list = get_target_by_source_and_specie_id(species_id, source_id)
    all_targets_with_ids = target_data_list
    target_data = [target['target_name'] for target in target_data_list]

    # targets_data = {
    #     ("Human", "Source A"): ["Target 1", "Target 2", "Target 3"],
    #     ("Human", "Source B"): ["Target X", "Target Y", "Target Z"],
    #     ("Mouse", "Source X"): ["Target 5", "Target 6", "Target 7"],
    #     ("Dog", "Source 1"): ["Target 8", "Target 9"]
    # }
    # targets = targets_data.get((species, source), [])
    # return JsonResponse({"targets": targets})
    return JsonResponse({"targets": target_data})


# Fetch dataset based on species, source, and target and return dummy values for score and relation
def get_dataset(request, species, source, target):
    # Dummy data generation based on species, source, and target
    dummy_data = {
        "score": "0.85",  # Example dummy score
        "relation": "interaction",  # Example dummy relation
    }

    # Add more logic here if you want to fetch real data from a database or API
    return JsonResponse({
        "species": species,
        "source": source,
        "target": target,
        "score": dummy_data["score"],
        "relation": dummy_data["relation"]
    })

