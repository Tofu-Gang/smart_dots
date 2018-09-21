__author__ = 'Tofu Gang'

from PyQt5.QtGui import QPen, QPainterPath
from PyQt5.QtCore import Qt, pyqtSignal as Signal, QThread, QLineF, QPointF, QRectF
from PyQt5.QtWidgets import QGraphicsObject
from time import sleep
from random import uniform, random
from math import pi, sin, cos
from enum import Enum
from src.path_finding import PathFinding, VisibilityGraph

################################################################################

class Dot(QGraphicsObject):
    DIAMETER_REGULAR = 5
    DIAMETER_CHAMPION = 8
    BOUNDING_RECT_REGULAR = QRectF(QPointF(-DIAMETER_REGULAR/2, -DIAMETER_REGULAR/2), QPointF(DIAMETER_REGULAR/2, DIAMETER_REGULAR/2))
    BOUNDING_RECT_CHAMPION = QRectF(QPointF(-DIAMETER_CHAMPION/2, -DIAMETER_CHAMPION/2), QPointF(DIAMETER_CHAMPION/2, DIAMETER_CHAMPION/2))
    SHAPE_REGULAR = QPainterPath()
    SHAPE_REGULAR.addEllipse(BOUNDING_RECT_REGULAR)
    SHAPE_CHAMPION = QPainterPath()
    SHAPE_CHAMPION.addEllipse(BOUNDING_RECT_CHAMPION)
    PEN_WIDTH = 1
    ACCELERATION_LIMIT = 5

    class State(Enum):
        ALIVE = 0
        WON = 1
        EXHAUSTED = 2
        DEAD = 3

    class Type(Enum):
        REGULAR = 0
        CHAMPION = 1

################################################################################

    def __init__(self, population, vectors=None, type=Type.REGULAR):
        """

        """

        self._type = type
        self._population = population
        super().__init__()
        self._brain = Brain(population, vectors)
        self._brain.move.connect(self._move)
        self._usedVectors = []
        self._distanceTravelled = 0
        self._acceleration = [0.0, 0.0]
        self._velocity = [0.0, 0.0]
        self._state = self.State.ALIVE

################################################################################

    def boundingRect(self):
        """

        :return:
        """

        if self._type is self.Type.REGULAR:
            return self.BOUNDING_RECT_REGULAR
        elif self._type is self.Type.CHAMPION:
            return self.BOUNDING_RECT_CHAMPION
        else:
            return None

################################################################################

    def shape(self):
        """

        :return:
        """

        if self._type is self.Type.REGULAR:
            return self.SHAPE_REGULAR
        elif self._type is self.Type.CHAMPION:
            return self.SHAPE_CHAMPION
        else:
            return None

################################################################################

    def paint(self, painter, option, widget=None):
        """

        :param painter:
        :param option:
        :param widget:
        :return:
        """
        if self._state is self.State.ALIVE:
            if self._type is self.Type.REGULAR:
                painter.setBrush(Qt.white)
            elif self._type is self.Type.CHAMPION:
                painter.setBrush(Qt.blue)
            else:
                pass
        elif self._state is self.State.DEAD:
            painter.setBrush(Qt.darkRed)
        elif self._state is self.State.WON:
            painter.setBrush(Qt.darkGreen)
        elif self._state is self.State.EXHAUSTED:
            painter.setBrush(Qt.gray)
        painter.setPen(QPen(Qt.black, self.PEN_WIDTH, Qt.SolidLine))
        painter.drawEllipse(self.boundingRect())

################################################################################

    @property
    def dotType(self):
        """

        """

        return self._type

################################################################################

    @dotType.setter
    def dotType(self, value):
        """

        """

        self.prepareGeometryChange()
        self._type = value
        self.update()

################################################################################

    @property
    def child(self):
        """

        """

        return Dot(self._population, self._brain.vectors.copy())

################################################################################

    @property
    def usedVectorsCount(self):
        """

        """

        return len(self._usedVectors)

################################################################################

    def mutate(self):
        """

        """

        self._brain.mutate()

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

    def _setState(self, value):
        """

        :param value:
        :return:
        """

        self._state = value
        self.update()

