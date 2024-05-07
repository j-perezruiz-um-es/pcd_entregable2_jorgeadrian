import functools
import random
from datetime import datetime
from math import sqrt
import time
from abc import ABC, abstractmethod
import threading
# -----------------------
# EXPLICACIONES DEL PROGRAMA
# -----------------------

'''
Los cultivos de invernadero más comunes requieren un rango de temperatura 
de alrededor de 18º-24ºC, por tanto, estableceremos un rango de -10 y +10 de este intervalo
para que sea logica la temperatura y se cumplan las condiciones propuestas del problema
'''

# -----------------------
# CLASES
# ----------------------- 

# R2
# Se trata de un Observer para que notifique al sistema un nuevo valor de temperatura con su fecha cada 5 segundos
# En esta clase podremos registrar el observer, eliminarlo y notificar a los observadores sobre cada actualizacion de los valores
class Observable:
    def __init__(self):
        self._observers = []

    def register_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def notify_observers(self, date_temp):
        for observer in self._observers:
            observer.update(date_temp)

# El Sensor de temperatura que obtendra la tupla (timestamp, t) y notificara de cada actualizacion
class Sensor(Observable):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.running = True                                             # Variable para poder salir del programa
        self.pause_event = threading.Event()                            # Variable para poder pausar y reaunudar el programa
    
    # Funcion que inicia el proceso de obtencion de la tupla (timestamp, t) cada 5 segundos    
    def run(self):
        while self.running:
            self.pause_event.wait()                                     # Espera a a que se reanude el proceso, mientras esta paausado
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    # Obtiene la fecha actual
            temperature = random.randint(8, 34)                         # Obtiene una temperatura random en el intervalo (8, 34)            
            date_temp = (timestamp, temperature)                        # Formamos la tupla
            self.notify_observers(date_temp)                            # Notifica al observer la tupla obtenida
            time.sleep(5)                                               # Espera 5 segundos antes de generar la proxima temperatura
    
    # Funcion para pausar el programa (la funcion run)
    def pause(self):
        self.pause_event.clear()
    
    # Funcion para reaunudar el programa (la funcion run)
    def resume(self):
        self.pause_event.set()

    # Funcion para salir del progrmama (termina la funcion run poniendo la variable del while False)
    def exit(self):
        self.running = False

# Observer con la funcion update
class Observer(ABC):
    @abstractmethod
    def update(self, date_temp):
        pass

