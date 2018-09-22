__author__ = 'Tofu Gang'

from PyQt5.QtGui import QPen, QPainterPath
from PyQt5.QtCore import QPointF, QRectF, QLineF, Qt, QPropertyAnimation, \
    pyqtSignal as Signal
from PyQt5.QtWidgets import QGraphicsObject
from enum import Enum
from math import cos, sin, pi, ceil
from random import uniform, random
from src.path_finding import PathFinding, VisibilityGraph

################################################################################

class Dot(QGraphicsObject):

    class State(Enum):
        ALIVE = 0
        WON = 1
        EXHAUSTED = 2
        DEAD = 3

    class Type(Enum):
        REGULAR = 0
        CHAMPION = 1

    DIAMETER_REGULAR = 5
    DIAMETER_CHAMPION = 8
    BOUNDING_RECT_REGULAR = QRectF(QPointF(-DIAMETER_REGULAR/2, -DIAMETER_REGULAR/2),
                                   QPointF(DIAMETER_REGULAR/2, DIAMETER_REGULAR/2))
    BOUNDING_RECT_CHAMPION = QRectF(QPointF(-DIAMETER_CHAMPION/2, -DIAMETER_CHAMPION/2),
                                    QPointF(DIAMETER_CHAMPION/2, DIAMETER_CHAMPION/2))
    SHAPE_REGULAR = QPainterPath()
    SHAPE_REGULAR.addEllipse(BOUNDING_RECT_REGULAR)
    SHAPE_CHAMPION = QPainterPath()
    SHAPE_CHAMPION.addEllipse(BOUNDING_RECT_CHAMPION)
    PEN_WIDTH = 1

    ACCELERATION_LIMIT = 5
    MUTATION_RATE = 0.01

    finished = Signal()

################################################################################

    def __init__(self, population, vectors=None, dotType=Type.REGULAR):
        """

        """

        super().__init__()
        self._dotType = dotType
        self._state = self.State.ALIVE
        self._population = population
        self._animation = QPropertyAnimation(self, b'pos')
        self._animation.finished.connect(self._stepFinished)
        if vectors:
            self._vectors = vectors
        else:
            # random vectors
            self._vectors = [(cos(angle), sin(angle)) for angle in
                             [uniform(0, 2*pi)
                              for _ in range(self._population.maxVectorsCount)]]
        self._usedVectors = []
        self._distanceTravelled = 0
        self._acceleration = [0.0, 0.0]
        self._velocity = [0.0, 0.0]

################################################################################

    def boundingRect(self):
        """

        :return:
        """

        if self._dotType is self.Type.REGULAR:
            return self.BOUNDING_RECT_REGULAR
        elif self._dotType is self.Type.CHAMPION:
            return self.BOUNDING_RECT_CHAMPION
        else:
            return self.BOUNDING_RECT_REGULAR

################################################################################

    def shape(self):
        """

        :return:
        """

        if self._dotType is self.Type.REGULAR:
            return self.SHAPE_REGULAR
        elif self._dotType is self.Type.CHAMPION:
            return self.SHAPE_CHAMPION
        else:
            return self.SHAPE_REGULAR

################################################################################

    def paint(self, painter, option, widget=None):
        """

        :param painter:
        :param option:
        :param widget:
        :return:
        """

        if self._state is self.State.ALIVE:
            if self._dotType is self.Type.REGULAR:
                painter.setBrush(Qt.white)
            elif self._dotType is self.Type.CHAMPION:
                painter.setBrush(Qt.blue)
            else:
                pass
        elif self._state is self.State.DEAD:
            painter.setBrush(Qt.darkRed)
        elif self._state is self.State.WON:
            painter.setBrush(Qt.darkGreen)
        elif self._state is self.State.EXHAUSTED:
            painter.setBrush(Qt.gray)
        else:
            pass

        painter.setPen(QPen(Qt.black, self.PEN_WIDTH, Qt.SolidLine))
        painter.drawEllipse(self.boundingRect())

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
    def usedVectorsCount(self):
        """

        """

        return len(self._usedVectors)