################################################################################

    @property
    def fitnessFunction(self):
        """

        """

        if self._state is self.State.WON:
            return 1/16+10000/pow(len(self._usedVectors), 2)
        else:
            # TODO: no idea why the self._visibilityGraph isn't created when the dot reaches the goal
            try:
                distanceToFinish = self._visibilityGraph.shortestRouteDistance
            except AttributeError:
                self._visibilityGraph = VisibilityGraph(self.pos(), self.scene().GOAL_POINT, self.scene().WALLS_CUSTOM+self.scene().WALLS_SURROUNDING, self.scene().ALLOWED_AREA)
                distanceToFinish = self._visibilityGraph.shortestRouteDistance
            return 1/pow(distanceToFinish, 2)

################################################################################

    def _move(self):
        """

        """

        if self.scene():
            vector = self._brain.getVector()
            self._acceleration[0] += vector[0]
            self._acceleration[1] += vector[1]
            accMagnitude = pow(pow(self._acceleration[0], 2)+pow(self._acceleration[1], 2), 0.5)
            if accMagnitude > self.ACCELERATION_LIMIT:
                self._acceleration[0] *= self.ACCELERATION_LIMIT/accMagnitude
                self._acceleration[1] *= self.ACCELERATION_LIMIT/accMagnitude

            self._velocity[0] += self._acceleration[0]
            self._velocity[1] += self._acceleration[1]
            newPos = QPointF(self.pos().x()+self._velocity[0], self.pos().y()+self._velocity[1])

            # collisions check
            moveLine = QLineF(self.pos(), newPos)
            if any(PathFinding.intersects(rect, moveLine) for rect in self.scene().WALLS_SURROUNDING) \
              or any(PathFinding.intersects(rect, moveLine) for rect in self.scene().WALLS_CUSTOM):
                self._setState(self.State.DEAD)
                self._stop()
            else:
                self.setPos(newPos)
                self._usedVectors.append(vector)
                self._distanceTravelled += moveLine.length()
                if QLineF(newPos, self.scene().GOAL_POINT).length() < self.scene().GOAL_TOLERANCE:
                    self._setState(self.State.WON)
                    self._stop()
                elif len(self._usedVectors) == self._population.maxVectorsCount:
                    self._setState(self.State.EXHAUSTED)
                    self._stop()

################################################################################

    def start(self):
        """

        """

        self._brain.start()

################################################################################

    def _stop(self):
        """

        """

        self._brain.stop()
        self._visibilityGraph = VisibilityGraph(self.pos(), self.scene().GOAL_POINT, self.scene().WALLS_CUSTOM+self.scene().WALLS_SURROUNDING, self.scene().ALLOWED_AREA)

################################################################################

class Brain(QThread):
    move = Signal()
    MUTATION_RATE = 0.01
    DELAY = 0.1

################################################################################

    def __init__(self, population, vectors=None):
        """

        """

        super().__init__()
        self._population = population
        if vectors:
            self._vectors = vectors
        else:
            # random vectors
            self._vectors = [(cos(angle), sin(angle)) for angle in [uniform(0, 2*pi) for _ in range(self._population.maxVectorsCount)]]
        self._vectorBuffer = []
        self._isRunning = False
        self.finished.connect(self.deleteLater)

################################################################################

    @property
    def vectors(self):
        """

        """

        return self._vectors

################################################################################

    def mutate(self):
        """

        """

        for i in range(len(self._vectors)):
            rand = random()
            if rand < self.MUTATION_RATE:
                angle = uniform(-pi, pi)
                self._vectors[i] = (cos(angle), sin(angle))

################################################################################

    def getVector(self):
        """

        """

        vector = self._vectorBuffer[0]
        del self._vectorBuffer[0]
        return vector

################################################################################

    def run(self):
        """

        """

        self._isRunning = True
        i = 0
        while self._isRunning and i < self._population.maxVectorsCount:
            self._vectorBuffer.append(self._vectors[i])
            self.move.emit()
            i += 1
            sleep(self.DELAY)

################################################################################

    def stop(self):
        """

        """

        self._isRunning = False

################################################################################
