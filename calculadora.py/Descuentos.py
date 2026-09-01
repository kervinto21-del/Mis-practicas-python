num1 = float(input("Ingresa el monto total del producto: "))
num2 = float(input("Ingresa la cantidad del descuento: "))
multi = num1 - ((num1 * num2) / 100)
print ("El monto total a cancelar es", multi)
