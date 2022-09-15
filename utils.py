"""
Auteur : Sébastien Polonski
Matricule : 499415
"""

##### Constantes

########## Constantes d'affichage
CELL_SIZE = 100
OFFSET = 10
WIDTH = 10 * CELL_SIZE + 11 * OFFSET
HEIGHT = 4 * CELL_SIZE + 5 * OFFSET

########## True pour l'affichage "debug"
GRID_DEBUG = False

########## Constantes de jeu
EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2
LEFT = -1
RIGHT = +1

INF = float('inf')

########## valeurs minimax
WIN = +10
DRAW = 0
LOSS = -10


# Note : WIN > 1 permet de favoriser le gain rapide de la partie


class InvalidActionException(Exception):
    '''
    Exception levée quand une action invalide est créee ou jouée
    '''

    def __init__(self, msg=''):
        super().__init__(msg)
