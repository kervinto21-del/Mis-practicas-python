num1 = int(input())
num2 = 2
op = "%"
def Numero (num1, op, num2):
    if num1 % num2 == 1:
        return "IMPAR"
    elif num1 % num2 == 0:
        return "PAR"
Resultado = Numero (num1, op, num2)
print(Resultado)











