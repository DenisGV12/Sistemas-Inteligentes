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

HEURISTICA='Grado'

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

#Clase variable, representa un hueco del crucigrama 
class Variable:
    def __init__(self, nombre, tipo, celdas, dominio):
        self.nombre=nombre
        self.tipo=tipo# 'h' o 'v'
        self.celdas=celdas
        self.fila=celdas[0][0]
        self.col=celdas[0][1]
        self.dominio=dominio
        self.restricciones=[]
        self.valor=None
        self.podado=[]

    def __str__(self):
        tipo='horizontal' if self.tipo=='h' else 'vertical'
        return f'Nombre {self.nombre} Posición {self.fila} {self.col} Tipo: {tipo} Dominio: {self.dominio}'

#Recorre el tablero por fila o columna, devolviendo los trozos libres
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

#Mira si las palabras de forma ordenada del diccionario caben en la variable y la guarda en su dominio, lo hace letra por letra de la palabra
def palabraCabe(tablero, almacen, celdas):
    dominio=[]
    for pal in sorted(almacen.get(len(celdas), [])):
        valida=True
        #Comprueba que si la celda no esta vacía y si la letra no sea dintinta de la que comprobamos, acabando el bucle si es así
        for i, (f, c) in enumerate(celdas):
            letra=tablero.getCelda(f, c)
            if letra!=VACIA and letra!=pal[i]:
                valida=False
                break
        if valida:
            dominio.append(pal)
    return dominio

#Recorre el tablero y crea sus variables, siempre mayores que 2, calculando los dominios y restricciones
def creaVariables(tablero, almacen):
    variables=[]
    filas=tablero.getAlto()
    cols=tablero.getAncho()

    #Filas
    for f in range(filas):
        fila=[]
        for c in range(cols):
            fila.append((f, c))
        for tramo in recorreTablero(tablero, fila):
            if len(tramo)>=2:
                variables.append(Variable(len(variables), 'h', tramo, palabraCabe(tablero, almacen, tramo)))
    #Columnas
    for c in range(cols):
        columna=[]
        for f in range(filas):
            columna.append((f, c))
        for tramo in recorreTablero(tablero, columna):
            if len(tramo)>=2:
                variables.append(Variable(len(variables), 'v', tramo, palabraCabe(tablero, almacen, tramo)))

    #restricciones
    for v1 in variables:
        for v2 in variables:
            #solo se comprueba una vertical con una horizontal, nunca del mismo tipo
            if v1.tipo!=v2.tipo:
                for celda in v1.celdas:
                    #Comprueba que la celda de la horizontal/vertical pertenezca a la otra
                    if celda in v2.celdas:
                        v1.restricciones.append((v2, v1.celdas.index(celda), v2.celdas.index(celda)))

    if HEURISTICA=='Ninguna':
        return variables
    if HEURISTICA=='MRV':
        return ordenaMRV(variables)

    #Grado (la que se usa por defecto): primero las variables con más cruces
    ordenadas=[]
    for n in range(len(variables), -1, -1):
        for v in variables:
            if len(v.restricciones)==n:
                ordenadas.append(v)
    for i in range(len(ordenadas)):
        ordenadas[i].nombre=i

    return ordenadas

#Imprime las variables en el propio tablero
def imprimeVariables(variables):
    for v in variables:
        print(v)    
    
#Comprueba si el valor se puede poner en Vk con lo que ya hay asignado
def test(Vk, valor, variables_pasadas):
    #No se pueden repetir palabras
    for v in variables_pasadas:
        if valor == v.valor:
            return False

    #Las restricciones tienen que coincidir
    for otra, posVk, posOtra in Vk.restricciones:
        if otra in variables_pasadas and valor[posVk] != otra.valor[posOtra]:
            return False

    return True

#backtracking: prueba valores y si falla vuelve atras
def backtracking(Variables, index):
    #si ya hemos asignado todas, hay solucion
    if index == len(Variables):
        return True

    for valor in Variables[index].dominio:
        if test(Variables[index], valor, Variables[:index]):
            Variables[index].valor = valor

            #pasamos a la siguiente variable
            if backtracking(Variables, index+1):
                return True

            #no ha funcionado, quitamos el valor
            Variables[index].valor = None

    return False

#escribe en el tablero las palabras de la solucion
def escribeSolucion(tablero, variables):
    for v in variables:
        for i, (f, c) in enumerate(v.celdas):
            tablero.setCelda(f, c, v.valor[i])

