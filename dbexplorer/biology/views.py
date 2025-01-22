from django.shortcuts import render
from django.http import JsonResponse
import csv
import os

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


# Example species list
def get_species(request):
    # species_list = ["Human", "Mouse", "Dog", "Cat"]
    species_list = get_all_species()
    species_names = [specie['specie_name'] for specie in species_list]
    print(species_names)
    # return JsonResponse({"nodes": species_list})
    return JsonResponse({"nodes": species_names})


# Example sources based on species
def get_sources(request, species):
    sources_data = {
        "Human": ["Source A", "Source B", "Source C"],
        "Mouse": ["Source X", "Source Y", "Source Z"],
        "Dog": ["Source 1", "Source 2", "Source 3"],
        "Cat": ["Source P", "Source Q", "Source R"]
    }
    sources = sources_data.get(species, [])
    return JsonResponse({"sources": sources})


# Example targets based on species and source
def get_targets(request, species, source):
    targets_data = {
        ("Human", "Source A"): ["Target 1", "Target 2", "Target 3"],
        ("Human", "Source B"): ["Target X", "Target Y", "Target Z"],
        ("Mouse", "Source X"): ["Target 5", "Target 6", "Target 7"],
        ("Dog", "Source 1"): ["Target 8", "Target 9"]
    }
    targets = targets_data.get((species, source), [])
    return JsonResponse({"targets": targets})


# Example dataset for species, source, and target
def get_dataset(request, species, source, target):
    # Simulate CSV data for the dataset
    dataset = [
        ["ID", "Value"],
        [1, f"{species}-{source}-{target}-Data1"],
        [2, f"{species}-{source}-{target}-Data2"],
        [3, f"{species}-{source}-{target}-Data3"]
    ]

    # Convert dataset to CSV format
    csv_file = io.StringIO()
    writer = csv.writer(csv_file)
    writer.writerows(dataset)
    csv_data = csv_file.getvalue()

    return JsonResponse({"csv": csv_data})

