#Este programa calcula los netos de un importe partiendo desde una percepcion y el porcentaje de la cuota por actividad para arba
percepcion = float(input("Ingrese la cantidad percibida : "))
alicuota = float(input("Ingrese la alicuota (%): "))

x = (percepcion*100)/alicuota

print(f"El neto de la percepcion es: {x}")
