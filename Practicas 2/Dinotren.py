from difflib import get_close_matches
print("Base de datos de Dinotren Park")
Dinotren = {
    "Tyrannosaurus_Rex" : {
                    "Nombre": "Tyrannosaurus Rex",
                    "Especie": "Rex",
                    "Dieta": "Carnivore",
                    "Periodo": "Cretaceous"},
    "Velociraptor": {
                    "Nombre": "Velociraptor",
                    "Especie": "Raptor",
                    "Dieta": "Carnivore",
                    "Periodo": "Cretaceous"},
    "Triceratops": {
                    "Nombre": "Triceraptos",
                    "Especie": "Prorsus",
                    "Dieta": "Herbivore",
                    "Periodo": "Cretaceous"},
    "Brachiosaurus": {
                    "Nombre": "Brachiosaurus",
                    "Especie": "Brachiosaurus",
                    "Dieta": "Herbivore",
                    "Periodo": "Jurassic"},
    "Stegosaurus": {
                    "Nombre": "Stegosaurus",
                    "Especie": "Armatus",
                    "Dieta": "Herbivore",
                    "Periodo": "Jurassic"},
    "Herbivore": {
                  "1": "Stegosaurus",
                  "2": "Brachiosauru",
                  "3": "Triceratops"},
    "Carnivore": {
                 "1": "Tyrannosaurus Rex",
                 "2": "Velociraptor"},
    "Period Jurassic": {
                "1": "Stegosaurus",
                "2": "Brachiosaurus"},
    "Period Cretaceous": {
                "1":"Triceratops",
                "2": "Velociraptor",
                "3": "Tyrannosaurus Rex"}
}


def buscar_dinosaurio():
    Busqueda = input("Ingresa el nombre clave de lo que deseas buscar:  ").lower().strip()
    Nombres_correctos = list(Dinotren.keys())
    coincidencias = get_close_matches(Busqueda, Nombres_correctos, n=1, cutoff=0.5)
    if coincidencias:
        dino_encontrado = coincidencias[0]
        datos = Dinotren[dino_encontrado]
        for clave, valor in datos.items():
            print (f"{clave}: {valor}")
    else:
            print ("Busqueda invalida")
while True:
     Accion = input("Hola, por favor ingresa 1 para buscar información o ingresa 0 si deseas finalizar la busqueda:  ")
     if Accion == "0":
          print ("bye bye")
          break
     else:
         buscar_dinosaurio()





