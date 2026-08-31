print("Hola buen día, soy tu balanza de valores")
print("Por favor ingresa los números a comparar")
def Comparador (num1, num2):
    if num1 < num2:
      return "num2 es mayor"
    elif num1 > num2:
       return "num1 es mayor"  
num1 = float(input())
num2 = float(input())
Resultado = Comparador (num1, num2)
print(Resultado)