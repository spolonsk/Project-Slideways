"""
Auteur : Sébastien Polonski
Matricule : 499415
Description : Projet Slideways partie 4
"""

from sys import argv
from PyQt5.QtWidgets import QApplication
from gui import App


def main():
    """Fonction principale qui permet de lancer le programme et la fenêtre de jeu"""
    
    app = QApplication(argv)
    if not app:
        app = QApplication(argv)
    ex = App()
    return app.exec_()


if __name__ == '__main__':
    exit(main())
