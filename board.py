"""
Auteur : Sébastien Polonski
Matricule : 499415
Description : fichier contenant le plateau
"""

from utils import *


class Action:
    '''
    Action to be played on the board.
    :attribute row: row_idx to play the action on
    :attribute col: None if offset or col_idx to play on
    :attribute direction: None if placement or either LEFT or RIGHT
    '''
    def __init__(self, row, col=None, direction=None):
        '''
        Constructor of class `Action`.
        :param row: row_idx to play the action on
        :param col: None if offset or col_idx to play on
        :param direction: None if placement or either LEFT or RIGHT
        '''
        self.row = row
        self.col = col
        self.direction = direction
        if not (self.direction in (None, LEFT, RIGHT) and \
                self.row in range(4) and \
                (self.col in range(4) or self.col is None) and \
                col is not None or direction is not None):
            raise InvalidActionException()

    def is_offset(self):
        '''
        :return: True if action is an offset
        '''
        return not self.is_placement()

    def is_placement(self):
        '''
        :return: True if action is a placement
        '''
        return self.direction is None

    def __eq__(self, other):  # détermine si deux action sont les mêmes, ayant les mêmes attributs
        return self.row == other.row and \
               self.col == other.col and \
               self.direction == other.direction

    def __str__(self):
        if self.is_offset():
            return f'{"-+"[(self.direction+1)//2]}{self.row}'
        else:
            return f'{"4321"[self.row]}{"ABCD"[self.col]}'

    def __repr__(self):
        return str(self)


class Board:
    '''
    Plateau de jeu représentant l'état de la partie
    :attribute offset: liste d'entier représantant le décalage
    :attribute grid: matrice contenant chaque case
    :attribute last_actions: action prises
    '''
    def __init__(self):
        '''
        Constructeurr de la classe `Board`
        '''
        self.reset()

    def reset(self):
        '''
        Remise à l'état inital du plateau
        '''
        self.offset = [0 for y in range(4)]
        self.grid = [[0 for x in range(4)] for y in range(4)]
        self.last_actions = list()
        self.played_boards = set()
        self.played_moves = list()
        
    def get_grid(self):
        '''
        Plateau actuel
        '''
        return self.grid
        
    def get_offset(self):
        '''
        Décalage actuel
        '''
        return self.offset

    def get_valid_actions(self, player):
        '''
        Donne tous les coups possibles sur le plateau actuel
        :param player: id du joueur qui veut agir
        :return: liste des actions
        '''
        columns = rows = range(4)
        # placement possibles
        actions = [Action(row, col) for col in columns for row in rows if self.grid[row][col] != player]
        # décalages possibles
        actions += [Action(row, None, direction=direction) for row in rows for direction in (LEFT, RIGHT) \
                        if -3 <= self.offset[row]+direction <= +3]
        # Enlève l'action
        if self.last_actions:
            last_action = self.last_actions[-1][0]
            if last_action.is_placement():
                if last_action in actions:
                    actions.remove(last_action)
            else:
                actions.remove(Action(last_action.row, col=None, direction=-last_action.direction))

        # coups menants aux plateaux déja joués
        for action in actions:
            # joue le coup
            if action.is_placement():
                self.last_actions.append((action, self.grid[action.row][action.col]))
                self.grid[action.row][action.col] = player
            else:
                self.last_actions.append((action, None))
                self.offset[action.row] += action.direction

            values = self.get_values()  # valeurs du plateau + offset après coup
            if values in self.played_boards:  # action invalide menant à un plateau joué
                del actions[actions.index(action)]
            else:
                pass
            self.undo()  # remet le plateau à son état d'origine
        return actions

    def get_values(self):
        """
        Fonction permettant d'avoir les valeurs d'un plateau(grid+offset) sous forme de str
        afin de ne plus le rencontrer par la suite
        :return: values : str contenant les valeurs de grid et offset
        """
        values = ""
        for row in self.grid:
            for elem in row:
                values = values + str(elem)  # ajout de chaque élément du plateau
        for offset in self.offset:
            values = values + str(offset)  # ajout de chaque décalage
        return values

    def save_game(self):
        """
        Fonction permettant de sauvegarder les coups joués dans un fichier dédié
        :return: None
        """
        lst = self.played_moves
        with open('out.sldws', 'w') as output:
            for elem in lst:
                output.write(elem)
                if elem != lst[-1]:
                    output.write(",")

    def act(self, action, player):
        '''
        Agis sur le plateau
        :param action: instance de la classe `Action` contenant l'action à exécuter
        :param player: id du joueur qui veut jouer
        :raise: `InvalidActionException` si l'action est invalide
        '''
        if action not in self.get_valid_actions(player):
            raise InvalidActionException()
        if action.is_placement():
            self.last_actions.append((action, self.grid[action.row][action.col]))
            self.grid[action.row][action.col] = player
        else:
            self.last_actions.append((action, None))
            self.offset[action.row] += action.direction

    def undo(self):
        '''
        Défait la dernière action
        '''
        last_action, color = self.last_actions.pop()
        if last_action.is_placement():
            self.grid[last_action.row][last_action.col] = color
        else:
            self.offset[last_action.row] -= last_action.direction

    @staticmethod
    def find_all_winners(dico):
        '''
        Get the list of potential winners given in the values of dico
        :param dico: a dict whose keys are ignored and whose values are lists of integers
        '''
        return list(map(set, filter(lambda seq: len(seq) == 4 and 0 not in seq, dico.values())))

    def winner(self):
        '''
        Find the winner of the current board.
        :return: a (possibly empty) list of winners.
        '''
        min_index = max(self.offset)
        max_index = min(self.offset) + 3
        columns = {i: list() for i in range(min_index, max_index+1)}
        rows = {i: self.grid[i] for i in range(4)}
        diagonals, skew_diagonals = self.extract_diagonals()

        for col in range(min_index, max_index+1):
            for row in range(4):
                columns[col].append(self.grid[row][col-self.offset[row]])

        potential_winners = \
            Board.find_all_winners(columns) + \
            Board.find_all_winners(rows) + \
            Board.find_all_winners(diagonals) + \
            Board.find_all_winners(skew_diagonals)

        winners = list({seq.pop() for seq in potential_winners if len(seq) == 1 and seq != {0}})

        return winners

    def extract_diagonals(self):
        '''
        Isolate all the k-diagonals and k-skew-diagonals on the board.
        :return: a tuple (diagonals, skew_diagonals) of dictionaries.

        For k in range(offset[0], offset[0]+4):
            diagonals[k] is a list containing the k-diagonal
            skew_diagonals[k] is a list containing the k-skew-diagonal
        Note that the length of these diagonals lies between 1 and 4.
        '''

        min_index = self.offset[0]
        max_index = 3 + self.offset[0]
        diagonals = {i: list() for i in range(min_index, max_index + 1)}
        skew_diagonals = {i: list() for i in range(min_index, max_index + 1)}

        for col in range(min_index, max_index + 1):
            for i in range(4):
                for j in range(4):
                    # Are we currently on the appropriate diagonal
                    if j + self.offset[i] == col + i:
                        diagonals[col].append(self.grid[i][j])
                    # Are we currently on the appropriate skew-diagonal
                    if j + self.offset[i] == col - i:
                        skew_diagonals[col].append(self.grid[i][j])

        return diagonals, skew_diagonals