#mira si a (de Vi) y b (de Vj) pueden ir juntas
def es_consistente(Vi, a, Vj, b):
    #misma palabra no vale
    if a == b:
        return False
    #si se cruzan la letra tiene que ser la misma
    for otra, posVi, posOtra in Vi.restricciones:
        if otra is Vj and a[posVi] != b[posOtra]:
            return False
    return True

#Poda los dominios de las variables futuras segun el valor a
def Forward(i, a, variable):
    dominio_vacio = False
    for j in range(i+1, len(variable)):
        for b in list(variable[j].dominio):
            if not es_consistente(variable[i], a, variable[j], b):
                #lo quitamos y guardamos quien lo ha podado
                variable[j].dominio.remove(b)
                variable[j].podado.append((b, i))
            if variable[j].dominio == []:
                dominio_vacio = True
                break
        #si algun dominio se queda vacio este valor no sirve
        if dominio_vacio:
            return False
    return True

#Devuelve a los dominios lo que podo la variable i
def Restaurar(i, variable):
    for j in range(i+1, len(variable)):
        for b in list(variable[j].podado):
            if b[1] == i:
                variable[j].podado.remove(b)
                variable[j].dominio.append(b[0])

#forward checking
def FC(i,variable):
    if not variable:
        return True
    for a in variable[i].dominio:
        variable[i].valor=a
        #si es la ultima variable ya esta
        if i == len(variable)-1:
            return True
        else:
            if Forward(i,a,variable):
                if FC(i+1,variable):
                    return True
            #si no ha ido bien deshacemos la poda
            Restaurar(i,variable)
    variable[i].valor=None
    return False

#lee crucigrama.txt y devuelve un diccionario {"FILASxCOLS": [filas del tablero]}
def leeCrucigramas():
    guardados={}
    try:
        f=open('crucigrama.txt', 'r')
        lineas=f.read().split()
        f.close()
    except FileNotFoundError:
        return guardados
    clave=None
    for linea in lineas:
        if 'x' in linea: #cabecera con el tamaño, p.ej. 8x8
            clave=linea
            guardados[clave]=[]
        elif clave is not None:
            guardados[clave].append(linea)
    return guardados

#guarda el tablero en crucigrama.txt (uno por tamaño, si ya existe se sobrescribe)
def guardaCrucigrama(tablero):
    guardados=leeCrucigramas()
    clave=str(tablero.getAlto())+'x'+str(tablero.getAncho())
    guardados[clave]=str(tablero).split()
    f=open('crucigrama.txt', 'w')
    for k in guardados:
        f.write(k+'\n'+'\n'.join(guardados[k])+'\n\n')
    f.close()
    print('Crucigrama guardado')

#carga desde crucigrama.txt el tablero de su mismo tamaño
def cargaCrucigrama(tablero):
    clave=str(tablero.getAlto())+'x'+str(tablero.getAncho())
    guardados=leeCrucigramas()
    if clave not in guardados:
        MessageBox.showwarning("Alerta", "No hay crucigrama guardado de este tamaño")
        return
    lineas=guardados[clave]
    #copiamos celda a celda al tablero
    for fil in range(tablero.getAlto()):
        for col in range(tablero.getAncho()):
            tablero.setCelda(fil, col, lineas[fil][col])
    print('Crucigrama cargado')

def AC3(Q,variables):
    for v in variables:
        if not v.dominio:
            return False
    while Q:
        Vk,Vm = Q.pop(0)
        cambio = False
        for d in list(Vk.dominio):
            aux = False
            for vm in Vm.dominio:
                if es_consistente(Vk, d, Vm, vm):
                    aux = True
                    break
            if not aux:
                Vk.dominio.remove(d)
                cambio = True
        if not Vk.dominio:
            return False
        if cambio == True:
            for r in Vk.restricciones:
                Vi = r[0]
                if Vi is not Vm and (Vi, Vk) not in Q:
                    Q.append((Vi,Vk))
    return True

def creaCola(variables):
    Q = []
    for v in variables:
        for r in v.restricciones:
            Q.append((v, r[0]))
    return Q

def aplicaDominiosAC3(variables, dominiosAC3, fotoAC3, tablero):
    if dominiosAC3 is not None and fotoAC3 == str(tablero) and len(dominiosAC3) == len(variables):
        for v, d in zip(variables, dominiosAC3):
            v.dominio = list(d)