################################################################################

    @property
    def fitnessFunction(self):
        """

        """

        if self._state is self.State.WON:
            return 1/16+10000/pow(len(self._usedVectors), 2)
        else:
            distanceToFinish = self._visibilityGraph.shortestRouteDistance
            return 1/pow(distanceToFinish, 2)

################################################################################

    def setChampion(self):
        """

        :return:
        """

        self.prepareGeometryChange()
        self._dotType = self.Type.CHAMPION
        self.update()

################################################################################

    def getChild(self):
        """

        """

        return Dot(self._population, self._usedVectors.copy())

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

    def life(self):
        """

        :return:
        """

        self._makeStep()

################################################################################

    def _makeStep(self):
        """

        :return:
        """

        vector = self._vectors[0]
        del self._vectors[0]
        self._useVector(vector)
        newPos = QPointF(self.pos().x()+self._velocity[0], self.pos().y()+self._velocity[1])

        # collisions check
        moveLine = QLineF(self.pos(), newPos)
        collidingWalls = [wall for wall in self.scene().walls if PathFinding.intersects(wall, moveLine)]
        if len(collidingWalls) > 0:
            self._setState(self.State.DEAD)
            for wall in collidingWalls:
                # find out which sides of the wall the vector intersects, find the
                # first collision point and set it as the new dot position
                for wallSide in [QLineF(wall.topLeft(), wall.topRight()),
                                 QLineF(wall.topLeft(), wall.bottomLeft()),
                                 QLineF(wall.topRight(), wall.bottomRight()),
                                 QLineF(wall.bottomLeft(), wall.bottomRight())]:
                    point = QPointF()
                    if wallSide.intersect(moveLine, point) == QLineF.BoundedIntersection:
                        if QLineF(self.pos(), point).length() < moveLine.length():
                            newPos = point
                            moveLine = QLineF(self.pos(), newPos)
                # set the new position slightly further from the wall, it messes the
                # visibility graph initialization otherwise
                newPos = moveLine.pointAt(0.99)
                moveLine = QLineF(self.pos(), newPos)
        elif QLineF(newPos, self.scene().GOAL_POINT).length() < self.scene().GOAL_TOLERANCE:
            self._setState(self.State.WON)

        velocityMagnitude = pow(pow(self._velocity[0], 2)+pow(self._velocity[1], 2), 0.5)
        self._distanceTravelled += moveLine.length()
        self._animation.setDuration(ceil(moveLine.length()/velocityMagnitude)*50)
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(newPos)
        self._animation.start()

################################################################################

    def _useVector(self, vector):
        """

        :param vector:
        :return:
        """

        self._acceleration[0] += vector[0]
        self._acceleration[1] += vector[1]

        accMagnitude = pow(pow(self._acceleration[0], 2)+pow(self._acceleration[1], 2), 0.5)
        if accMagnitude > self.ACCELERATION_LIMIT:
            self._acceleration[0] *= self.ACCELERATION_LIMIT/accMagnitude
            self._acceleration[1] *= self.ACCELERATION_LIMIT/accMagnitude

        self._velocity[0] += self._acceleration[0]
        self._velocity[1] += self._acceleration[1]

        self._usedVectors.append(vector)

################################################################################

    def _stepFinished(self):
        """

        :return:
        """

        if self._state is self.State.ALIVE:
            if len(self._vectors) > 0:
                self._makeStep()
            else:
                self._setState(self.State.EXHAUSTED)
                self._finalize()
        else:
            self._finalize()

################################################################################

    def _finalize(self):
        """

        :return:
        """

        self._visibilityGraph = VisibilityGraph(self.pos(),
                                                self.scene().GOAL_POINT,
                                                self.scene().walls,
                                                self.scene().ALLOWED_AREA)
        self.finished.emit()

################################################################################
