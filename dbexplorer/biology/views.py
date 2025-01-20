from django.shortcuts import render

# Create your views here.


def home(request):
    if request.method == 'POST':
        return render(request, 'biology/extractedData.html')
    return render(request, 'biology/home.html')


def documentation(request):
    return render(request, 'biology/documentation.html')


def about(request):
    return render(request, 'biology/about.html')


def contact(request):
    return render(request, 'biology/contact.html')


def tutorial(request):
    return render(request, 'biology/tutorial.html')