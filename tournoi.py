"""
Auteur : Sébastien Polonski
Matricule : 499415
Description : Fichier contenant l'IA participant au grand tournoi Mortal Slideways
"""

from players import Player, AIPlayer
from abc import ABCMeta, abstractmethod
import random
import time

from PyQt5.QtGui import QMouseEvent

from utils import *
from board import Action


class TournoiAIPlayer(AIPlayer):
    '''.
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
