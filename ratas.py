#!/usr/bin/env python3
import RPi.GPIO as GPIO  # importa GPIO
import datetime 
import time
from hx711 import HX711 # importa la clase HX711
from hx712 import HX712 # importa la clase HX712
import csv 
import numpy as np
import matplotlib.pyplot as plt


#Comida 
#GRIS-NARANJO (VCC)
#ROJO MORADO (GND)
#VERDE-CAFE (DOUT)
#AMARILLO-AMARILLO (CSK)

#AGUA
#MORADO-NARANJO (VCC)
#GIS-BLANCO (GND)
#AZUL-CAFE (DOUT)
#VERDE-NEGRO (CSK)

filename = "medicion.csv"

c=0
try:
    GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
    # Create an object hx which represents your real hx711 chip
    # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
    hx = HX711(dout_pin=21, pd_sck_pin=20)
    hx2 = HX712(dout_pin=11, pd_sck_pin=10)
    # measure tare and save the value as offset for current channel
    # and gain selected. That means channel A and gain 128
    err = hx.zero()
    err2 = hx2.zero()
    
    # check if successful
    if err or err2:
        raise ValueError('Tara indefinida.')

    reading = hx.get_raw_data_mean()
    reading2 = hx2.get_raw_data_mean()
    if reading or reading2:  # always check if you get correct value or only False
        # now the value is close to 0
        print('Datos restados por compensación pero todabia no convertidos a unidades:',
              reading)
        print('Datos restados por compensación pero todabia no convertidos a unidades:',
              reading2)
    else:
        print('Dato invalido', reading)
        print('Dato invalido', reading2)

    # In order to calculate the conversion ratio to some units, in my case I want grams,
    # you must have known weight.
    input('Coloque un peso conocido en la balanza de "COMIDA" y luego presione enter')
    reading = hx.get_data_mean()
    if reading:
        print('Valor medio de HX711 restado para compenzar:', reading)
        known_weight_grams = input(
            'Escribe cuantos gramos son y presiona enter: ')
        try:
            value = float(known_weight_grams)
            print(value, 'gramos')
        except ValueError:
            print('Entero o flotante esperado:',
                  known_weight_grams)
                  
        # set scale ratio for particular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
        ratio = reading / value  # calculate the ratio for channel A and gain 128
        hx.set_scale_ratio(ratio)  # set ratio for current channel
        print('Relación de peso establecida (comida).')
    else:
        raise ValueError('No se puede calcular el valor medio. ERROR', reading)

#--------- segundo acondicionador----
    
    input('Coloque un peso conocido en la balanza de "AGUA" y luego presione enter')
    reading2 = hx2.get_data_mean()
    if reading2:
        print('Valor medio de HX712 restado para compenzar:', reading2)
        known_weight_grams2 = input(
            'Escribe cuantos gramos son y presiona enter: ')
        try:
            value2= float(known_weight_grams2)
            print(value2,'gramos')
        except ValueError:
            print('Entero o flotante esperado:',
                  known_weight_grams2)
                  
        # set scale ratio for particular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
        ratio2= reading2/ value2 # calculate the ratio for channel A and gain 128
        hx2.set_scale_ratio(ratio2) # set ratio for current channel
        print('Relación de peso establecida (Agua).')
    else:
        raise ValueError('No se puede calcular el valor medio. ERROR', reading2)
        

    # Read data several times and return mean value
    # subtracted by offset and converted by scale ratio to
    # desired units. In my case in grams.
    print("Ahora leere datos en un bucle infinito. Para salir presione 'CTRL + C'")
    input('Presione enter para comenzar a leer')
    print('El peso actual en las balanzas es: ')
    while True:
        c = c+1
        tiempo=time.strftime('%y-%m-%d %H:%M:%S')
        print('Comida',c,round(hx.get_weight_mean(20),2),'g',tiempo)
        print('Agua',c,round(hx2.get_weight_mean(10),2) ,'g',tiempo)
        with open(filename, 'a', newline='') as archivo_csv:
              csvwriter = csv.writer(archivo_csv)
              csvwriter.writerow(['[Comida]',c,round(hx.get_weight_mean(20),2),'g',tiempo])
              csvwriter.writerow(['[Agua]',c,round(hx2.get_weight_mean(10),2), 'g',tiempo])
              #time.sleep(26)
              fig, ax=plt.subplots()
              DIA=[tiempo]
              COMIDA=[round(hx.get_weight_mean(20),2)]
              AGUA=[round(hx2.get_weight_mean(10),2)]
              x=np.arange(len(DIA))
              width=0.35
              rect_Com=ax.bar(x-width/2,COMIDA,width,label='COMIDA')
              rect_Ag=ax.bar(x+width/2,AGUA,width,label='AGUA')
              ax.set_ylabel('GRAMOS')
              ax.set_title('Cantidad de alimento en las celdas')
              ax.set_xticks(x)
              ax.set_xticklabels(DIA)
              ax.legend()
              def autolabel(rects):
                  for rect in rects:
                      height = rect.get_height()
                      ax.annotate('{}'.format(height),
                                  xy=(rect.get_x() + rect.get_width() / 2,height),
                                  xytext=(0,3),
                                  textcoords="offset points",
                                  ha='center',va='bottom')
                  
              autolabel(rect_Com)
              autolabel(rect_Ag)
              fig.tight_layout()
              plt.show()
              time.sleep(15)
                    
except (KeyboardInterrupt, SystemExit):
    print('Bye')


finally:
    GPIO.cleanup()
