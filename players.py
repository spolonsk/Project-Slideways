"""
Auteur : Sébatien Polonski
Matricule : 499415
Description : Amélioration de L' IA : implémentation de l'élagage alpha-beta
"""

from abc import ABCMeta, abstractmethod
import random
import time

from PyQt5.QtGui import QMouseEvent

from utils import *
from board import Action


class Player(metaclass=ABCMeta):
    '''
    Classe de base pour les joueurs
    :attribute player: id du joueur
    :attribute board: le plateau sur lequel le joueur joue
    :attribute is_playing: True durant le tour du joueur, faux sinon
    '''

    def __init__(self, player, board):
        '''
        Constructeur de `Player`
        :param player: id du joueur instancié
        :param board: e plateau sur lequel le joueur joue
        '''
        self.player = player
        self.board = board
        self.not_your_turn()

    def your_turn(self):
        '''
        C'est à son tour de jouer
        '''
        self.is_playing = True

    def not_your_turn(self):
        '''
        Ce n'est plus à son tour de jouer
        '''
        self.is_playing = False

    def is_currently_playing(self):
        '''
        Indique si le joueur doit jouer
        :return: True s'il doit jouer, faux sinon
        '''
        return self.is_playing

    @abstractmethod
    def play(self, event):
        pass


class HumanPlayer(Player):
    '''
    Classe pour le joueur humain
    '''

    def __init__(self, player, board):
        '''
        Constructeur de la classe `HumanPlayer`
        '''
        super().__init__(player, board)

    def play(self, event, offset=None):
        '''
        Fonction liée au click sur le plateau
        Joue l'action demandée sur le plateau
        :param event:  QMouseEvent généré
        :param offset: None si l'action est un placement ou tuple(direction,row)
        :raise: `InvalidActionException` si le joueur ne peut jouer ou si l'action est invalide
        '''
        if not self.is_currently_playing():
            raise InvalidActionException()
        if isinstance(event, QMouseEvent):
            self._play_placement(event)
        else:
            self._play_offset(offset)

    @staticmethod
    def pos2rowcol(x, y):
        '''
        Transforme une position (x, y) sur le plateau en un numéro de case
        :param x: position x
        :param y: position y
        :return: tuple (row_id, col_idx)
        '''
        return y // (CELL_SIZE + OFFSET), x // (CELL_SIZE + OFFSET)

    def _play_placement(self, event):
        '''
        Convertit QMouseEvent en action jouable.
        :param event: voir HumanPlayer.play
        :raise:       voir HumanPlayer.play
        '''
        x = event.x()
        y = event.y()
        row, col = HumanPlayer.pos2rowcol(x, y)
        col -= 3 + self.board.get_offset()[row]
        if col < 0 or col >= 4:
            raise InvalidActionException()
        # click sur self.board.grid[col][row]
        action = Action(row, col)
        self.board.act(action, self.player)
        self.board.played_boards.add(self.board.get_values())  # ajoute le plateau joué

    def _play_offset(self, offset):
        '''
        Convertit le tuple en action jouable
        :param offset: voir HumanPlayer.play
        :raise:        voir HumanPlayer.play
        '''
        if not isinstance(offset, tuple) or len(offset) != 2:
            raise InvalidActionException()
        direction, row = offset
        action = Action(row, col=None, direction=direction)
        self.board.act(action, self.player)
        self.board.played_boards.add(self.board.get_values())  # ajoute le plateau joué


class AIPlayer(Player):
    '''
    Classe de base pour le joueur IA
    '''

    def __init__(self, player, board):
        super().__init__(player, board)
        self.other_player = PLAYER_1 if self.player == PLAYER_2 else PLAYER_2

    def your_turn(self):
        '''
        Redéfini `Player.your_turn` par faisant jouer l'ia sur le plateau
        '''
        self.play(event=None)


class MinimaxPlayer(AIPlayer):
    '''
    IA utilisant l'algorithme minimax
    '''

    def __init__(self, player, board):
        super().__init__(player, board)

    def play(self, event=None):
        '''
        Joue le meilleur coup selon l'arbre de possibilités minimax
        :param event: ignoré
        '''
        starting_time = time.time()  # départ de la minuterie, avant que l'IA calcule son coup
        action = self.minimax()[0]
        if time.time() - starting_time < 1:  # L'ia a maximum 1 seconde pour jouer
            self.board.act(action, self.player)
            self.board.played_moves.append(action)  # ajoute l'action jouée
            self.board.played_boards.add(self.board.get_values())  # ajoute le plateau joué
        else:
            print("IA Disqualifiée")  # Disqualification de l'IA, reset du plateau
            self.board.reset()

    def minimax(self, depth=2, maximize=True, penalty=0, alpha=-1000, beta=1000):
        '''
        Fonction permettant de parcourir les coups possibles et d'en choisir les meilleurs en utilisant
        l'élagage alpha-beta et une pénalité selon la profondeur du coup voulu
        :param depth:   profondeur maximale utilisée pour explorer les coups possibles
        :param maximize: True si on veut maximiser le score, False sinon
        :param penalty:  pénalité de temps, augmente en fonction de la profondeur
        :param alpha: valeur utilisée pour comparer les scores rencontrés précédemment(max)
        :param beta:  valeur utilisée pour comparer les scores rencontrés précédemment(min)
        '''
        if depth == 0:  # fin de l'arbre, pas de coup gagnant
            return (None, DRAW - penalty)
        if maximize:
            # joueur max
            best_score = -INF
            player = self.player

        else:
            # joueur min
            best_score = +INF
            player = self.other_player
        best_actions = []

        valid_actions = self.board.get_valid_actions(player)
        for action in valid_actions:  # pour chaque action valide
            self.board.act(action, player)
            winner = self.board.winner()
            if len(winner) == 0:
                score = self.minimax(depth - 1, not maximize, penalty + 1, alpha, beta)[1]
            else:  # si le coup est gagnant
                score = WIN - penalty if winner.pop() == self.player else LOSS + penalty
            self.board.undo()

            if score > best_score:
                if maximize:
                    best_score = max(alpha, score)  # compare le score actuel avec alpha
                    if not (beta <= alpha):
                        best_actions = [(action, score)]
                    alpha = max(best_score, alpha)

            elif score < best_score:
                if not maximize:
                    best_score = min(score, beta)  # compare le score actuel avec beta
                    if not (beta <= alpha):
                        best_actions = [(action, score)]
                    beta = min(best_score, beta)

            else:
                best_actions.append((action, score))
        return random.choice(best_actions)
