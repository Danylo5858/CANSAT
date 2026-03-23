import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import threading
from time import sleep
import math
import serial
#import board
#import adafruit_mpu6050
"""
#Coneccion con el giroscopio
i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)
Gyro = mpu.gyro
"""
#Valores de los tres ejes.
class IMU:
    Roll = 0
    Pitch = 0
    Yaw = 0
myimu = IMU()

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
    DrawText("  Roll: {}°                           Pitch: {}°      ".format(round(myimu.Roll,1),round(myimu.Pitch,1)))
    glRotatef(-90, 1, 0, 0)
    DrawCylinder()
    DrawCircle_verde()
    DrawCircle_rojo()
    pygame.display.flip()

#Lee los datos del sensor de movimiento y actualiza la orientacion calculada por el IMU.
def ReadData():
    while True:
        """
        xacc, yacc, zacc = mpu.acceleration
        xgyro, ygyro, zgyro = mpu.gyro
        xacc =round(xacc,2)
        yacc =round(yacc,2)
        zacc =round(zacc,2)
        xgyro =round(xgyro,2)
        ygyro =round(ygyro,2)
        zgyro =round(zgyro,2)

        myimu.Roll = math.atan(xacc/math.sqrt(pow(yacc,2) + pow(zacc,2)))*(180.0/3.14)
        myimu.Pitch = math.atan(yacc/math.sqrt(pow(xacc,2) + pow(zacc,2)))*(180.0/3.14)
        sleep(0.2)
        """
        myimu.Roll = Data(roll)
        myimu.Pitch = Data(pitch)

def main():
    #Lee la informacion y despues entra en bucle revisando si la pestana sigue activa mientras actualiza la imagen.
    global display
    pygame.init()
    display = (1280,724)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('IMU visualizer   (Press Esc to exit)')
    try:
        InitGL()

        myThread1 = threading.Thread(target = ReadData)
        myThread1.daemon = True
        myThread1.start()
        """
        while True:
            event = pygame.event.poll()
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                break
            """
        DrawGL()
        #pygame.time.wait(10)
            
    #Borra la pantalla de OpenGL y muestra un mensaje durante 5 segundos si ocurre algun error.
    except:
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        DrawText("             Existe un error              ")
        pygame.display.flip()
        sleep(5)

if __name__ == '__main__': main()
