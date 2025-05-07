import tkinter as tk
from tkinter import messagebox
from threading import Thread
import random
import time
import mysql.connector

class OrdenadorVisual:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Visualizador de Burbuja")
        self.ventana.geometry("800x600")

        self.datos = []
        self.en_proceso = False
        self.velocidad_ms = 100
        self.db = self.conectar_bd()

        self.crear_gui()

    def conectar_bd(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Cortana33",
                database="burbuja",
                auth_plugin="mysql_native_password"
            )
            print("Conexión establecida con la BD.")
            return conexion
        except mysql.connector.Error as e:
            messagebox.showerror("Error de conexión", str(e))
            return None

    def guardar_resultados(self, original, resultado):
        if not self.db:
            return
        try:
            cur = self.db.cursor()
            sql = "INSERT INTO intento_orden (intento, res) VALUES (%s, %s)"
            cur.execute(sql, (str(original), str(resultado)))
            self.db.commit()
            cur.close()
            self.estado.set("Datos guardados exitosamente")
        except mysql.connector.Error as e:
            messagebox.showerror("Error al guardar", str(e))

    def crear_gui(self):
        marco = tk.Frame(self.ventana)
        marco.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        entrada_frame = tk.Frame(marco)
        entrada_frame.pack(fill=tk.X)

        tk.Label(entrada_frame, text="Números separados por comas:").pack(side=tk.LEFT)
        self.entrada = tk.Entry(entrada_frame, width=40)
        self.entrada.pack(side=tk.LEFT, padx=5)
        tk.Button(entrada_frame, text="Cargar", command=self.cargar_datos).pack(side=tk.LEFT)

        botones = tk.Frame(marco)
        botones.pack(fill=tk.X, pady=5)
        tk.Button(botones, text="Aleatorios", command=self.generar_datos).pack(side=tk.LEFT)
        tk.Button(botones, text="Ordenar", command=self.iniciar_ordenamiento).pack(side=tk.LEFT)
        tk.Button(botones, text="Limpiar", command=self.limpiar).pack(side=tk.LEFT)

        tk.Label(botones, text="Velocidad:").pack(side=tk.LEFT, padx=10)
        self.slider = tk.Scale(botones, from_=10, to=500, orient=tk.HORIZONTAL, command=self.actualizar_velocidad)
        self.slider.set(self.velocidad_ms)
        self.slider.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(marco, bg="white", height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.estado = tk.StringVar()
        self.estado.set("Listo para comenzar")
        tk.Label(marco, textvariable=self.estado, relief=tk.SUNKEN, anchor="w").pack(fill=tk.X)

    def actualizar_velocidad(self, valor):
        self.velocidad_ms = int(valor)

    def cargar_datos(self):
        if self.en_proceso:
            return
        try:
            entrada_txt = self.entrada.get()
            self.datos = [int(x.strip()) for x in entrada_txt.split(",") if x.strip()]
            self.dibujar()
            self.estado.set(f"{len(self.datos)} elementos cargados")
        except ValueError:
            messagebox.showerror("Entrada inválida", "Ingrese solo números separados por comas")

    def generar_datos(self):
        if self.en_proceso:
            return
        self.datos = [random.randint(1, 100) for _ in range(20)]
        self.dibujar()
        self.estado.set("Generados 20 números aleatorios")

    def limpiar(self):
        if self.en_proceso:
            return
        self.datos.clear()
        self.canvas.delete("all")
        self.estado.set("Limpio")

    def dibujar(self, resaltados=[]):
        self.canvas.delete("all")
        if not self.datos:
            return

        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        ancho_barra = ancho / len(self.datos)
        maximo = max(self.datos)

        for i, valor in enumerate(self.datos):
            x0 = i * ancho_barra
            y1 = alto - (valor / maximo * (alto - 20))
            x1 = (i + 1) * ancho_barra
            color = "red" if i in resaltados else "blue"
            self.canvas.create_rectangle(x0, alto, x1, y1, fill=color, outline="black")
            self.canvas.create_text(x0 + ancho_barra / 2, y1 - 10, text=str(valor))

        self.canvas.update()

    def burbuja(self):
        if not self.datos:
            return

        self.en_proceso = True
        original = self.datos[:]
        n = len(self.datos)

        for i in range(n):
            for j in range(n - i - 1):
                if self.datos[j] > self.datos[j + 1]:
                    self.datos[j], self.datos[j + 1] = self.datos[j + 1], self.datos[j]
                self.dibujar([j, j+1])
                time.sleep(self.velocidad_ms / 1000)

        self.dibujar()
        self.guardar_resultados(original, self.datos[:])
        self.estado.set("Ordenamiento finalizado")
        self.en_proceso = False

    def iniciar_ordenamiento(self):
        if not self.en_proceso:
            hilo = Thread(target=self.burbuja)
            hilo.daemon = True
            hilo.start()

    def __del__(self):
        if hasattr(self, 'db') and self.db:
            self.db.close()

if __name__ == '__main__':
    ventana = tk.Tk()
    app = OrdenadorVisual(ventana)
    ventana.mainloop()
