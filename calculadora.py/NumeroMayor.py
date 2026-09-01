print("Hola buen día, soy tu balanza de valores")
def Comparador (num1, num2):
    if num1 < num2:
      return "num2 es mayor"
    elif num1 > num2:
       return "num1 es mayor"  
num1 = float(input("Ingresa el primero número a comparar: "))
num2 = float(input("Ingresa el segundo número a comparar: "))
Resultado = Comparador (num1, num2)
print(Resultado)