from django.shortcuts import render

from main.populateDB import populate

# Create your views here.

def index(request):
    return render(request, 'base_INDEX.html')

def populateDatabase(request):
    (b, g, s)=populate()

    message = 'It has been loaded ' + str(b) + ' books; ' + str(g) + 'genres; ' + str(s) + ' settings.'
    return render(request, 'base_POPULATEDB.html', {'title': 'End of database load', 'message':message})

    