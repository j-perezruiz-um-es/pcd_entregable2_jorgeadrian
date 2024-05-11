import pytest
from unittest.mock import Mock
from datetime import datetime
import threading
import time
import random

from pcd_entregable2_jorge_adrian import *

# ----------------------------
# EXPLICACIONES DEL PROGRAMA
# ----------------------------
'''
Para algunos pytest se ha usado la clase Mock para comprobar si
se han llegado a ejecutar los metodos abstractos que se encuentran 
en las funciones gracias a la funcion de Mock, assert_called_once_with 
(assert_not_called compruba lo contrario) asi veremos si se llega a 
ejecutar como esperamos el codigo en un orden correcto.

Por ejemplo, veremos en el sistema, en el contexto y en el umbral si se llama 
a la funcion manejar_date_temp ya que son los que tienen sucesores en el programa
'''
# -----------------------
# TEST STRATEGIES
# ----------------------- 
def test_execute_strategy_meansd():
    # Datos de prueba
    date = '2024-05-01 13:00:00' 
    temp = [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33]  

    # Instancia de StrategyMeanSd
    strategy = StrategyMeanSd()

    # Llamada a la función execute
    mean, sd = strategy.execute(date, temp)

    # Verificar que los valores devueltos sean los esperados
    assert round(mean, 2) == 23.17
    assert round(sd, 2) == 6.72

def test_execute_strategy_cuantil():
    # Datos de prueba
    date = '2024-05-01 13:00:00' 
    temp = [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33]  

    # Instancia de StrategyMeanSd
    strategy = StrategyCuantil()

    # Llamada a la función execute
    Q1, mediana, Q3 = strategy.execute(date, temp)

    # Verificar que los valores devueltos sean los esperados
    assert Q1 == 18.5
    assert mediana == 23.5
    assert Q3 == 29

def test_execute_strategy_maxmin():
    # Datos de prueba
    date = '2024-05-01 13:00:00' 
    temp = [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33]  

    # Instancia de StrategyMeanSd
    strategy = StrategyMaxMin()

    # Llamada a la función execute
    maximo, minimo = strategy.execute(date, temp)

    # Verificar que los valores devueltos sean los esperados
    assert maximo == 33
    assert minimo == 10

# -----------------------
# TEST CONTEXTO
# -----------------------
def test_contexto_estadisticos_init():
    # Instancia del contexto
    contexto = ContextoEstadisticos()
    
    # Verificar que no existe ningunna estrategia establecida en el contexo
    assert contexto.strategy is None

def test_contexto_estadisticos_set_strategy():
    # Instancia del contexto
    contexto = ContextoEstadisticos()
    
    # Instancia de la estrategia (si se establece la clase Strategy, falla la prueba ya que es un abstract method) por ejemplo StrategyMaxMin
    strategy = StrategyMaxMin()
    
    # Establecemos la estrategia
    contexto.set_strategy(strategy)
    
    # Verificar si se ha seleccionado la estrategia
    assert contexto.strategy == strategy

def test_contexto_estadisticos_manejar_date_temp_con_strategy():
    # Strategy y sucesor con Mock
    strategy_mock = Mock()
    sucesor_mock = Mock()
    
    # Contexto con la estrategia definida y un sucesor
    contexto = ContextoEstadisticos(sucesor_mock)
    contexto.set_strategy(strategy_mock)
    
    # Llamada al método manejar_date_temp
    contexto.manejar_date_temp('2024-05-01 13:00:00', [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33])
    
    # Verificar si se llamo a execute de la estrategia y luego manejar_date_temp
    contexto.strategy.execute.assert_called_once_with('2024-05-01 13:00:00', [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33])
    contexto.sucesor.manejar_date_temp.assert_called_once_with('2024-05-01 13:00:00', [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33])

def test_contexto_estadisticos_manejar_date_temp_sin_strategy():
    # Strategy y sucesor con Mock
    sucesor_mock = Mock()
    strategy_mock = Mock()
    
    # Contexto sin establecer la estrategia
    contexto = ContextoEstadisticos(sucesor_mock)
    
    # Llamada al método manejar_date_temp
    contexto.manejar_date_temp('2024-05-01 13:00:00', [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33])
    
    # Verificar si se llamo al metodo manejar_date_temp del sucesor y no se ejecuto la estrategia que se definio pero no se registro en el contexto
    strategy_mock.execute.assert_not_called()
    contexto.sucesor.manejar_date_temp.assert_called_once_with('2024-05-01 13:00:00', [25, 28, 30, 20, 27, 18, 15, 19, 10, 22, 31, 33])

