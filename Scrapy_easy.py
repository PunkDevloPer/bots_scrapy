import os

year = int(input("Ingrese el año de la vulnerabilidad: "))

question = input("¿Sabe el mes de la vulnerabilidad? (y/n): ")

# Limpiar la salida en la consola
os.system('cls' if os.name == 'nt' else 'clear')

if question == "y":
    years = year
    mes = input("Ingrese el número del mes: ")
    mont = input("Ingrese el mes en inglés: ")
    url = f'https://www.cvedetails.com/vulnerability-list/year-{years}/month-{mes}/{mont}.html'
    print(url)
    
else:
    print(f"Mostrando vulnerabilidades generales del año {year}")
    url = "https://www.cvedetails.com/vulnerability-list/year-2023/vulnerabilities.html"
    print(url)
