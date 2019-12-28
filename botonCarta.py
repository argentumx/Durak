import pygame
import sys_tools as st
import text_tools as tt

# recibe una img extra, "activa", si la imagen debe cambiar.
# pensar en que jackets de los AI's se ponen azules al estar activos.


class BotonCarta():
    def __init__(self, x, y, width, height, nombre, activa, enabled):

        self.imagen = pygame.image.load(
            st.current_dir() + "/data/cards/{}".format(nombre)).convert_alpha()
        self.imagen = pygame.transform.scale(self.imagen, (width, height))

        if activa != False:
            self.imagen_activa = pygame.image.load(
                st.current_dir() + "/data/cards/{}".format(activa)).convert_alpha()
            self.imagen_activa = pygame.transform.scale(
                self.imagen_activa, (width, height))

        self.imagen_inactiva = self.imagen

        self.u1 = pygame.Rect(x, y, width, height)

        self.long = x

        self.tall = y

        self.enabled = enabled

    def mouseOverButton(self):
        if self.enabled == True:
            #mover la carta hacia arriba
            print("Me estan clickeando/hovereando")
        else:
            #nada lol
            pass
            print("No se puede utilizar la carta seleccionada.")

    # se usara para cambiar de jacket para los jugadores NPC
    # y en menu
    def isActivePlayer(self, param):
        if param:
            self.imagen = self.imagen_activa
        else:
            self.imagen = self.imagen_inactiva

    def turnOffBoton(self):
        self.enabled = False

    def turnOnBoton(self):
        self.enabled = True

    def getRekt(self):
        return self.u1

    def getImg(self):
        return self.imagen

    def getX(self):
        return self.long

    def getY(self):
        return self.tall