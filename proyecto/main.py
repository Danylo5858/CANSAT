import sx126x
import time
import requests
import serial
import string
from pa1010d import PA1010D
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException
import pynmea2
import matplotlib.pyplot as plt
import cilindro

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
from time import sleep
import math
import serial

# rastreador por web
pnChannel = "rastreador"

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-82ed3899-e2cf-4265-9179-a7f500fc38bb'
pnconfig.publish_key = 'pub-c-6743dcf8-e4a1-43a2-a6b1-299f8458027b'
pnconfig.ssl = False
pnconfig.uuid = '6bfa57b2-d21c-4abb-8401-12bf846ea229'
pubnub = PubNub(pnconfig)
pubnub.subscribe().channels(pnChannel).execute()

# Comunicaciones por radio
node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=868,addr=0,power=22,rssi=False,air_speed=2400,relay=False)

# Datos de thingspeak
url = 'https://api.thingspeak.com/update?api_key=1WLQX15WWF5KYCZD&field1=0'
api_Key = "1WLQX15WWF5KYCZD"
channelNumber = 2436861


#Valores de los tres ejes.
class IMU:
    Roll = 0
    Pitch = 0
    Yaw = 0
myimu = IMU()


def traking():
    dataout = pynmea2.NMEAStreamReader()
    if lat is not None and lng is not None:
            try:
                envelope = pubnub.publish().channel(pnChannel).message({
                    'lat': lat,
                    'lng': lng,
                }).sync()
            except PubNubException as e:
                handle_exception(e)

#Inicia OpenGL y establece la perspectiva y la posición de la cámara
def InitGL():
    pygame.init()
    display = (1280, 724)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('IMU visualizer   (Press Esc to exit)')

    glClearColor((1.0/255*46),(1.0/255*45),(1.0/255*64),1)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    gluPerspective(100, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)

#Dibuja texto en la ventana de visualización.
def DrawText(textString):
    font = pygame.font.SysFont ("Courier New",40, True)
    textSurface = font.render(textString, True, (255,255,0), (46,45,64,255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

#Dibuja un cilindro 3D.
def DrawCylinder():
    quadric = gluNewQuadric()
    glColor3f(0.0, 0.0, 1.0) # color azul
    gluQuadricDrawStyle(quadric, GLU_FILL)
    glTranslatef(-0.1, 0, -1.5)
    gluCylinder(quadric, 1.5, 1.5, 4.0, 150, 10) # cilindro exterior
    gluDeleteQuadric(quadric)

#Dibuja unos circulos 3D.
def DrawCircle_verde():
    glColor3f(0, 1, 0)
    glTranslatef(-0.5, 1.0, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0.5, -1)
    for i in range(361):
        angle = i * math.pi / 180
        glVertex2f(0.5 + (1.5 * math.cos(angle)), -1 + (1.5 * math.sin(angle)))
    glEnd()

def DrawCircle_rojo():
    glColor3f(1, 0, 0)
    glTranslatef(-0.5, 1.0, 4.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(1, -2)
    for i in range(361):
        angle = i * math.pi / 180
        glVertex2f(1 + (1.5 * math.cos(angle)), -2 + (1.5 * math.sin(angle)))
    glEnd()

#Dibuja los objeto 3D y la orientacion calculada por el IMU.
def DrawGL():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluPerspective(100, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)
    glRotatef(round(myimu.Pitch,1), 0, 0, 1)
    glRotatef(round(myimu.Roll,1), -1, 0, 0)
    DrawText("  Roll: {}°                          Pitch: {}°      ".format(round(myimu.Roll,1),round(myimu.Pitch,1)))
    glRotatef(-90, 1, 0, 0)
    DrawCylinder()
    DrawCircle_verde()
    DrawCircle_rojo()
    pygame.display.flip()

def ReadData():
    myimu.Roll = float(result[7])
    myimu.Pitch = float(result[8])
      
def main():
    #Lee la informacion y despues entra en bucle revisando si la pestana sigue activa mientras actualiza la imagen.
    global display
    pygame.init()
    display = (1280,724)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('IMU visualizer   (Press Esc to exit)')
    
    InitGL()

    myThread1 = threading.Thread(target = ReadData)
    myThread1.daemon = True
    myThread1.start()
    DrawGL()
            
"""
    #Borra la pantalla de OpenGL y muestra un mensaje durante 5 segundos si ocurre algun error.
    except:
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        DrawText("             Existe un error              ")
        pygame.display.flip()
        sleep(0.1)
"""

while True:
    result = node.receive()
    
    if (result is not None) and (len(result) == 9):
        print (result)
        
        day = result[0]
        hour = result[1]
        pres = result[2]
        temp = result[3]
        lat = result[4]
        lng = result[5]
        height = result[6]
        myimu.Roll = result[7]
        myimu.Pitch = result[8]

        main()
        
        parametros = {'api_Key':api_Key, 'field1':pres, 'field2':temp, 'field3':height}
        respuesta = requests.post(url, params=parametros)
        traking()
    else:
        continue

