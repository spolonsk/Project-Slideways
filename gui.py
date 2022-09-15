"""
Auteur : Sébastien Polonski
Matricule : 499415
Description : fichier contenant l'interface graphique
"""

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from board import Board
from players import *


class App(QMainWindow):
    '''
    Classe contenant l'interface graphique principale
    :attribute current_player: Joueur sensé jouer
    :attribute waiting_player: L'autre joueur
    :attribute time_interval: Entier donnant le délai avant une action de l'IA
    '''
    TITLE = 'INFOF-106 SlideWays'

    def __init__(self):
        '''
        Constructeur de la classe "App"
        '''
        super().__init__()
        self.init_vars()
        self.game_is_playing = False  # partie pas jouée
        self.current_player = None
        self.waiting_player = None
        self.initUI()

    def initUI(self):
        '''
        Création de l'interface en tant que telle : widgets et layouts
        :return: None
        '''
        self.setWindowTitle(App.TITLE)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_vbox = QVBoxLayout()

        self.settings_groupbox = QGroupBox('Settings')
        self.settings_grid = QGridLayout()
        self.settings_groupbox.setLayout(self.settings_grid)
        label = QLabel('Player 1:')
        self.settings_grid.addWidget(label, 0, 0, alignment=Qt.AlignRight)
        self.cb_player1 = QComboBox()
        self.cb_player1.addItems(['Minimax', 'Human'])
        self.settings_grid.addWidget(self.cb_player1, 0, 1)
        label = QLabel('Player 2:')
        self.settings_grid.addWidget(label, 1, 0, alignment=Qt.AlignRight)
        self.cb_player2 = QComboBox()
        self.cb_player2.addItems(['Minimax', 'Human'])
        self.settings_grid.addWidget(self.cb_player2, 1, 1)
        label = QLabel('Timer interval:')
        self.settings_grid.addWidget(label, 2, 0, alignment=Qt.AlignRight)
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.sliderReleased.connect(self.release_slider)
        self.time_slider.setTickInterval(10)
        self.time_slider.setValue(1)
        self.settings_grid.addWidget(self.time_slider, 2, 1)

        self.dialogbutton = QPushButton("Search file")  # rechercher fichier
        self.dialogbutton.clicked.connect(self.replay_game)
        self.settings_grid.addWidget(self.dialogbutton, 3, 0)
        self.checkbutton = QCheckBox("Save game")  # cocher la case pour sauvegarder
        self.settings_grid.addWidget(self.checkbutton, 3, 1, )
        self.main_vbox.addWidget(self.settings_groupbox)

        self.hbox = QHBoxLayout()

        self.left_buttons = ButtonPanel(self, '<', 4, self.handle_click_event, LEFT)
        self.hbox.addWidget(self.left_buttons)

        self.canvas = Canvas(self.board, parent=self.central_widget)
        self.canvas.mousePressEvent = self.handle_click_event
        self.hbox.addWidget(self.canvas)

        self.right_buttons = ButtonPanel(self, '>', 4, self.handle_click_event, RIGHT)
        self.hbox.addWidget(self.right_buttons)

        self.main_vbox.addLayout(self.hbox)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_game)
        self.main_vbox.addWidget(self.start_button)

        self.central_widget.setLayout(self.main_vbox)
        self.show()

    def release_slider(self):
        '''
        Met à jour l'interval de temps
        :return: None
        '''
        self.time_interval = self.time_slider.value() * 10

    def handle_click_event(self, event, offset=None):
        '''
        Fonction liée aux actions sur le plateau et les boutons de décalage
        :param event: contient la position(x,y) du click
        :param offset: tuple (direction, row)
        :return: None
        '''
        if self.current_player is None or not self.current_player.is_currently_playing():
            return
        if not isinstance(self.current_player, HumanPlayer):
            return
        try:
            self.current_player.play(event, offset)
        except InvalidActionException:
            pass
        else:
            self.toggle_players()

    def get_file_content(self):
        """
        Fonction permettant de choisir un fichier via QfileDialog et d'en extraire le contenu s'il est valide
        :return: data : liste contenant les coups à jouer si le fichier est valide, -1 sinon
        """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        data = []
        if dialog.exec_():
            file_name = dialog.selectedFiles()
            if file_name[0].endswith('.sldws'):  # fichier dédié contenant les coups joués
                with open(file_name[0], 'r') as f:
                    for line in f:
                        for elem in line.split(","):
                            data.append(elem)  # chaque coup joué dans l'ordre
            else:
                data = -1
        return data

    def replay_game(self):
        """
        Fonction permettant la rediffusion d'une partie jouée précédemment
        :return: None, affiche la rediffusion coup par coups
        """
        if not self.game_is_playing:  # si personne ne joue déja
            file_data = self.get_file_content()  # coups joués
            try:
                player = 0
                i = -1
                for elem in file_data:
                    i += 1
                    if i % 2 == 0:  # quel joueur joue
                        player = 1
                    else:
                        player = 2
                    time.sleep(1)
                    # selon que le coup soi un décalage ou un placement
                    if elem[0] == "+":
                        self.board.get_offset()[int(elem[1])] += 1
                    if elem[0] == "-":
                        self.board.get_offset()[int(elem[1])] -= 1
                    if elem[0] in "1234":
                        self.board.get_grid()[-int(elem[0])][ord(elem[1]) - 65] = player
                    self.repaint()  # met à jour l'affichage
                self.exhibit_end_of_game()  # fin de la partie rediffusée
            except:
                print("erreur")

    def init_vars(self):
        '''
        Initialise les variables liées au jeu
        :return: None
        '''
        self.board = Board()
        self.time_interval = 10

    @staticmethod
    def make_player(text, player_id, board):
        '''
        Crée un joueur selon les paramètres fournis
        :param text: 'AI' ou 'Human'
        :param player_id: id du joueur à créer
        :param board:  instance du plateau de jeu de classe `Board`
        :return: instance de la classe `Player`
        :raise: `ValueError` si le texte ne correspond pas aux données fournies
        '''
        if text == 'Minimax':
            return MinimaxPlayer(player_id, board)
        elif text == 'Human':
            return HumanPlayer(player_id, board)
        else:
            raise ValueError('Only \'Minimax\' and \'Human\' are valid player types')

    def start_game(self):
        '''
        Fonction liée au bouton "start/restart"
        :return: None
        '''
        self.start_button.setText('Restart')
        self.board.reset()
        self.player_1 = App.make_player(self.cb_player1.currentText(), 1, self.board)
        self.player_2 = App.make_player(self.cb_player2.currentText(), 2, self.board)
        self.current_player = self.player_2
        self.waiting_player = self.player_1
        self.canvas.update()
        self.toggle_players()  # Le joueur 1 joue
        self.game_is_playing = True  # la partie est jouée

    def toggle_players(self):
        '''
        échange le joueur actuel avec celui qui attend
        :return: None
        '''
        self.canvas.update()
        self.current_player.not_your_turn()
        if self.board.winner():
            self.exhibit_end_of_game()
            return
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.your_turn()
        if isinstance(self.current_player, AIPlayer):
            QTimer.singleShot(self.time_interval, self.toggle_players)

    def exhibit_end_of_game(self):
        '''
        Montre que la partie est terminée et affiche le gagnant
        '''
        # self.player_1.not_your_turn()
        if self.checkbutton.isChecked():  # Sauvegarde de la partie si la case est cochée
            self.board.save_game()
        popup = WinnerPopup(self.board.winner(), self)
        popup.exec_()  # Use exec_ instead of show to block main window
        self.start_button.setText('Start')


