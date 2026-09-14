import pygame
from pygame.locals import *
import tkinter
from tkinter import *
from tkinter.simpledialog import *
from tkinter import messagebox as MessageBox
import sys
import time
import copy
from tablero import *

GREY=(190, 190, 190)
NEGRO=(100,100, 100)
BLANCO=(255, 255, 255)
GRIS_ACTIVO=(245,245,245)
GRIS_NORMAL=(169,169,169)

MARGEN=5 #ancho del borde entre celdas
MARGEN_DERECHO=125 #ancho del margen derecho entre la cuadrícula y la ventana
TAM=60  #tamaño de la celda

LLENA='*' 
VACIA='-'

#########################################################################
# Detecta si se pulsa un botón
#########################################################################   
def pulsaBoton(pos, boton):
    if boton.collidepoint(pos[0], pos[1]):    
        return True
    else:
        return False
    
#########################################################################
# Pintar un boton
#########################################################################   
def pintarBoton(screen, fuenteBot, boton, mensaje):
    if boton.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, GRIS_ACTIVO, boton, 0)        
    else:
        pygame.draw.rect(screen, GRIS_NORMAL, boton, 0)
        
    texto=fuenteBot.render(mensaje, True, NEGRO)
    screen.blit(texto, (boton.x+(boton.width-texto.get_width())/2, boton.y+(boton.height-texto.get_height())/2))         

#########################################################################
# Pintar el crucigrama
#########################################################################         
def pintarTablero(screen, fuenteCelda,tablero, filas, cols):
    pygame.draw.rect(screen, GREY, [0, 0, filas*(TAM+MARGEN)+MARGEN, cols*(TAM+MARGEN)+MARGEN],0)
    for fil in range(tablero.getAlto()):
        for col in range(tablero.getAncho()):
            if tablero.getCelda(fil, col)==VACIA: 
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
            elif tablero.getCelda(fil, col)==LLENA: 
                pygame.draw.rect(screen, NEGRO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
            else: #dibujar letra                    
                pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)                
                texto= fuenteCelda.render(tablero.getCelda(fil, col), True, NEGRO)            
                screen.blit(texto, [(TAM+MARGEN)*col+MARGEN+15, (TAM+MARGEN)*fil+MARGEN+5])    
         
    
######################################################################### 
# Detecta si el ratón se pulsa en la cuadrícula
######################################################################### 
def inTablero(pos, filas, cols):
    if pos[0]>=MARGEN and pos[0]<=(TAM+MARGEN)*cols+MARGEN and pos[1]>=MARGEN and pos[1]<=(TAM+MARGEN)*filas+MARGEN:        
        return True
    else:
        return False
   
  
######################################################################### 
# Crea el almacen de palabras
######################################################################### 
def creaAlmacen(file):   
    f= open(file, 'r', encoding="utf-8")
    lista=f.read()
    f.close()
    listaPal=lista.split()
    almacen={}
    for pal in listaPal:        
        if len(pal) not in almacen:
            almacen[len(pal)]=set()
            almacen[len(pal)].add(pal.upper())
        else:
            almacen[len(pal)].add(pal.upper())   
    
    return almacen

######################################################################### 
# Imprime el contenido del almacen
######################################################################### 
def imprimeAlmacen(almacen):
    for tam, palabras in almacen.items():
        print (f'tam: {tam}: {palabras}')

#########################################################################
# Clase Variable: un hueco (horizontal o vertical) del crucigrama
#########################################################################
class Variable:
    def __init__(self, nombre, tipo, celdas, dominio):
        self.nombre=nombre
        self.tipo=tipo# 'h' o 'v'
        self.celdas=celdas
        self.fila=celdas[0][0]
        self.col=celdas[0][1]
        self.longitud=len(celdas)
        self.dominio=dominio
        self.restricciones=[]

    def __str__(self):
        tipo='horizontal' if self.tipo=='h' else 'vertical'
        return f'Nombre {self.nombre} Posición {self.fila} {self.col} Tipo: {tipo} Dominio: {self.dominio}'

def recorreTablero(tablero, celdas):
    trozosHueco=[]
    aux=[]
    for (f, c) in celdas:
        if tablero.getCelda(f, c)==LLENA:
            if aux!=[]:
                trozosHueco.append(aux)
            aux=[]
        else:
           aux.append((f, c))
    if aux!=[]:
        trozosHueco.append(aux)
    return trozosHueco

def creaVariables(tablero, almacen):
    variables=[]
    filas=tablero.getAlto()
    cols=tablero.getAncho()

    # horizontales: cada tramo de cada fila
    for f in range(filas):
        fila=[(f, c) for c in range(cols)]
        for tramo in recorreTablero(tablero, fila):
            variables.append(Variable(len(variables), 'h', tramo, palabraCabe(tablero, almacen, tramo)))

    # verticales: cada tramo de cada columna, solo si tiene 2 o más celdas
    for c in range(cols):
        columna=[(f, c) for f in range(filas)]
        for tramo in recorreTablero(tablero, columna):
            if len(tramo)>=2:
                variables.append(Variable(len(variables), 'v', tramo, palabraCabe(tablero, almacen, tramo)))

    # restricciones: si una horizontal y una vertical comparten una celda, se cruzan ahí
    for v1 in variables:
        for v2 in variables:
            if v1.tipo!=v2.tipo:
                for celda in v1.celdas:
                    if celda in v2.celdas:
                        v1.restricciones.append((v2, v1.celdas.index(celda), v2.celdas.index(celda)))

    return variables

