import csv
from main.models import Book


def prueba(archivo):
    Book.objects.all().delete()
    
    lista=[]
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                b=Book(title=row[1], series=row[2],author=row[3], average_rating=float(row[4]), description=row[5])
                lista.append(b)
                print("Sinopsis: " + row[5])
                print("===========\n")
        Book.objects.bulk_create(lista)
    except FileNotFoundError:
        print("El archivo no existe")

res = remover_saltos_linea("data\\books.csv")