def variablesConflicto(Variables, index):
    Vk = Variables[index]
    conflictos = set()

    for i in range(index): #Mira si alguan palabra anterior ya tiene asignada la palabra del domino que se esta mirando ahora
        if Variables[i].valor == Vk.valor:
            conflictos.add(i)

    for otra, posVk, posOtra in Vk.restricciones: #Compruba que la letra de la palbra guardada en una variable anterior coincide con la qu se esta probando ahora
        if otra.nombre < index and Vk.valor[posVk] != otra.valor[posOtra]:
            conflictos.add(otra.nombre)
    return conflictos

def backjumping(Variables, index):
    if index == len(Variables):
        return True, set()

    Vk = Variables[index]
    conflictos_k = set()

    for v in Vk.dominio: #Prueba una a una todas las palabras del domino de la variable actual
        Vk.valor = v
        conflictosVk = variablesConflicto(Variables, index)

        if not conflictosVk: #Caso de los conflictos este vacío
            exito, conflictos = backjumping(Variables, index + 1) #Pasa a la siguiente variable porque se ha asignado un valor

            if exito:
                return True, set() #Todas las varaibles se le ha asignado un valor
            if index not in conflictos: #Si la variable no esta en los conflicto, vuelve atrás
                Vk.valor = None
                return False, conflictos
            else:
                conflictos_k = conflictos_k.union(conflictos - {index}) #Se quita el indice actual, para volver a probar otra palabra del domino de la variable actual
        else:
            conflictos_k = conflictos_k.union(conflictosVk)

        Vk.valor = None # Se desasigna el valor que se probaba

    return False, conflictos_k.union({index}) # Fallo a la hroa de asignar y devuelve los conflictos actuales mas el indice que se prueba
    
def ejecuta(algoritmo, tablero, almacen):
    variables=creaVariables(tablero, almacen)
    inicio=time.time()
    res=True
    if 'AC3' in algoritmo:
        res=AC3(creaCola(variables),variables)
    if res and algoritmo!='AC3':
        if 'BK' in algoritmo:
            res=backtracking(variables,0)
        elif 'FC' in algoritmo:
            res=FC(0,variables)
        elif 'BJ' in algoritmo:
            res,_=backjumping(variables,0)
    fin=time.time()
    return res, fin-inicio

def comparaAlgoritmos(tablero, almacen):
    print('TIEMPOS DEL TABLERO ACTUAL')
    print('Algoritmo   Tiempo (s)   Resultado')
    for algoritmo in ['AC3', 'FC', 'AC3+FC', 'AC3+BJ', 'AC3+BK', 'BJ', 'BK']:
        res, tiempo = ejecuta(algoritmo, tablero, almacen)
        print(f'{algoritmo:9}   {tiempo:10.4f}   {res}', flush=True)

#Heurística MRV (no se usa en la entrega): primero las variables con el dominio más pequeño
def ordenaMRV(variables):
    maximo=0
    for v in variables:
        if len(v.dominio)>maximo:
            maximo=len(v.dominio)
    ordenadas=[]
    for n in range(maximo+1):
        for v in variables:
            if len(v.dominio)==n:
                ordenadas.append(v)
    for i in range(len(ordenadas)):
        ordenadas[i].nombre=i
    return ordenadas

