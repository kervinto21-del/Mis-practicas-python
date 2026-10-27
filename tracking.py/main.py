# app_transporte_con_gps.py

import os
import pandas as pd
import heapq

from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy_garden.mapview import MapView, MapMarker
from kivy.clock import Clock

from plyer import gps
from kivy.utils import platform
from kivy.uix.popup import Popup
from kivy.uix.label import Label


# --- Constantes y configuración

APP_NAME = "Transporte Urbano Caracas"
TARIFA_BASE_BS = 220
ARCHIVO_CONDUCTORES = "conductores.xlsx"
PARADAS = [
    "Coche", "IPSFA", "San Mónica", "Los Símbolos",
    "Plaza Venezuela", "Chacaíto", "La Hoyada", "Petare",
    "Metro Chacao / Frente al Sambil"
]


# --- Backend simulado y lógica de grafo

def asegurar_archivo(path, columnas):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=columnas)
        df.to_excel(path, index=False)
        print(f"[INFO] Archivo creado: {path}")

class BackendSimulado:
    def __init__(self):
        asegurar_archivo(ARCHIVO_CONDUCTORES, ["Nombre", "Placa", "Linea"])

    def agregar_conductor(self, nombre, placa, linea):
        df = pd.read_excel(ARCHIVO_CONDUCTORES)
        nuevo = {"Nombre": nombre, "Placa": placa, "Linea": linea}
        df = df.append(nuevo, ignore_index=True)
        df.to_excel(ARCHIVO_CONDUCTORES, index=False)
        print(f"[INFO] Conductor agregado: {nuevo}")

    def leer_conductores(self):
        return pd.read_excel(ARCHIVO_CONDUCTORES)

class GrafoTransporte:
    def __init__(self):
        self.nodos = {
            "Coche": [("IPSFA", 3.2, "L1"), ("Plaza Venezuela", 6.5, "L2"), ("Los Símbolos", 5.0, "L3")],
            "IPSFA": [("Coche", 3.2, "L1"), ("San Mónica", 2.0, "L1")],
            "San Mónica": [("IPSFA", 2.0, "L1"), ("Chacaíto", 7.0, "L1")],
            "Los Símbolos": [("Coche", 5.0, "L3"), ("Plaza Venezuela", 2.5, "L3"), ("Chacaíto", 4.0, "L3")],
            "Plaza Venezuela": [("Coche", 6.5, "L2"), ("Los Símbolos", 2.5, "L3"), ("La Hoyada", 1.8, "L2"), ("Chacaíto", 4.0, "L2")],
            "Chacaíto": [("San Mónica", 7.0, "L1"), ("Los Símbolos", 4.0, "L3"), ("Plaza Venezuela", 4.0, "L2"), ("Petare", 9.0, "L4")],
            "La Hoyada": [("Plaza Venezuela", 1.8, "L2"), ("Petare", 10.0, "L4")],
            "Petare": [("Chacaíto", 9.0, "L4"), ("La Hoyada", 10.0, "L4")],
            "Metro Chacao / Frente al Sambil": [("Chacaíto", 1.5, "L3"), ("Plaza Venezuela", 3.0, "L2")]
        }

    def calcular_ruta_corta(self, origen, destino):
        heap = [(0, origen, [], [])]
        visitados = {}
        while heap:
            dist_acum, nodo, ruta, lineas = heapq.heappop(heap)
            if nodo == destino:
                return ruta + [nodo], dist_acum, lineas
            if nodo in visitados and visitados[nodo] <= dist_acum:
                continue
            visitados[nodo] = dist_acum
            for vecino, distancia, linea in self.nodos.get(nodo, []):
                nuevo_dist = dist_acum + distancia
                nueva_ruta = ruta + [nodo]
                nuevas_lineas = list(lineas)
                if not nuevas_lineas or linea != nuevas_lineas[-1]:
                    nuevas_lineas.append(linea)
                heapq.heappush(heap, (nuevo_dist, vecino, nueva_ruta, nuevas_lineas))
        return [], float('inf'), []

    def calcular_tarifa(self, lineas_usadas):
        return len(set(lineas_usadas)) * TARIFA_BASE_BS


