__author__ = 'Tofu Gang'

from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QThread, QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsEllipseItem
from math import pi, cos, sin
from random import uniform
from time import sleep
from enum import Enum

################################################################################

class Dot(QGraphicsEllipseItem):
    DIAMETER = 10
    PEN_WIDTH = 1

    class State(Enum):
        WON = 0
        EXHAUSTED = 1
        DEAD = 2

################################################################################

    def __init__(self):
        """

        """

        super().__init__(-self.DIAMETER/2, -self.DIAMETER/2, self.DIAMETER, self.DIAMETER)
        self.setBrush(Qt.white)
        self.setPen(QPen(Qt.black, self.PEN_WIDTH, Qt.SolidLine))
        self._brain = Brain(self)
        self._brain.move.connect(self.setPos)
        self._brain.won.connect(self._won)
        self._brain.exhausted.connect(self._exhausted)
        self._brain.died.connect(self._died)
        self._state = None
        self._stepsCount = None

################################################################################

    @property
    def brain(self):
        """

        """

        return self._brain

################################################################################

    @property
    def state(self):
        """

        """

        return self._state

################################################################################

    @property
    def stepsCount(self):
        """

        """

        return self._stepsCount

################################################################################

    def _won(self, stepsCount):
        """

        """

        self._state = self.State.WON
        self._stepsCount = stepsCount

################################################################################

    def _exhausted(self):
        """

        """

        self._state = self.State.EXHAUSTED

################################################################################

    def _died(self):
        """

        """

        self._state = self.State.DEAD

################################################################################

    def start(self):
        """

        """

        self._brain.start()

################################################################################

class Brain(QThread):
    move = Signal(float, float)
    won = Signal(int)
    exhausted = Signal()
    died = Signal()
    VECTORS_COUNT = 100

################################################################################

    def __init__(self, dot, vectors=None):
        """

        """

        super().__init__()
        self._dot = dot

        if vectors and len(vectors) == self.VECTORS_COUNT:
            self._vectors = vectors
        else:
            self._vectors = []
            for _ in range(self.VECTORS_COUNT):
                angle = uniform(-pi, pi)
                self._vectors.append((cos(angle), sin(angle)))

################################################################################

    @property
    def dot(self):
        """

        """

        return self._dot

################################################################################

    def run(self):
        """

        """

        walls = self._dot.scene().WALLS
        winningArea = self._dot.scene().WINNING_AREA
        acceleration = [0.0, 0.0]
        velocity = [0.0, 0.0]

        for i in range(len(self._vectors)):
            # apply the acceleration vector on the velocity vector and determine
            # the new dot position
            acceleration[0] += self._vectors[i][0]
            acceleration[1] += self._vectors[i][1]
            velocity[0] += acceleration[0]
            velocity[1] += acceleration[1]
            newX = self._dot.pos().x()+velocity[0]
            newY = self._dot.pos().y()+velocity[1]

            # collisions check
            pathRect = QRectF(QPointF(min(self._dot.pos().x(), newX), min(self._dot.pos().y(), newY)),
                              QPointF(max(self._dot.pos().x(), newX), max(self._dot.pos().y(), newY)))
            if walls.intersects(pathRect):
                self.died.emit()
                break
            elif winningArea.intersects(pathRect):
                self.won.emit(i+1)
                break
            else:
                self.move.emit(newX, newY)
                sleep(0.1)
        else:
            self.exhausted.emit()

################################################################################
