from django.shortcuts import render


def index(request):

    context = {
        'title': 'Home'
    }

    return render(request, 'basic/index.html', context=context)