# --- Pantallas KivyMD

from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton

class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", padding=dp(50), spacing=dp(30))
        label = MDLabel(text=f"Bienvenido a {APP_NAME}", halign="center", font_style="H4")
        btn_conductor = MDRaisedButton(text="Soy Conductor", pos_hint={"center_x":0.5})
        btn_pasajero = MDRaisedButton(text="Soy Pasajero", pos_hint={"center_x":0.5})

        btn_conductor.bind(on_release=self.ir_conductor)
        btn_pasajero.bind(on_release=self.ir_usuario)

        layout.add_widget(label)
        layout.add_widget(btn_conductor)
        layout.add_widget(btn_pasajero)

        self.add_widget(layout)

    def ir_conductor(self, instance):
        self.manager.current = "conductor_screen"

    def ir_usuario(self, instance):
        self.manager.current = "pasajero_screen"


from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView

class PasajeroScreen(Screen):
    def __init__(self, backend, grafo, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend
        self.grafo = grafo

        layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        label = MDLabel(text="Seleccione Origen y Destino", halign="center", font_style="H5")
        self.spinner_origen = MDFlatButton(text="Origen")
        self.spinner_destino = MDFlatButton(text="Destino")

        self.menu_origen = MDDropdownMenu(
            caller=self.spinner_origen,
            width_mult=4,
            max_height=dp(200),
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": item,
                    "height": dp(40),
                    "on_release": lambda x=item: self.set_origen(x)
                } for item in PARADAS
            ],
        )

        self.menu_destino = MDDropdownMenu(
            caller=self.spinner_destino,
            width_mult=4,
            max_height=dp(200),
            items=[
                {
                    "viewclass": "OneLineListItem",
                    "text": item,
                    "height": dp(40),
                    "on_release": lambda x=item: self.set_destino(x)
                } for item in PARADAS
            ],
        )

        self.spinner_origen.bind(on_release=self.menu_origen.open)
        self.spinner_destino.bind(on_release=self.menu_destino.open)

        btn_buscar = MDRaisedButton(text="Buscar Ruta", size_hint=(1, None), height=dp(50))
        btn_buscar.bind(on_release=self.buscar_ruta)

        self.resultados_scroll = ScrollView()
        self.resultados_container = MDBoxLayout(
            orientation="vertical", padding=dp(10),
            size_hint_y=None, spacing=dp(10)
        )
        self.resultados_container.bind(minimum_height=self.resultados_container.setter('height'))
        self.resultados_scroll.add_widget(self.resultados_container)

        layout.add_widget(label)
        layout.add_widget(self.spinner_origen)
        layout.add_widget(self.spinner_destino)
        layout.add_widget(btn_buscar)
        layout.add_widget(self.resultados_scroll)

        self.add_widget(layout)

    def set_origen(self, texto):
        self.spinner_origen.text = texto
        self.menu_origen.dismiss()

    def set_destino(self, texto):
        self.spinner_destino.text = texto
        self.menu_destino.dismiss()

    def buscar_ruta(self, instance):
        self.resultados_container.clear_widgets()
        origen = self.spinner_origen.text
        destino = self.spinner_destino.text

        if origen == "Origen" or destino == "Destino":
            self.resultados_container.add_widget(MDLabel(text="Seleccione ambos origen y destino."))
            return
        if origen == destino:
            self.resultados_container.add_widget(MDLabel(text="Origen y destino no pueden ser iguales."))
            return

        ruta, distancia, lineas = self.grafo.calcular_ruta_corta(origen, destino)
        if not ruta:
            self.resultados_container.add_widget(MDLabel(text="No se encontró ruta."))
            return

        tarifa = self.grafo.calcular_tarifa(lineas)
        texto = f"Ruta: {' → '.join(ruta)}\nDistancia: {distancia:.2f} km\nLíneas usadas: {', '.join(lineas)}\nTarifa: Bs {tarifa}"
        self.resultados_container.add_widget(MDLabel(text=texto))