#########################################################################  
# Principal
#########################################################################
def main():
    root= tkinter.Tk() #para eliminar la ventana de Tkinter
    root.withdraw() #se cierra
    pygame.init()

    global HEURISTICA
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
    altoVentana= filas*(TAM+MARGEN)+2*MARGEN + 50
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygame.display.set_caption("Practica 1: Crucigrama")    
     
    #La altura del botón depende del tamaño de la ventana pero hay una altura máxima
    altoBoton=altoVentana//6
    if altoBoton>=65:
        altoBoton=85
        
    hueco=(altoVentana-5*altoBoton)//6
    xBoton=anchoVentana-95
    botBK=pygame.Rect(xBoton, hueco, 70, altoBoton)
    botFC=pygame.Rect(xBoton, 2*hueco+altoBoton, 70, altoBoton)
    botAC3=pygame.Rect(xBoton, 3*hueco+2*altoBoton, 70, altoBoton)
    botBJ=pygame.Rect(xBoton, 4*hueco+3*altoBoton, 70, altoBoton)
    botVR=pygame.Rect(xBoton, 5*hueco+4*altoBoton, 70, altoBoton)
    #botones de guardar y cargar abajo a la izquierda
    botGuardar=pygame.Rect(MARGEN+5, altoVentana-45, 92, 40)
    botCargar=pygame.Rect(MARGEN+100, altoVentana-45, 92, 40)
    botTiempos=pygame.Rect(MARGEN+200, altoVentana-45, 92, 40)
    botHeur=pygame.Rect(MARGEN+290, altoVentana-45, 92, 40)

    tamFuenteBot=int(altoBoton//1.5)  
    fuenteBotPeq=pygame.font.Font(None, 28)  
    fuenteBot=pygame.font.Font(None, tamFuenteBot)
    fuenteCelda= pygame.font.Font(None, 70)
    
    almacen=creaAlmacen(file)
    #imprimeAlmacen(almacen)
    game_over=False
    tablero=Tablero(filas, cols)    
    dominiosAC3 = None
    fotoAC3 = None
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
                    aplicaDominiosAC3(variables, dominiosAC3, fotoAC3, tablero)
                    imprimeVariables(variables)
                    inicio=time.time() #apuntamos cuando empieza
                    res=backtracking(variables,0) #empezamos por la primera variable
                    fin=time.time() #y cuando acaba
                    print(f'Tiempo BK: {fin-inicio:.4f} segundos') #mostramos lo que ha tardado
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")
                    else:
                        escribeSolucion(tablero,variables) #pintamos la solucion

                elif pulsaBoton(pos, botFC):
                    print('FC')
                    variables=creaVariables(tablero, almacen)
                    aplicaDominiosAC3(variables, dominiosAC3, fotoAC3, tablero)
                    imprimeVariables(variables)
                    inicio=time.time() #apuntamos cuando empieza
                    res=FC(0,variables) #esta variable debe estar a falso si el problema no tiene solución
                    fin=time.time() #y cuando acaba
                    print(f'Tiempo FC: {fin-inicio:.4f} segundos') #mostramos lo que ha tardado
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")
                    else:
                        escribeSolucion(tablero,variables)

                elif pulsaBoton(pos, botAC3):
                    print('AC3')
                    variables=creaVariables(tablero, almacen)
                    print('DOMINIOS ANTES DEL AC3')
                    imprimeVariables(variables)
                    Q = creaCola(variables)
                    inicio=time.time()
                    res = AC3(Q,variables)
                    fin=time.time()
                    print(f'Tiempo AC3: {fin-inicio:.4f} segundos')
                    print('DOMINIOS DESPUES DEL AC3')
                    imprimeVariables(variables)
                    if res==False:
                        dominiosAC3=None
                        fotoAC3=None
                        MessageBox.showwarning("Alerta", "No hay solución")
                    else:
                        dominiosAC3 = []
                        for v in variables:
                            copia = list(v.dominio)
                            dominiosAC3.append(copia)
                        fotoAC3=str(tablero)

                elif pulsaBoton(pos, botBJ):
                    print('BJ')
                    variables=creaVariables(tablero, almacen)
                    aplicaDominiosAC3(variables, dominiosAC3, fotoAC3, tablero)
                    imprimeVariables(variables)
                    inicio=time.time() #apuntamos cuando empieza
                    res,_=backjumping(variables,0) #esta variable debe estar a falso si el problema no tiene solución
                    fin=time.time() #y cuando acaba
                    print(f'Tiempo BJ: {fin-inicio:.4f} segundos') #mostramos lo que ha tardado
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")
                    else:
                        escribeSolucion(tablero,variables)

                elif pulsaBoton(pos, botVR):
                    print('VAR')
                    variables=creaVariables(tablero, almacen)
                    imprimeVariables(variables)
                elif pulsaBoton(pos, botTiempos):
                    print('TIEMPOS')
                    comparaAlgoritmos(tablero, almacen)
                elif pulsaBoton(pos, botHeur):
                    if HEURISTICA=='Grado':
                        HEURISTICA='MRV'
                    elif HEURISTICA=='MRV':
                        HEURISTICA='Ninguna'
                    else:
                        HEURISTICA='Grado'
                    dominiosAC3=None
                    fotoAC3=None
                    print('HEURISTICA:', HEURISTICA)
                elif pulsaBoton(pos, botGuardar):
                    guardaCrucigrama(tablero) #guardamos el tablero actual
                elif pulsaBoton(pos, botCargar):
                    cargaCrucigrama(tablero) #cargamos el que habia guardado
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
        pintarBoton(screen, fuenteBot, botBJ, "BJ")
        pintarBoton(screen, fuenteBot, botVR, "Variables")
        pintarBoton(screen, fuenteBotPeq, botTiempos, "Tiempos")
        pintarBoton(screen, fuenteBotPeq, botGuardar, "Guardar")
        pintarBoton(screen, fuenteBotPeq, botCargar, "Cargar")
        pintarBoton(screen, fuenteBotPeq, botHeur, HEURISTICA)

        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()
 
