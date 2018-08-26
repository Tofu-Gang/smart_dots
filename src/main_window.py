__author__ = 'Tofu Gang'

from PyQt5.QtWidgets import QMainWindow, QGraphicsView
from src.data_model import DataModel

################################################################################

class MainWindow(QMainWindow):
    WIDTH = 900
    HEIGHT = 900

################################################################################

    def __init__(self):
        super().__init__()
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        model = DataModel()
        view = QGraphicsView(model)
        self.setCentralWidget(view)

################################################################################