class WinnerPopup(QDialog):
    '''
    Popup affichant le/les gagnant(s) de la partie
    '''

    def __init__(self, winners, parent):
        '''
        Constructeur de la class `WinnerPopup`
        :param winners: liste de gagant(s)
        :param parent: parent du Qt Widget
        '''
        super().__init__(parent)
        assert len(winners) > 0
        if len(winners) == 1:
            text = f'Player {winners[0]} won!'
        else:
            text = 'Draw game: nobody won. Try again!'
        self.setFixedSize(QSize(500, 100))
        self.label = QLabel(text, self)
        self.label.setFont(QFont("Calibri", 20, QFont.Bold))
        label_width = self.label.fontMetrics().boundingRect(self.label.text()).width()
        label_height = self.label.fontMetrics().boundingRect(self.label.text()).height()
        self.label.move((self.width() - label_width) / 2, (self.height() - label_height) / 2)
        parent.game_is_playing = False  # partie terminée


class ButtonPanel(QWidget):
    '''
    Qt-compatible widget representing a panel containing several buttons intended for board offsets.
    :attribute buttons: list of QPushButton instances
    '''

    def __init__(self, parent, button_text, nb_buttons, button_callback, direction):
        '''
        Constructeurr de la class `ButtonPanel`.
        :param parent: parent du Qt Widget
        :param button_text: texte affiché sur chaque bouton
        :param nb_buttons: nombre de boutons à ajouter
        :param button_callback: fonction à appeler quand un bouton est clické
        :param direction: direction du décalage(+1 ou -1)
        '''
        # appeler le constructeur du parent
        super().__init__(parent=parent)
        self.setFixedSize(QSize(20, HEIGHT))
        self.buttons = list()
        for row in range(nb_buttons):
            self.buttons.append(QPushButton(button_text, parent=self))
            self.buttons[-1].setMaximumWidth(20)
            self.buttons[-1].clicked.connect(lambda _, row=row: button_callback(event=None, offset=(direction, row)))
            self.buttons[-1].move(0, OFFSET + CELL_SIZE // 2 + row * (CELL_SIZE + OFFSET) - 10)


class Canvas(QWidget):
    '''
    Widget représentant la zone où le plateau est affiché
    :attribute board: plateau
    '''

    def __init__(self, board, parent=None):
        '''
        Constructeurr de la classe `Canvas`
        :param board: instance de la classe `Board` qui sera représentée
        :param parent: parent du Qt widget
        '''
        super().__init__(parent=parent)
        self.board = board
        self.setFixedSize(QSize(WIDTH, HEIGHT))

    def paintEvent(self, event=None):
        '''
        Callback of the Update event on the canvas.
        :param event: ignored
        '''
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        '''
        Dessine le plateau sur la fenêtre.
        :param qp: instance de la classe `QPainter`
        '''
        grid = self.board.get_grid()
        offset = self.board.get_offset()
        self.draw_grid_debug(qp)
        # associe la couleur à chaque valeur possible
        colors = [Qt.white, Qt.yellow, Qt.red]
        qp.setPen(Qt.black)
        for row in range(4):
            qp.setBrush(Qt.darkBlue)
            # Dessine le rectangle de la rangée
            y = row * (CELL_SIZE + OFFSET) + OFFSET + CELL_SIZE // 2
            x = (CELL_SIZE + OFFSET) * (offset[row] + 3) + OFFSET + CELL_SIZE // 2
            ### (x, y) représente le milieu de la première case de la rangée
            qp.drawRect(
                x - CELL_SIZE // 2 + 5,
                y - CELL_SIZE // 2 + 5,
                3 * OFFSET + 4 * CELL_SIZE - 10,
                CELL_SIZE - 10
            )
            # Desssine chaques cercles de chaque rangée
            for col in range(4):
                qp.setBrush(colors[grid[row][col]])
                qp.drawEllipse(
                    x - CELL_SIZE // 2 + 10,
                    y - CELL_SIZE // 2 + 10,
                    CELL_SIZE - 20,
                    CELL_SIZE - 20
                )
                x += CELL_SIZE + OFFSET

    def draw_grid_debug(self, qp):
        '''
        Affichage debug
        :param qp: instance de la classe `QPainter`
        '''
        if not GRID_DEBUG:
            return
        qp.setPen(Qt.red)
        x = 0
        for i in range(10):
            x += OFFSET
            qp.drawLine(x, 0, x, HEIGHT)
            x += CELL_SIZE
            qp.drawLine(x, 0, x, HEIGHT)
        y = 0
        for i in range(4):
            y += OFFSET
            qp.drawLine(0, y, WIDTH, y)
            y += CELL_SIZE
            qp.drawLine(0, y, WIDTH, y)
