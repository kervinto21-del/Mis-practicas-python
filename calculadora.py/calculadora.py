print("Hola buen día, soy tu calculadora")
print("Por favor ingresa un número seguido de la operación que deseas realizar seguido de otro número")
print("Las operaciones puedes definirlas de la siguiente manera + - * /")
print("Recuerda que no puedo dividir entre 0 porque me da ansiedad")
def Calculadora(num1, op, num2):
    if op == "+":
       return num1 + num2
    elif op == "-":
       return num1 - num2
    elif op == "*":
       return num1 * num2
    elif op == "/":
       return num1 / num2
num1 = float(input())
op = input()
num2 = float(input())
resultado = Calculadora(num1, op, num2)
print(resultado)