# R1 
# Se trata de un Singleton para que gestione todos los componentes y recursos del entorno en unica instancia
# En este caso tambien, es el operador del observer para que reciba las actualizaciones de datos a tiempo real
class SistemaIoT(Observer):
    __instance = None                                                           # Inicializamos la unica instancia a None
    
    def __init__(self, manager_chain):
        if SistemaIoT.__instance != None:                                       # Solo puede haber una instancia
            raise Exception('No puede haber mas de una instancia del sistema')
        else:
            self.manager_chain = manager_chain                                  # Variable que habra que indicar al inicializar el sistema para indicar el manejador que empiza el chain responsability
            self.date_temp = []                                                 # Variable para almacenar cada tupla (timestamp, t) nueva
            self.date = []                                                      # Variable para almacenar cada timestamp de date_temp
            self.temp = []                                                      # Variable para almacenar cada t de date_temp
    
    # Metodo de clase para obtener la instancia
    @classmethod
    def obtener_instancia(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance
    
    # Funcion que va actualizando cada lista cuando recibe una tupla (timestamp, t)(=date_temp) nueva
    def update(self, date_temp):
        self.date.append(date_temp[0])                                          # En el primer elemento de la tupla se encuentra la fecha
        self.temp.append(date_temp[1])                                          # En el segundo elemento de la tupla se encuentra la temperatura
        self.date_temp.append(date_temp)                                        # Añadimos cada tupla a la lista vacia por si queremos obtener todos los datos en algun momento
        self.manager_chain.manejar_date_temp(self.date, self.temp)              # Empezamos a manejar estos datos (las listas date y temp por separado) para la obtencion del resultado del manejador que hemos inicializado en el SistemaIoT
    
    # Funcion para obtener todas las tuplas generadas
    def get_date_temp(self):
        return self.date_temp
    
    # Funcion para obtener todas las fechas generadas
    def get_date(self):
        return self.date_temp
    
    # Funcion para obtener todas las temperaturas generadas
    def get_temp(self):
        return self.date_temp

# R3
# Se trata de un Chain of Responsability que obtendra las dos listas (date y temp) desde la funcion de update que hemos visto anteriormente
# Iniciamos con la clase Manejador para poder definir cada sucesor que va despues de cada paso y formar asi una cadena y obtener los datos del sistema
class Manejador(ABC):
    def __init__(self, sucesor=None):
        self.sucesor : Manejador = sucesor
    
    @abstractmethod    
    def manejar_date_temp(self, date, temp):
        pass

# Definimos cada paso encadenado que son herencia de la clase Manejador y en cada paso se indica que si tiene un sucesor que pase a realizar ese manejador sucesor
# Este sera el ultimo paso, la clase Aumento, que comprueba si durante los últimos 30 segundos la temperatura ha aumentado más de 10 grados centígrados.
class Aumento(Manejador):
    def manejar_date_temp(self, date, temp):
        n = len(temp)
        if n >=6:
            ultima_temperatura = temp[-1]
            temperatura_30seg = temp[-6]
            if (ultima_temperatura - temperatura_30seg) > 10:
                print('Ultimos 30 segundos:\tLa temperatura ha aumentado mas de 10 grados')

        if self.sucesor:
            self.sucesor.manejar_date_temp(date, temp)

# Este sera el segundo paso, la clase Umbral, que comprueba si la temperatura actual del invernadero está por encima de un umbral que hemos definido
class Umbral(Manejador):
     def manejar_date_temp(self, date, temp):
        umbral = 28                                                 # Hemos indicado como umbral los 28 grados centigrados (es modificabel)
        temperatura_actual = temp[-1]
        if temperatura_actual > umbral:
            print('Temperatura actual:\tPor encima del umbral')

        if self.sucesor:
            self.sucesor.manejar_date_temp(date, temp)

# R4
# Este sera el primer paso de la chain responsability, la clase ContextoEstadisticos, que tambien seria el contexto del patron Strategy
# Aqui es donde se inicia la ultima regla en la que en el contexto podremos elgir la distinta estrategia que queremos para el analisis de las temperaturas del sensor
class ContextoEstadisticos(Manejador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)
        self.strategy = None                                # Variable que obtiene la estrategia que seguiremos
    
    # Funcion para definir la estrategia que queremos seguir
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    # Funcion del Manejador para obtener las listas actualizadas y realizar la estrategia de este paso encadenado
    def manejar_date_temp(self, date, temp):
        if self.strategy is not None:                       # Si existe una estrategia, que la ejecute
            self.strategy.execute(date, temp)
        
        if self.sucesor:                                    # Si existe un sucesor en la cadena, que realize el manejador sucesor
            self.sucesor.manejar_date_temp(date, temp)

# Iniciamos la clase Strategy para realizar la funcion execute y realice una de las estrategia que deseemos
class Strategy(ABC): 
    @abstractmethod    
    def execute(self, date, temp):
        pass

# Definimos cada estrategia que seran herencias de la clase Strategy
# La siguiente estrategia calcula la media y la desviacion tipica de la lista de temperaturas de los ultimos 60 segundos
class StrategyMeanSd(Strategy):
    def execute(self, date, temp):
        n = len(temp)
        mean = functools.reduce(lambda x, y: x+y, temp)/ n              # Calculo de la media
        sd = sqrt(sum(map(lambda x: (x - mean) ** 2, temp)) / n)        # Calculo de la desviacion tipica
        
        # Una vez pasados los 60 segundos eliminamos la ultima temperatura ya que no la necesitamos para nuestro analisis
        if n > 12:
            temp.pop(0)
        
        # Mostramos por pantalla
        print(f"Fecha: {date[-1]}")
        print(f"Ultimos 60 segundos:\tMedia: {round(mean, 2)}\tDesviacion Tipica: {round(sd, 2)}")

# La siguiente estrategia calcula Q1, Mediana y Q2 de la lista de temperaturas de los ultimos 60 segundos
class StrategyCuantil(Strategy):
    def execute(self,  date, temp):
        n = len(temp)
        temp_ordenada = sorted(temp)
        Q1 = temp_ordenada[n//4] if n%2 != 0 else (temp_ordenada[n//4-1] + temp_ordenada[n//4])/2           # Calculo de Q1
        mediana = temp_ordenada[n//2] if n%2 != 0 else (temp_ordenada[n//2-1] + temp_ordenada[n//2])/2      # Calculo de la Mediana
        Q3 = temp_ordenada[3*n//4] if n%2 != 0 else (temp_ordenada[3*n//4-1] + temp_ordenada[3*n//4])/2     # Calculo de Q3
        
        # Una vez pasados los 60 segundos eliminamos la ultima temperatura ya que no la necesitamos para nuestro analisis
        if n > 12:
            temp.pop(0)
        
        # Mostramos por pantalla
        print(f"Fecha: {date[-1]}")
        print(f"Ultimos 60 segundos:\tQ1: {Q1}\tMediana: {mediana}\tQ3: {Q3}")

# La siguiente estrategia calcula el maximo y el minimo de la lista de temperaturas de los ultimos 60 segundos
class StrategyMaxMin(Strategy):
    def execute(self,  date, temp):
        n = len(temp)
        maximo = functools.reduce(lambda x, y: x if x > y else y, temp)     # Calculo del maximo
        minimo = functools.reduce(lambda x, y: x if x < y else y, temp)     # Calculo del minimo
        
        # Una vez pasados los 60 segundos eliminamos la ultima temperatura ya que no la necesitamos para nuestro analisis
        if n > 12:
            temp.pop(0)
        
        # Mostramos por pantalla
        print(f"Fecha: {date[-1]}")
        print(f"Ultimos 60 segundos:\tMaximo: {maximo}\tMinimo: {minimo}") 

# -----------------------
# SISTEMA DE GESTION
# ----------------------- 
if __name__ == '__main__':
    
    # Definimos las diferentes estrategias y construimos la cadena de responsabilidades en el orden como se indica en el problema
    meansd = StrategyMeanSd()
    maxmin = StrategyMaxMin()
    cuantil = StrategyCuantil()
    aumento = Aumento()
    umbral = Umbral(aumento)
    contexto = ContextoEstadisticos(umbral)
    
    # Menu principal del sistema para establecer el nombre del sensor y la estrategia con la que se quiere inicializar el programa    
    print("¡Bienvenido al SistemaIOT!")
    name = input("- Introduce el nombre del sensor de temperatura: ")
    print("INORMACION GENERAL:")
    print("\t- Cada 5 segundos se le mostrara la fecha y hora actual, un estadistico calculado que debera elegir y si se han cumplido las siguientes condiciones")
    print("\t\t· Primera condicion -> ¿La temperatura actual ha superado el umbral?")
    print("\t\t· Segunda condicion -> ¿En los ultimos 30 segundos, la temperatura ha aumentado mas de 10 grados?")
    print("\t- En 60 segundos obtendra un Menu por si quere salir, cambiar de estrategia o seguir igual")
    print("ESTRATEGIAS DE CALCULO DE LAS TEMPERATURAS DE LOS ULTIMOS 60 SEGUNDOS:")
    print("1: Obtener la media y desviacion tipica")
    print("2: Obtener los cuantiles")
    print("3: Obtener el maximo y el minimo")
    while True:
        estrategia = int(input("Introduce el numero de la estrategia que deseas emplear: "))
        if estrategia == 1:
            contexto.set_strategy(meansd)
            break
        elif estrategia == 2:
            contexto.set_strategy(cuantil)
            break
        elif estrategia == 3:
            contexto.set_strategy(maxmin)
            break
        else:
            print("No existe esta estrategia por el momento, intentalo de nuevo.")
    print("Cargando...")

    # Definimos el sensor y el operador que sera el Sistema con su manejador de iniciacion 
    sensor_temperatura = Sensor(name)
    operator = SistemaIoT(contexto)
    sensor_temperatura.register_observer(operator)              # Registramos el operador
    thread = threading.Thread(target=sensor_temperatura.run)    # Iniciamos el sensor desde un hilo
    thread.start()                                              # Empezamos a ejecutar el hilo
    sensor_temperatura.resume()                                 # Reunudamos el sensor para que ya empieze a funcionar la funcion run del sensor
    
    # En 60 segundos (modificable) se pausa el sensor y se abre el siguiente menu con distintas opciones
    time.sleep(60)
    sensor_temperatura.pause()
    print("\nMENU")
    print("Opcion 1: Seguir obteniendo informacion con la misma estrategia")
    print("Opcion 2: Cambiar de estrategia")
    print("Opcion 3: Salir (aparecera la ultima informacion obtenida)")
    while True:
        opcion = int(input("Introduce el numero de la opcion: "))
        if opcion == 1:
            sensor_temperatura.resume()                         # Reanuda el programa
            break
        elif opcion == 2:
            while True:
                estrategia = int(input("Introduce el numero de la estrategia que deseas emplear: "))
                if estrategia == 1:
                    contexto.set_strategy(meansd)
                    break
                elif estrategia == 2:
                    contexto.set_strategy(cuantil)
                    break
                elif estrategia == 3:
                    contexto.set_strategy(maxmin)
                    break
                else:
                    print("No existe esta estrategia por el momento, intentalo de nuevo.")
            sensor_temperatura.resume()                         # Reanuda el programa
            break
        elif opcion == 3:
            sensor_temperatura.resume()                         # Antes de salir hay que reanudar el programa
            sensor_temperatura.exit()                           # Salir del programa
            thread.join()                                       # Al salir del programa se debe devolver los ultimos datos obtenidos en el hilo
            break
        else:
            print("No existe esta opcion por el momento, intentalo de nuevo.")