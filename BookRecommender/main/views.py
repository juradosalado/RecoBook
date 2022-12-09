from django.shortcuts import render

from main.populateDB import populate

# Create your views here.

def populateDatabase(request):
    (b, g, s)=populate()

    mensaje = 'It has been loaded ' + str(b) + ' books; ' + str(g) + 'genres; ' + str(s) + ' settings.'
    return render(request, 'message.html', {'title': 'End of database load', 'mensaje':mensaje})

    