def palabraCabe(tablero, almacen, celdas):
    dominio=[]
    for pal in sorted(almacen.get(len(celdas), [])):
        valida=True
        for i, (f, c) in enumerate(celdas):
            letra=tablero.getCelda(f, c)
            if letra!=VACIA and letra!=pal[i]:
                valida=False
                break
        if valida:
            dominio.append(pal)
    return dominio

def imprimeVariables(variables):
    for v in variables:
        print(v)

#########################################################################  
# Principal
#########################################################################
def main():
    root= tkinter.Tk() #para eliminar la ventana de Tkinter
    root.withdraw() #se cierra
    pygame.init()
    
    reloj=pygame.time.Clock()
    
    print("Uso: python main.py --filas M --columnas N --dic archivo.txt")
    if '--filas' in sys.argv:
        filas = int(sys.argv[sys.argv.index("--filas") + 1])
    else:
        filas=5
    if '--columnas' in sys.argv:
        cols = int(sys.argv[sys.argv.index("--columnas") + 1])
    else:
        cols=6
    if '--dic' in sys.argv:
        file = sys.argv[sys.argv.index("--dic") + 1]
    else:
        file='d0.txt'    
        
    anchoVentana=cols*(TAM+MARGEN)+MARGEN_DERECHO
    altoVentana= filas*(TAM+MARGEN)+2*MARGEN 
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygame.display.set_caption("Practica 1: Crucigrama")    
     
    #La altura del botón depende del tamaño de la ventana pero hay una altura máxima
    altoBoton=altoVentana//5    
    if altoBoton>=65:
        altoBoton=65    
    
    posBotBK=altoVentana//1-altoBoton//2
    posBotFC=altoVentana//2-altoBoton//2
    posBotAC3=(altoVentana//2+altoVentana)//2-altoBoton//2     
    postBotVR= altoVentana//4-altoBoton//2
    botBK=pygame.Rect(anchoVentana-95, posBotBK, 70, altoBoton)    
    botFC=pygame.Rect(anchoVentana-95,posBotFC , 70, altoBoton)
    botAC3=pygame.Rect(anchoVentana-95, posBotAC3, 70, altoBoton)
    botVR=pygame.Rect(anchoVentana-95, postBotVR, 70, altoBoton)
    

    tamFuenteBot=int(altoBoton//1.5)    
    fuenteBot=pygame.font.Font(None, tamFuenteBot)
    fuenteCelda= pygame.font.Font(None, 70)
    
    almacen=creaAlmacen(file)
    #imprimeAlmacen(almacen)
    game_over=False
    tablero=Tablero(filas, cols)    
    ac3=False
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición y calcular coordenadas matriciales                               
                pos=pygame.mouse.get_pos()                
                if pulsaBoton(pos, botBK):
                    print('BK')
                    variables=creaVariables(tablero, almacen)
                    imprimeVariables(variables)
                    res=True #esta variable debe estar a falso si el problema no tiene solución
                    if res==False:
                            MessageBox.showwarning("Alerta", "No hay solución")                     
                elif pulsaBoton(pos, botFC):
                    print('FC')
                    variables=creaVariables(tablero, almacen)
                    imprimeVariables(variables)
                    res=True #esta variable debe estar a falso si el problema no tiene solución               
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")  
                elif pulsaBoton(pos, botAC3):
                    print('AC3')
                    variables=creaVariables(tablero, almacen)
                    imprimeVariables(variables)
                elif pulsaBoton(pos, botVR):
                    print('VAR')
                    variables=creaVariables(tablero, almacen)
                    imprimeVariables(variables)         
                elif inTablero(pos, filas, cols):
                    colDestino=pos[0]//(TAM+MARGEN)
                    filDestino=pos[1]//(TAM+MARGEN)                    
                    if event.button==1: #botón izquierdo
                        if tablero.getCelda(filDestino, colDestino)==VACIA:
                            tablero.setCelda(filDestino, colDestino, LLENA)
                        else:
                            tablero.setCelda(filDestino, colDestino, VACIA)
                    elif event.button==3: #botón derecho
                        c=askstring('Entrada', 'Introduce carácter')
                        if not c is None:
                            tablero.setCelda(filDestino, colDestino, c.upper())             
        #limpiar pantalla
        screen.fill(GREY)
        #pintar crucigrama 
        pintarTablero(screen, fuenteCelda, tablero, filas, cols)                   
        #pintar botones           
        pintarBoton(screen, fuenteBot, botBK, "BK")
        pintarBoton(screen, fuenteBot, botFC, "FC")
        pintarBoton(screen, fuenteBot, botAC3, "AC3")
        pintarBoton(screen, fuenteBot, botVR, "Variables")  
        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()
 
