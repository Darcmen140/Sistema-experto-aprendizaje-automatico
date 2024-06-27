import tkinter as tk
import sqlite3
from tkinter import messagebox

class SistemaExpertoDescuentos:
    def __init__(self, db_path='base_conocimiento.db'):
        """
        Inicializa el sistema experto con una conexión a la base de datos.
        """
        self.db_path = db_path
        self.conexion = sqlite3.connect(self.db_path)
        self.cursor = self.conexion.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        """
        Crea la tabla de reglas en la base de datos si no existe.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reglas (
                id INTEGER PRIMARY KEY,
                monto_compra TEXT NOT NULL,
                frecuencia TEXT NOT NULL,
                miembro BOOLEAN NOT NULL,
                resultado TEXT NOT NULL
            )
        ''')
        self.conexion.commit()

    def agregar_regla(self, condiciones, resultado):
        """
        Agrega una nueva regla a la base de datos.

        :param condiciones: Diccionario de características que deben cumplirse.
        :param resultado: Descuento a aplicar si se cumplen las condiciones.
        """
        self.cursor.execute('''
            INSERT INTO reglas (monto_compra, frecuencia, miembro, resultado)
            VALUES (?, ?, ?, ?)
        ''', (condiciones['monto_compra'], condiciones['frecuencia'], condiciones['miembro'], resultado))
        self.conexion.commit()

    def cargar_reglas(self):
        """
        Carga todas las reglas desde la base de datos.
        """
        self.cursor.execute('SELECT monto_compra, frecuencia, miembro, resultado FROM reglas')
        return self.cursor.fetchall()

    def evaluar(self, entrada):
        """
        Evalúa la entrada contra las reglas de la base de datos y devuelve el descuento correspondiente.

        :param entrada: Diccionario con las características de la consulta.
        :return: Descuento si se cumple alguna regla, de lo contrario None.
        """
        try:
            if not isinstance(entrada, dict):
                raise ValueError("La entrada debe ser un diccionario de características.")
            reglas = self.cargar_reglas()
            for regla in reglas:
                condiciones = {
                    'monto_compra': regla[0],
                    'frecuencia': regla[1],
                    'miembro': bool(regla[2])
                }
                resultado = regla[3]
                if all(entrada.get(k) == v for k, v in condiciones.items()):
                    return resultado
            return None
        except Exception as e:
            return f"Error: {e}"

class Aplicacion:
    def __init__(self, root):
        self.sistema = SistemaExpertoDescuentos()
        self.crear_base_conocimiento()

        # Configuración de la ventana principal
        self.root = root
        self.root.title("Sistema Experto de Descuentos")

        # Crear y posicionar etiquetas y campos de entrada
        self.label_monto = tk.Label(root, text="Monto de compra (alto/bajo):")
        self.label_monto.grid(row=0, column=0, padx=10, pady=10)
        self.entry_monto = tk.Entry(root)
        self.entry_monto.grid(row=0, column=1, padx=10, pady=10)

        self.label_frecuencia = tk.Label(root, text="Frecuencia de compra (alta/baja):")
        self.label_frecuencia.grid(row=1, column=0, padx=10, pady=10)
        self.entry_frecuencia = tk.Entry(root)
        self.entry_frecuencia.grid(row=1, column=1, padx=10, pady=10)

        self.label_miembro = tk.Label(root, text="¿Es miembro? (True/False):")
        self.label_miembro.grid(row=2, column=0, padx=10, pady=10)
        self.entry_miembro = tk.Entry(root)
        self.entry_miembro.grid(row=2, column=1, padx=10, pady=10)

        # Botón para evaluar la consulta
        self.boton_evaluar = tk.Button(root, text="Evaluar", command=self.evaluar)
        self.boton_evaluar.grid(row=3, column=0, columnspan=2, pady=10)

        # Etiqueta para mostrar el resultado
        self.label_resultado = tk.Label(root, text="")
        self.label_resultado.grid(row=4, column=0, columnspan=2, pady=10)

    def crear_base_conocimiento(self):
        """
       Base de conocimiento agregando reglas al sistema experto.
        """
        base_conocimiento = [
            {'condiciones': {'monto_compra': 'alto', 'frecuencia': 'alta', 'miembro': True}, 'resultado': '20% de descuento'},
            {'condiciones': {'monto_compra': 'alto', 'frecuencia': 'baja', 'miembro': True}, 'resultado': '15% de descuento'},
            {'condiciones': {'monto_compra': 'bajo', 'frecuencia': 'alta', 'miembro': True}, 'resultado': '10% de descuento'},
            {'condiciones': {'monto_compra': 'bajo', 'frecuencia': 'baja', 'miembro': False}, 'resultado': '5% de descuento'},
            # Puedes agregar más reglas aquí
        ]
        
        for regla in base_conocimiento:
            self.sistema.agregar_regla(regla['condiciones'], regla['resultado'])

    def evaluar(self):
        # Obtener valores de los campos de entrada
        monto = self.entry_monto.get().strip().lower()
        frecuencia = self.entry_frecuencia.get().strip().lower()
        miembro = self.entry_miembro.get().strip().lower() == 'true'

        # Crear la consulta como un diccionario
        consulta = {
            'monto_compra': monto,
            'frecuencia': frecuencia,
            'miembro': miembro
        }

        # Evaluar la consulta
        resultado = self.sistema.evaluar(consulta)

        # Mostrar el resultado en la etiqueta
        self.label_resultado.config(text=f"Resultado: {resultado}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