# ------------------------------
# TEST UMBRAL
# ------------------------------
def test_supera_umbral_manejar_date_temp():
    # Sucesor y umbral
    sucesor_mock = Mock()
    umbral = Umbral(sucesor_mock)
    
    # Llamada a la función manejar_date_temp con temperatura por encima del umbral
    result = umbral.manejar_date_temp('2024-05-01 12:00:00', [30])

    # Verificar que devuelve True cuando la temperatura supera el umbral y que se llama al método manejar_date_temp del sucesor
    assert result == True
    umbral.sucesor.manejar_date_temp.assert_called_once_with('2024-05-01 12:00:00', [30])

def test_no_supera_umbral_manejar_date_temp():
    # Sucesor y umbral
    sucesor_mock = Mock()
    umbral = Umbral(sucesor_mock)

    # Llamada a la función manejar_date_temp con temperatura por debajo del umbral
    result = umbral.manejar_date_temp('2024-05-01 12:00:00', [25])

    # Verificar que devuelve False cuando la temperatura no supera el umbral
    assert result == False
    umbral.sucesor.manejar_date_temp.assert_called_once_with('2024-05-01 12:00:00', [25])

# ------------------------------
# TEST AUMENTO
# ------------------------------
def test_existe_aumento_manejar_date_temp():
    # Aumento
    aumento = Aumento()

    # Llamada a la función manejar_date_temp con temperatura por encima del aumento
    result = aumento.manejar_date_temp('2024-05-01 12:00:30', [15, 28, 30, 20, 27, 26])

    # Verificar que devuelve True cuando la temperatura supera el aumento
    assert result == True

def test_no_existe_aumento_manejar_date_temp():
    # Aumento
    aumento = Aumento()

    # Llamada a la función manejar_date_temp con temperatura por debajo del aumento
    result = aumento.manejar_date_temp('2024-05-01 12:00:30', [15, 28, 30, 20, 27, 23])

    # Verificar que devuelve False cuando la temperatura no supera el aumento
    assert result == False

# ------------------------------
# TEST SISTEMA
# ------------------------------
def test_sistema_iot_obtener_instancia_sin_manager_chain():
    # Verificamos que se lance un error si no se proporciona un manager_chain
    with pytest.raises(ErrorNone):
        SistemaIoT.obtener_instancia()

def test_sistema_iot_singleton():
    # Creamos una instancia del SistemaIoT con su manager_chain usando Mock
    manager_chain_mock = Mock()
    sistema = SistemaIoT.obtener_instancia(manager_chain_mock)
    
    # Comprobramos que existe la instancia creada
    assert sistema is not None

    # Verificamos que salta el ErrorInstancia si creamos otra instancia
    with pytest.raises(ErrorInstancia):
        otra_instancia = SistemaIoT(manager_chain_mock)

def test_sistemaiot_update():
    # Creamos una instancia del SistemaIoT y el el manager_chain con Mock
    manager_chain_mock = Mock()
    sistema = SistemaIoT.obtener_instancia(manager_chain_mock)
    
    # Valores del sistema para ver si se actualizan correctamente
    sistema.date_temp = [('2024-05-01 12:00:00', 25), ('2024-05-01 12:00:05', 30), ('2024-05-01 12:00:10', 15), ('2024-05-01 12:00:15', 10)]
    sistema.date = '2024-05-01 12:00:15'
    sistema.temp = [25, 30, 15, 10]
    
    # Actualizar el sistema con una nueva tupla de fecha y temperatura
    sistema.update(('2024-05-01 12:00:20', 33))

    # Verificar que las listas se han actualizado correctamente y si se llama al método manejar_date_temp del manager_chain
    assert sistema.get_date_temp() == [('2024-05-01 12:00:00', 25), ('2024-05-01 12:00:05', 30), ('2024-05-01 12:00:10', 15), ('2024-05-01 12:00:15', 10), ('2024-05-01 12:00:20', 33)]
    assert sistema.get_date() == '2024-05-01 12:00:20'
    assert sistema.get_temp() == [25, 30, 15, 10, 33]
    sistema.manager_chain.manejar_date_temp.assert_called_once_with(sistema.get_date(), sistema.get_temp())
    
# ------------------------------
# TEST OBSERVABLE
# ------------------------------
def test_register_observer():
    # Observable y observador
    observable = Observable()
    observer = object()
    
    # Registrar el observador
    observable.register_observer(observer)
    
    # Verificar que el observador esta en observable
    assert observer in observable._observers

def test_remove_observer():
    # Observable y observador
    observable = Observable()
    observer = object()
    
    # Registrar el observador y eliminarlo
    observable.register_observer(observer)
    observable.remove_observer(observer)
    
    # Verificar que el observador no esta en observable
    assert observer not in observable._observers

def test_notify_observers():
    # Observable y mock de un observador
    observable = Observable()
    observer_mock = Mock()
    observable.register_observer(observer_mock)

    # Llamada al método notify_observers() con date_temp
    date_temp = ("2024-05-09 12:00:00", 25)
    observable.notify_observers(date_temp)

    # Verificar si se ha llamado al método update del observador con date_temp
    observer_mock.update.assert_called_once_with(date_temp)
