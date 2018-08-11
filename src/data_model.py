__author__ = 'Tofu Gang'

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPen, QPainterPath
from src.dot import Dot
from random import randint

################################################################################

class DataModel(QGraphicsScene):
    WIDTH = 400
    HEIGHT = 400
    WALL_THICKNESS = 5
    ALLOWED_AREA = QRectF(QPointF(-WIDTH/2, -HEIGHT/2), QPointF(WIDTH/2, HEIGHT/2))
    WALLS = QPainterPath()
    WALLS.setFillRule(Qt.OddEvenFill)
    # walls around the allowed area
    WALLS.addRect(ALLOWED_AREA.adjusted(-WALL_THICKNESS, -WALL_THICKNESS, WALL_THICKNESS, WALL_THICKNESS))
    WALLS.addRect(ALLOWED_AREA)
    # some random wall
    WALLS.addRect(QRectF(QPointF(-50, -WALL_THICKNESS / 2),
                         QPointF(50, WALL_THICKNESS / 2)))
    START_AREA = QRectF(QPointF(-100, HEIGHT/4), QPointF(100, HEIGHT/2-WALL_THICKNESS))
    WINNING_AREA = QRectF(QPointF(-100, -HEIGHT/2+WALL_THICKNESS), QPointF(100, -HEIGHT/4))
    POPULATION = 200

################################################################################

    def __init__(self):
        """

        """

        super().__init__()
        self.setSceneRect(self.ALLOWED_AREA)
        self._winCounter = 0
        self._exhaustedCounter = 0
        self._deadCounter = 0
        self._winCounterItem = self.addSimpleText(str(self._winCounter))
        self._exhaustedCounterItem = self.addSimpleText(str(self._exhaustedCounter))
        self._deadCounterItem = self.addSimpleText(str(self._deadCounter))
        self._winCounterItem.setPos(self.WINNING_AREA.center())
        self._exhaustedCounterItem.setPos(QPointF(self.START_AREA.center().x(), self.START_AREA.top()))
        self._deadCounterItem.setPos(QPointF(self.START_AREA.center().x(), self.START_AREA.bottom()-self._deadCounterItem.boundingRect().height()))
        self._population = []

################################################################################

    def _processDot(self):
        """

        """
        dot = self.sender().dot
        if dot.state is dot.State.WON:
            self._winCounter += 1
            self._winCounterItem.setText(str(self._winCounter))
            stepsCount = dot.stepsCount
        elif dot.state is dot.State.EXHAUSTED:
            self._exhaustedCounter += 1
            self._exhaustedCounterItem.setText(str(self._exhaustedCounter))
        elif dot.state is dot.State.DEAD:
            self._deadCounter += 1
            self._deadCounterItem.setText(str(self._deadCounter))

        self._population.remove(dot)
        self.removeItem(dot)
        self._checkCounters()

################################################################################

    def _checkCounters(self):
        """

        """

        if len(self._population) == 0:
            if self._winCounter+self._exhaustedCounter+self._deadCounter == self.POPULATION:
                self._winCounterItem.setText(str(self._winCounter)+' ✔')
                self._exhaustedCounterItem.setText(str(self._exhaustedCounter)+' ✔')
                self._deadCounterItem.setText(str(self._deadCounter)+' ✔')
            else:
                self._winCounterItem.setText(str(self._winCounter) + ' ✘')
                self._exhaustedCounterItem.setText(str(self._exhaustedCounter) + ' ✘')
                self._deadCounterItem.setText(str(self._deadCounter) + ' ✘')

################################################################################

    def _resetCounters(self):
        """

        """

        self._winCounter = 0
        self._winCounterItem.setText(str(self._winCounter))
        self._exhaustedCounter = 0
        self._exhaustedCounterItem.setText(str(self._exhaustedCounter))
        self._deadCounter = 0
        self._deadCounterItem.setText(str(self._deadCounter))

################################################################################

    def _start(self):
        """

        """

        self._resetCounters()

        for _ in range(self.POPULATION):
            dot = Dot()
            dot.brain.finished.connect(self._processDot)
            self._population.append(dot)
            x = randint(self.START_AREA.left(), self.START_AREA.right())
            y = randint(self.START_AREA.top(), self.START_AREA.bottom())
            dot.setPos(x, y)
            self.addItem(dot)
            dot.start()

################################################################################

    def mousePressEvent(self, event):
        """

        """

        self._start()
        super().mousePressEvent(event)

################################################################################

    def drawBackground(self, painter, rect):
        """

        """

        painter.setPen(Qt.gray)
        painter.setBrush(Qt.gray)
        painter.drawRect(rect)
        painter.setBrush(Qt.white)
        painter.drawRect(self.ALLOWED_AREA)
        painter.setPen(Qt.blue)
        painter.setBrush(Qt.blue)
        painter.drawRect(self.START_AREA)
        painter.setPen(Qt.green)
        painter.setBrush(Qt.green)
        painter.drawRect(self.WINNING_AREA)
        painter.setPen(Qt.black)
        super().drawBackground(painter, rect)

################################################################################

    def drawForeground(self, painter, rect):
        """

        """

        painter.setPen(QPen(Qt.red, self.WALL_THICKNESS, join=Qt.MiterJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.WALLS)
        super().drawForeground(painter, rect)

################################################################################
