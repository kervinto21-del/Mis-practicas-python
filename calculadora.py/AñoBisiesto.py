num1 = int(input())
def Bisiesto(num1):
     if (num1 % 4 == 0 and num1 % 100 != 0) or (num1 % 400 == 0):
      return "AÑO BISIESTO"
     else:
        return "NO ES BISIESTO"

Resultado = Bisiesto(num1)
print(Resultado)