class ConductorScreen(Screen):
    def __init__(self, backend, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend

        layout = MDBoxLayout(orientation="vertical", padding=dp(30), spacing=dp(15))
        label = MDLabel(text="Registro de Conductor", halign="center", font_style="H5")
        self.input_nombre = MDTextField(hint_text="Nombre")
        self.input_placa = MDTextField(hint_text="Placa")
        self.input_linea = MDTextField(hint_text="Línea/Ruta")

        btn_registrar = MDRaisedButton(text="Registrar")
        btn_registrar.bind(on_release=self.registrar)

        layout.add_widget(label)
        layout.add_widget(self.input_nombre)
        layout.add_widget(self.input_placa)
        layout.add_widget(self.input_linea)
        layout.add_widget(btn_registrar)

        self.add_widget(layout)

    def registrar(self, instance):
        nombre = self.input_nombre.text.strip()
        placa = self.input_placa.text.strip()
        linea = self.input_linea.text.strip()

        if not nombre or not placa or not linea:
            print("Complete todos los campos")
            return
        self.backend.agregar_conductor(nombre, placa, linea)
        print(f"Conductor registrado: {nombre}")
        self.input_nombre.text = ""
        self.input_placa.text = ""
        self.input_linea.text = ""


# --- Pantalla nueva para mapa y GPS

from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel

from kivy.uix.screenmanager import Screen
from kivy_garden.mapview import MapView, MapMarker
from kivy.utils import platform
from kivy.uix.popup import Popup
from kivymd.uix.label import MDLabel


class MapaGPSScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapview = MapView(zoom=12, lat=10.5, lon=-66.9)  # Coordenadas aproximadas de Caracas
        self.add_widget(self.mapview)

        # Marcador sin imagen para evitar error
        self.gps_marker = MapMarker(lat=10.5, lon=-66.9)
        self.mapview.add_widget(self.gps_marker)

        if platform == 'android':
            from plyer import gps
            self.gps = gps
            self.gps.configure(on_location=self.on_location, on_status=self.on_status)
            self.gps.start(minTime=1000, minDistance=0)
        else:
            # Modo simulación para escritorio
            popup = Popup(
                title='GPS no disponible',
                content=MDLabel(text='GPS no implementado en esta plataforma.\nUsando posición simulada.'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            # Actualizar marcador a posición simulada cada 5 segundos
            from kivy.clock import Clock
            self.sim_lat = 10.5
            self.sim_lon = -66.9
            Clock.schedule_interval(self.update_simulated_location, 5)

    def update_simulated_location(self, dt):
        # Aquí podrías cambiar valores para simular movimiento
        self.gps_marker.lat = self.sim_lat
        self.gps_marker.lon = self.sim_lon
        self.mapview.center_on(self.sim_lat, self.sim_lon)

    def on_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            self.gps_marker.lat = lat
            self.gps_marker.lon = lon
            self.mapview.center_on(lat, lon)

    def on_status(self, stype, status):
        print('GPS status:', stype, status)



# --- App principal: cargar screens y ejecutar

from kivy.utils import platform

class TransporteApp(MDApp):
    def build(self):
        self.backend = BackendSimulado()
        self.grafo = GrafoTransporte()

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(WelcomeScreen(name="welcome_screen"))
        sm.add_widget(PasajeroScreen(self.backend, self.grafo, name="pasajero_screen"))
        sm.add_widget(ConductorScreen(self.backend, name="conductor_screen"))
        sm.add_widget(MapaGPSScreen(name="mapa_gps_screen"))

        return sm

if __name__ == "__main__":
    TransporteApp().run()
