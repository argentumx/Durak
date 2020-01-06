import pygame
import os
from random import shuffle
import random
import shutil

import sys_tools as st
import text_tools as tt

from baraja import Baraja
from naipe import Naipe
from jugador import Jugador, JugadorCPU, JugadorHumano
from botonCarta import BotonCarta


class Juego(st.Estados_Juego):
    def __init__(self, nJugadores):

        st.Estados_Juego.__init__(self)
        self.nJugadores = nJugadores
        # Crea a los n jugadores (incluyendo al usuario como jugador 0) y los guarda en una lista
        self.jugadores = []
        self.next = "MENU"
        self.st_done = False

        self.baraja = []  # Crea la baraja para la partida

        # Muestra la primera carta de la baraja para conseguir el trump
        self.trump = Naipe("Null", 0)
        self.w = 70
        self.h = 103
        self.atacante_count = 0 
        self.defensor_count = 0

        # Se tienen dos identificadores de jugador para no perder el orden de turno al realizar ataques/defensas

        #* Estos valores son "estaticos", solo cambian al finalizar la ronda de ataques
        self.turno = -1 # Indice del jugador al que le corresponde el turno original 
        self.defensor = -1 # Indice del jugador al que le corresponde defender

        self.atacante = -1  # Indice del jugador al que le corresponde el turno para atacar
        self.boolAtq = True # boolean que indica el jugador activo, True para atacante, False para defensor
        self.boolDfs = True # boolean que indica si el defensor tiene cartas para defender, en caso contrario perdera su turno hasta que todos los atacantes terminen
        self.atacantes = [] # Almacena a los atacantes en orden
        self.endTurn = False # boolean que indica si termino el turno.
        self.passers = [] # lista que almacena los atacantes que pasaron su turno 

        self.cartasJugadas = {"ataque": [], "defensa": []}
        self.cartaHumano = Naipe("Null", 0) # Carta que puede jugar el humano, captada por el click en pantalla

        self.durak = -1 # Indice del player que termina siendo durak, -1 si la partida termina en draw
        self.gameFinished = False # Bool que determina si la partida sigue o termina

        # u1, u2 y u3 son las 3 cartas visibles del usuario

        # Retorna una lista con 3 o menos elementos de la mano del jugador (funciona con slicing), son clase Naipe
        self.listpos = 0
        self.manoVisible = []

        # Lista con el nombre de los archivos de las imagenes correspondientes para cada carta en manoVisible
        self.imagesName = []

       #Asignaciones en funcion gameStart()
        self.u1 = None
        self.u2 = None
        self.u3 = None


        # genera posiciones para cartas fijas, y crea lista de botones no interactivos
        # que corresponden a los jugadores AI de 1 a 5
        self.pos = [(20, 200), (20, 20), (369, 20), (700, 20), (700, 200)]
        self.bot_ai = list(map(lambda i: BotonCarta(
            self.pos[i][0], self.pos[i][1], self.w, self.h, "Grey_1.png", "Blue_1.png", False), [i for i in range(5)]))

        # t1 es la carta trump, se asigna en funcion gameStart()
        self.t1 = None

        # para desplazarse en la lista
        self.arrow_up = BotonCarta(600, 370, 30, 30, "up.png", False, False)
        self.arrow_down = BotonCarta(
            655, 370, 30, 30, "down.png", False, False)

        self.tomar = BotonCarta(600,400,85,40,"tomar_gris.png","tomar_red.png",True)
        self.pasar = BotonCarta(600,430,85,40,"pass_gris.png", "pass_red.png", True)
        self.pause = BotonCarta(720,360,30,30,"stop_gray.png","stop_blue.png",True)
        self.sound = BotonCarta(720,400,30,30,"sound_blue.png","sound_gray.png",True)
        self.music = BotonCarta(720,440,30,30,"music_blue.png","music_gray.png",True)


        #!!!Rehacer la lambda una vez que tenga internet, para tener lista y no variables soltadas
    '''
    def crearListButtons(self):
        list_buttons = lista(map(lambda i: BotonCarta(x,y,w,h,self.manoVisible[i].fileNaipe()),[i for i in range(2)]))
    '''

    def crearJugadores(self, nJugadores):
        jugadores = [JugadorCPU() for id in range(1, nJugadores)]
        jugadores.append(JugadorHumano())
        jugadores.reverse()  # Jugador humano siempre en indice 0
        return jugadores

    def repartirCartas(self, atacantes = [], screen = None):  # Repartir cartas al inicio de la partida o al finalizar un ataque
        if len(atacantes) == 0: 
            jugadores = self.jugadores
        else:
            jugadores = atacantes # Esto ocurrira si se tienen menos de 6 jugadores o mas de 36 cartas, future proof
        repartir = False
        for i in range(len(jugadores)):
            pygame
            if self.baraja.mostrarCantidad() > 0:
                if jugadores[i].mostrarCantidad() < 6:
                    repartir = True
                    self.jugadores[self.jugadores.index(jugadores[i])].sacarCarta(self.baraja.sacarDeBaraja())

            else:
                repartir = False

        if repartir == True:
            self.repartirCartas(atacantes, screen)

    def makeTrump(self):
        if self.nJugadores >= 6:  # Si son 6 jugadores, no quedaran cartas en la baraja despues de repartir
            return self.baraja.sacarTrumpCon6Jugadores()
        else:
            return self.baraja.sacarTrump()

    def cardOnScreen(self, screen, carta, pos, w=None, h=None):
        if (w == None) | (h == None):
            w = self.w
            h = self.h
        img = carta.getImgNaipe(w, h)
        screen.blit(img, pos)

    def getDefensor(self, defensa = -1):
        if defensa == -1: # valor al inicio del juego
            if self.turno == (len(self.jugadores) - 1):
                self.defensor = 0
            else:
                self.defensor = self.turno + 1
        else: 
            if self.defensor == (len(self.jugadores) - 1):
                self.defensor = 0
            else:
                self.defensor += 1

        if (self.jugadores[self.defensor].mostrarCantidad() == 0) or (self.defensor == self.atacante):
            self.getDefensor(self.defensor)
        self.boolDfs = True

    def actualizarTurno(self):
        if self.turno == (len(self.jugadores) - 1):
            self.turno = 0
        else:
            self.turno += 1
        
        if self.turno == self.defensor and self.boolDfs == False:
            self.actualizarTurno() # Si no pudo defender pierde el turno

        if self.jugadores[self.turno].mostrarCantidad() == 0: # Los jugadores sin cartas en la mano no juegan
            self.actualizarTurno()
        else:
            self.getDefensor()
            self.atacante = self.turno
            self.boolAtq = True
            self.boolDfs = True
            print("El atacante inicial es el jugador " + str(self.atacante) + " y el defensor de esta ronda es " + str(self.defensor))
    
    def nextAtaquer(self):
        if self.atacante == (len(self.jugadores) - 1):
            self.atacante = 0
        else:
            self.atacante += 1

        if self.jugadores[self.atacante].mostrarCantidad() == 0:
            self.nextAtaquer()
        
        if self.atacante == self.defensor:
            self.nextAtaquer()

    def getActivePlayer(self):
        if self.boolAtq == True:
            return self.atacante
        else:
            return self.defensor

    def makeFirstPlayer(self):
        trumps = [jugador.getLowerTrump(self.trump) for jugador in self.jugadores] # lista con los menores trump de los jugadores
        self.turno = trumps.index(min(trumps))
        self.atacante = self.turno
        self.boolAtq = True
        self.getDefensor()
        print("El primer jugador es " + str(self.atacante) + " y el defensor de esta ronda es " + str(self.defensor))
    

    def changeActive(self):
        if self.boolAtq == True and self.boolDfs == True: # Si boolDfs es falso, el defensor no tiene para defender por lo tanto no tendra mas turnos
            self.boolAtq = False
        else:
            self.boolAtq = True

    def checkGame(self):
        cantNaipes = [jugador.mostrarCantidad() for jugador in self.jugadores]
        if cantNaipes.count(0) == (len(self.jugadores) - 1): # 1 jugador quedo con cartas en su mano
            self.gameFinished = True
            for i in range(len(cantNaipes)):
                if cantNaipes[i] != 0:
                    self.durak = i # Asigna el indice del durak
    


        elif cantNaipes.count(0) == len(self.jugadores): # todos los jugadores quedaron con 0 cartas (draw)
            self.gameFinished = True
        return self.gameFinished
    
    def getDurak(self):
        return self.durak

    def play(self, posicion, screen, carta = "pass"):
        pos_zona = [(180,180), (250,180), (320, 180), (390, 180), (460, 180), (530,180)]
        pos_zona_desfase = [(190,220),(260,220),(330, 220),(400, 220),(470, 220),(550,220)]
        # Maneja la continuidad de los turnos
        if posicion == self.atacante and len(self.passers) > 0:
            if posicion == self.passers[0]:
                self.endTurn = True
                self.atacante_count = 0
                self.defensor_count = 0
                self.passers = []
                print("Ningun jugador fue capaz de realizar un ataque, fin del turno") 
                return

        if posicion != 0: # si es la cpu consigue la carta a jugar de manera interna, a diferencia del humano
            carta = self.jugadores[posicion].jugarCarta(self.cartasJugadas, self.trump, self.boolAtq)
        else:
            self.jugadores[posicion].jugarCarta(carta) # Elimina la carta de la mano del humano
        if carta == "pass":
            print("El jugador " + str(posicion) + " no tiene cartas válidas")

            if posicion == self.defensor:
                self.boolDfs = False # Ya no puede seguir defendiendo
                self.changeActive()

            else:
                self.nextAtaquer() # Ya no tiene cartas para atacar -> pasa al siguiente atacante
                if self.jugadores[posicion].mostrarCantidad() > 0:
                    self.passers.append(posicion)
        else:
            if posicion == self.defensor:
                self.cartasJugadas["defensa"].append(carta)
                #blitea cartas sobre la pantalla, hasta 6
                if self.defensor_count < 6:
                    self.cardOnScreen(screen, carta, pos_zona_desfase[self.defensor_count], 55, 83)
                    self.defensor_count += 1
                if self.defensor_count ==  6:
                    self.defensor_count = 0

                print("El jugador " + str(posicion) + " defendió con la carta " + carta.printNaipe())
                self.changeActive()

                if posicion == 0:
                    self.refreshUI(screen)
                else:
                    self.actualizarMano(self.defensor)


            else:
                self.cartasJugadas["ataque"].append(carta)
                self.atacantes.append(self.jugadores[posicion]) 
                #blitea cartas sobre la pantalla, hasta 6
                if self.atacante_count < 6:
                    self.cardOnScreen(screen, carta, pos_zona[self.atacante_count], 55, 83)
                    self.atacante_count += 1
                if self.atacante_count == 6:
                    self.atacante_count = 0

                print("El jugador " + str(posicion) + " atacó con la carta " + carta.printNaipe())
                self.passers = []
                self.changeActive()
                if posicion == 0:
                    self.refreshUI(screen)
                else:
                    self.actualizarMano(self.atacante)

        # test consola
        ataq = [carta.printNaipe() for carta in self.cartasJugadas["ataque"]]
        defe = [carta.printNaipe() for carta in self.cartasJugadas["defensa"]]

        print("\ncartas en juego:\nAtaque: ", " ".join(ataq))
        print("Defensa: ", " ".join(defe)+ "\n")

        print("Turno del jugador " + str(self.getActivePlayer()))
        
    
    def game(self, screen):
        if self.boolDfs == False:
            x = lambda carta: self.jugadores[self.defensor].sacarCarta(carta)
            for carta in self.cartasJugadas["ataque"] + self.cartasJugadas["defensa"]:
                x(carta)
            if self.defensor == 0:
                self.refreshUI(screen)
            else: 
                self.actualizarMano(self.defensor)
            

        self.cartasJugadas = {"ataque": [], "defensa": []}
        
        self.endTurn = False
        self.actualizarTurno()

        # Future proof
        self.repartirCartas(self.atacantes, screen)
        self.repartirCartas([self.jugadores[self.defensor]], screen)

        self.atacantes= []

        # Revisa si la partida termino
        self.checkGame()
        if self.gameFinished:
            print ("Game Over")
            if self.durak != -1:
                print ("El jugador " + self.durak + " es nuestro querido Durak, felicidades, perdedor.")
            self.st_done = True
        else:
            # avanzar los turnos
            self.actualizarTurno()

    # Lista con las cartas de la mano del humano que se pueden jugar en este turno
    def cartasPosibles(self):
        return self.jugadores[0].posiblesCartas(self.cartasJugadas, self.trump, self.atacante == 0)   

    def getImagesName(self):
        return [carta.fileNaipe() for carta in self.manoVisible]

    def clean(self):
        pass

    def avanzarListPos(self, action):
        # usaremos cantidad para acotar cuantas veces se puede bajar/subir
        canti = self.jugadores[0].mostrarCantidad()
        if action:  # True = down
            if (canti % 3) == 0:
                if self.listpos >= int(canti / 3) - 1:
                    self.listpos = 0
                else:
                    self.listpos += 1
            else:
                if (self.listpos >= int(canti/3)):
                    self.listpos = 0 
                else:
                    self.listpos += 1

        else:  # False = up
            if self.listpos > 0:
                self.listpos -= 1
            elif self.listpos == 0:
                # vuelve a la ultima "pagina"
                #self.listpos = int(canti / 3) - 1
                if (canti % 3) == 0:
                    self.listpos = int(canti / 3) - 1
                else:
                    self.listpos = int(canti/3)
 
        print("Posicion actual en lista de naipes de humano es: ", self.listpos)

    def revisarJugada(self, naipe):

        if (len(self.cartasJugadas["ataque"]) < 6 or self.boolAtq == False) and self.gameFinished == False and self.endTurn == False:

            # Humano
            if (self.atacante == 0 and self.boolAtq == True) or ((self.defensor == 0 and self.boolAtq == False) and self.boolDfs == True):
                print("boolDfs = " + str(self.boolDfs))
            
                cartasPosibles = self.cartasPosibles()
                print("cartas posibles:")
                print([carta.printNaipe() for carta in cartasPosibles])

                if len(cartasPosibles) > 0:
                    if naipe.printNaipe() in [carta.printNaipe() for carta in cartasPosibles]: 
                        for carta in cartasPosibles:
                            if naipe.printNaipe() == carta.printNaipe():
                                self.cartaHumano = carta
                                return True
                    return False

    # Funcion para actualizar el numero de cartas que muestra cada jugador, no cacho como se hace tho asdnasjdn
    def actualizarMano(self, indice):
        nuevo_texto = tt.render_text("T", str(self.jugadores[indice].mostrarCantidad()), self.white)
        self.cant_Textos.remove(self.cant_Textos[indice])
        self.cant_Textos.insert(indice, nuevo_texto)

    def get_event(self, event, keys, screen):
        
        # Para los hovers/ clickeos sobre las CARTAS
        # sobre carta 1
                
        #agregar no reaccionar a las cartas nulas
        
        # Carta 1


        if self.u1.getRekt().collidepoint(pygame.mouse.get_pos()) and self.revisarJugada(self.u1.makeNaipe()) == True and self.checkGame() != True and self.mode_pause:   

            self.u1.mouseOverButton(True, 340)
            

            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Clickeando sobre CARTA1")
                print(self.cartaHumano.printNaipe())
                self.play(0, screen, self.cartaHumano)
        else:
            self.u1.mouseOverButton(False, 370)
        

        # Carta 2
        if self.u2.getRekt().collidepoint(pygame.mouse.get_pos()) and self.revisarJugada(self.u2.makeNaipe()) == True and self.checkGame() != True and self.mode_pause:   

            self.u2.mouseOverButton(True, 340) 

            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Clickeando sobre CARTA2")
                print(self.cartaHumano.printNaipe())
                self.play(0, screen, self.cartaHumano)
        else:
            self.u2.mouseOverButton(False, 370)
            

        # Carta 3
        if self.u3.getRekt().collidepoint(pygame.mouse.get_pos()) and self.revisarJugada(self.u3.makeNaipe()) == True and self.checkGame() != True and self.mode_pause:   

            self.u3.mouseOverButton(True, 340) 

            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Clickeando sobre CARTA1")
                print(self.cartaHumano.printNaipe())
                self.play(0, screen, self.cartaHumano)
        else:
            self.u3.mouseOverButton(False, 370)

        # Si esque el humano no tiene cartas validas para jugar
        if (self.atacante == 0 and self.boolAtq == True) or ((self.defensor == 0 and self.boolAtq == False) and self.boolDfs == True) and self.checkGame() != True and self.mode_pause:
            
            #humano es el defensor, puede tomar cartas en cualquier momento (no solo si no pueda defenderse). Tecla: t
            if self.defensor == 0: 
                    self.tomar.isActivePlayer(True)
                    print("El jugador 0 es un defensor, y no tiene cartas para defenderse o prefiere tomar")
                    if (self.tomar.getRekt().collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_t):
                        self.tomar.isActivePlayer(False)
                        print("El jugador 0 es un defensor, y se lleva todas las cartas :(")
                        self.play(0, screen, "pass")
            #humano es un atacante, decide por su cuenta si atacar o pasar el turno. Tecla : p
            elif self.atacante == 0:
                self.pasar.isActivePlayer(True)
                print("El jugador 0 es un atacante, y puede no atacar")
                if (self.pasar.getRekt().collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN) or (event.type == pygame.KEYDOWN and event.key == pygame.K_p):
                    print("El jugador 0 es un atacante, y decide no atacar")
                    self.pasar.isActivePlayer(False)
                    self.play(0, screen, "pass")
                            

        # Para solo clickeos/teclado up down sobre las FLECHAS 
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or (event.type == pygame.MOUSEBUTTONDOWN and self.arrow_up.getRekt().collidepoint(pygame.mouse.get_pos())) and self.mode_pause:
            self.avanzarListPos(False)
            self.manoVisible = self.jugadores[0].manoAcotada(self.listpos)
            self.refreshUI(screen)
        
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or (event.type == pygame.MOUSEBUTTONDOWN and self.arrow_down.getRekt().collidepoint(pygame.mouse.get_pos())) and self.mode_pause:
            self.avanzarListPos(True)
            self.manoVisible = self.jugadores[0].manoAcotada(self.listpos)
            self.refreshUI(screen)

        #En juego se para al presionar SPACE o al usar el boton chiquitito pause
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or (event.type == pygame.MOUSEBUTTONDOWN and self.pause.getRekt().collidepoint(pygame.mouse.get_pos())):
            if self.mode_pause:
                self.mode_pause = False 
            else:
                self.mode_pause = True


        '''
        if  self.checkGame() == True:
            print ("Gracias por jugar")
            x = input()
        '''

        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.quit = True
            pygame.quit()
            quit()

        
    def mostrarTrump(self, screen):
        trumpImg = self.t1.getImg()
        trump_text = tt.render_text(
            "T", "Triunfo: " + self.trump.printNaipe(), self.white)
        screen.blit(trump_text, (self.t1.getX() - 65, self.t1.getY() - 18))
        screen.blit(trumpImg, (self.t1.getX(), self.t1.getY()))

    def refreshUI(self, screen = None):
        self.u1 = BotonCarta(267, 370, self.w, self.h,
                            self.manoVisible[0].fileNaipe(), False, True)
        self.u2 = BotonCarta(369, 370, self.w, self.h,
                                self.manoVisible[1].fileNaipe(), False, True)
        self.u3 = BotonCarta(471, 370, self.w, self.h,
                            self.manoVisible[2].fileNaipe(), False, True)

        self.actualizarMano(0)

    def mostrarCantidadNaipes(self, screen, listaTextos):
        screen.blit(listaTextos[0],
                    (self.u2.getX() + 33, self.u2.getY() + 107))
        list(map(lambda i: screen.blit(listaTextos[i + 1], (self.bot_ai[i].getX(
        ) + 33, self.bot_ai[i].getY() + 107)), [i for i in range(5)]))

    def mostrarOponentes(self, screen):
        list(map(lambda i: screen.blit(self.bot_ai[i].getImg(
        ), (self.bot_ai[i].getX(), self.bot_ai[i].getY())), [i for i in range(5)]))

    def gameStart(self, screen):
        self.jugadores = self.crearJugadores(self.nJugadores)
        self.baraja = Baraja()  # Crea la baraja para la partida
        self.repartirCartas(self.jugadores, screen)

        self.trump = self.makeTrump()

        self.makeFirstPlayer()

        self.manoVisible = self.jugadores[0].manoAcotada(self.listpos)

        # Lista con el nombre de los archivos de las imagenes correspondientes para cada carta en manoVisible
        self.imagesName = self.getImagesName()

        #!! rehacer con lambda x = 267, y = 370, w = 70, h = 130 - iniciales, para avanzar en 102 en lambda
        #Dibuja las 3 cartas visibles de la mano del usurio
        self.manoVisible = self.jugadores[0].manoAcotada(self.listpos)

        self.u1 = BotonCarta(267, 370, self.w, self.h,
                             self.manoVisible[0].fileNaipe(), False, True)
        self.u2 = BotonCarta(369, 370, self.w, self.h,
                             self.manoVisible[1].fileNaipe(), False, True)
        self.u3 = BotonCarta(471, 370, self.w, self.h,
                             self.manoVisible[2].fileNaipe(), False, True)

        # t1 es la carta trump
        self.t1 = BotonCarta(
            100, 400, 50, 67, self.trump.fileNaipe(), False, False)
    def mostrarFlechas(self, screen):
        down = self.arrow_down.getImg()
        up = self.arrow_up.getImg()
        screen.blit(down, (self.arrow_down.getX(), self.arrow_down.getY()))
        screen.blit(up, (self.arrow_up.getX(), self.arrow_up.getY()))

    def mostrarTomar(self, screen):
        screen.blit(self.tomar.getImg(),(self.tomar.getX(),self.tomar.getY()))

    def mostrarPasar(self, screen):
        screen.blit(self.pasar.getImg(),(self.pasar.getX(),self.pasar.getY()))

    def mostrarOptions(self, screen):
        screen.blit(self.pause.getImg(),(self.pause.getX(),self.pause.getY()))
        screen.blit(self.music.getImg(),(self.music.getX(),self.music.getY()))
        screen.blit(self.sound.getImg(),(self.sound.getX(),self.sound.getY()))

    def generarCantidades(self):
        cant_Textos = list(map(lambda i: tt.render_text("T", str(self.jugadores[i].mostrarCantidad()), self.white), [i for i in range(1, 6)]))
        cant_Textos.insert(0, tt.render_text("S", str(self.jugadores[0].mostrarCantidad()), self.white))
        return cant_Textos

    def render(self, clock, screen, p):

        screen.fill(self.background_color)
        self.mode_pause = True
        # Prepara para dibujar
        self.gameStart(screen) # Inicializa valores para el juego
        # Mano del humano muestra 3 cartas

        self.cant_Textos = self.generarCantidades()

        self.refreshUI(screen) 
        

        while not self.st_done:
            if self.mode_pause:
                #dibuja mano de jugador, siempre debe estar en la pantalla
                self.cardOnScreen(
                    screen, self.manoVisible[0], (self.u1.getX(), self.u1.getY()))
                self.cardOnScreen(
                    screen, self.manoVisible[1], (self.u2.getX(), self.u2.getY()))
                self.cardOnScreen(
                    screen, self.manoVisible[2], (self.u3.getX(), self.u3.getY()))


                self.mostrarOponentes(screen)
                # Debajo de cada carta, se imprime la cantidad de naipes de cada jugador.
                self.mostrarCantidadNaipes(screen, self.cant_Textos)
                # Muestra la trump
                self.mostrarTrump(screen)
                #Muestra las felchas
                self.mostrarFlechas(screen)
                #muestra el boton tomar
                self.mostrarTomar(screen)
                #muestra el boton pasar
                self.mostrarPasar(screen)
                #muestra el boton de pausar,musica y sonidos
                self.mostrarOptions(screen)


                pygame.display.update()
                #screen.fill(self.background_color,(self.u1.getX(),self.u1.getY(),800,300))
                # Turno de la CPU
                if not ((self.atacante == 0 and self.boolAtq == True) or ((self.defensor == 0 and self.boolAtq == False) and self.boolDfs == True) and self.checkGame() != True):
                    pygame.time.wait(900) # Timer de 1.5 segundos para que no reviente la consola 
                    if  self.checkGame() != True:
                        print(self.boolAtq)
                        if self.boolAtq == True:
                            print("turno de atacante")
                            self.play(self.atacante, screen)
                        else:
                            if self.boolDfs == True:
                                print("turno de defensor")
                                self.play(self.defensor, screen)
                        
            
                if (len(self.cartasJugadas["ataque"]) == 6 and self.boolAtq == True)  or self.endTurn == True: # Siguiente turno
                    self.game(screen)
                    screen.fill(self.background_color)
            
            else:
                pause_text = tt.render_text("M", "PAUSE", self.white)
                count = 0
                while not self.mode_pause:
                    #rellenan la pantalla con background_color, sin blitear sobre las cartas
                    #porque al volver a presionar SPACE, queremos volver a jugar y ver las cartas sobre la mesa
                    screen.fill(self.background_color,(0,0,p[0],p[1]//2 - 100))
                    screen.fill(self.background_color,(0,p[1]//2 + 100,p[0],p[1]//2 + 100))
                    screen.fill(self.background_color,(0,0,p[0]//2 - 300,p[1]))
                    screen.fill(self.background_color,(p[0]//2 + 300,0,p[0]//2,p[1]))

                    screen.blit(pause_text, (p[0]/2 - pause_text.get_width()//2, 20))


                    term_text = tt.render_text("S", ">Presione SPACE para volver a jugar...", self.white_to_bg_fade[count % len(self.white_to_bg_fade)])
                    screen.blit(term_text, (p[0]/2 - term_text.get_width() //
                                    2, p[1] - term_text.get_height() - 100// 2))
                    pygame.display.flip()
                    count += 1
                    clock.tick(5)
                    [self.get_event(event, pygame.key.get_pressed(), screen) for event in pygame.event.get()]
                #como estoy volviendo al juego, relleno de nuevo la pantalla para blitear cartas de opontentes y al humano sobre ella
                screen.fill(self.background_color,(0,0,p[0],p[1]//2 - 100))
                screen.fill(self.background_color,(0,p[1]//2 + 100,p[0],p[1]//2 + 100))
                screen.fill(self.background_color,(0,0,p[0]//2 - 300,p[1]))
                screen.fill(self.background_color,(p[0]//2 + 300,0,p[0]//2,p[1]))

            [self.get_event(event, pygame.key.get_pressed(), screen) for event in pygame.event.get()]
            #despues de todo, como las cartas de humano se suben y bajan, aparte bliteo un rectangulo
            #que me llene solo la zona activa de humano
            screen.fill(self.background_color,(0,p[1]//2 + 70,p[0],p[1]//2)) 
            