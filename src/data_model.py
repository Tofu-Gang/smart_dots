__author__ = 'Tofu Gang'

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import QRectF, QPointF, Qt
from PyQt5.QtGui import QPen
from src.path_finding import VisibilityGraph
from src.population import Population

################################################################################

class DataModel(QGraphicsScene):
    WIDTH = 800
    HEIGHT = 800
    WALL_THICKNESS = 5
    ALLOWED_AREA = QRectF(QPointF(-WIDTH/2, -HEIGHT/2), QPointF(WIDTH/2, HEIGHT/2))
    START_POINT = QPointF(0, HEIGHT/2-20)
    GOAL_POINT = QPointF(0, -HEIGHT / 2 + 20)
    GOAL_TOLERANCE = 50
    # walls around the allowed area
    WALLS_SURROUNDING = []
    # left
    WALLS_SURROUNDING.append(QRectF(QPointF(ALLOWED_AREA.left()-WALL_THICKNESS, ALLOWED_AREA.top()-WALL_THICKNESS),
                                    QPointF(ALLOWED_AREA.left(), ALLOWED_AREA.bottom()+WALL_THICKNESS)))
    # right
    WALLS_SURROUNDING.append(QRectF(QPointF(ALLOWED_AREA.right(), ALLOWED_AREA.top()-WALL_THICKNESS),
                                    QPointF(ALLOWED_AREA.right()+WALL_THICKNESS, ALLOWED_AREA.bottom()+WALL_THICKNESS)))
    # top
    WALLS_SURROUNDING.append(QRectF(QPointF(ALLOWED_AREA.left()-WALL_THICKNESS, ALLOWED_AREA.top()-WALL_THICKNESS),
                                    QPointF(ALLOWED_AREA.right()+WALL_THICKNESS, ALLOWED_AREA.top())))
    # bottom
    WALLS_SURROUNDING.append(QRectF(QPointF(ALLOWED_AREA.left()-WALL_THICKNESS, ALLOWED_AREA.bottom()),
                                    QPointF(ALLOWED_AREA.right()+WALL_THICKNESS, ALLOWED_AREA.bottom()+WALL_THICKNESS)))
    # custom walls
    WALLS_CUSTOM = []
    WALLS_CUSTOM.append(QRectF(QPointF(ALLOWED_AREA.left()-WALL_THICKNESS, HEIGHT/4), QPointF(ALLOWED_AREA.left()+WIDTH-100, HEIGHT/4+WALL_THICKNESS)))
    WALLS_CUSTOM.append(QRectF(QPointF(ALLOWED_AREA.left()+100, 0), QPointF(ALLOWED_AREA.right()+WALL_THICKNESS, WALL_THICKNESS)))
    VISIBILITY_GRAPH = VisibilityGraph(START_POINT, GOAL_POINT, WALLS_CUSTOM+WALLS_SURROUNDING, ALLOWED_AREA)

################################################################################

    def __init__(self):
        """

        """

        super().__init__()
        self.setSceneRect(self.ALLOWED_AREA)
        self._population = Population(self)
        self._generationCountItem = self.addSimpleText('gen: '+str(self._population.generationCount))
        self._generationCountItem.setPos(QPointF(-self.WIDTH/2+20, -self.HEIGHT/2+20))
        self._wonCountItem = self.addSimpleText('won: '+str(self._population.wonCount))
        self._wonCountItem.setPos(QPointF(-self.WIDTH/2+20, -self.HEIGHT/2+40))
        self._exhaustedCountItem = self.addSimpleText('exh: '+str(self._population.exhaustedCount))
        self._exhaustedCountItem.setPos(QPointF(-self.WIDTH/2+20, -self.HEIGHT/2+60))
        self._deadCountItem = self.addSimpleText('ded: '+str(self._population.deadCount))
        self._deadCountItem.setPos(QPointF(-self.WIDTH/2+20, -self.HEIGHT/2+80))
        self._population.updateCounters.connect(self._updateCounters)
        self._ctrlFlag = False

################################################################################

    @property
    def walls(self):
        """

        :return:
        """

        return self.WALLS_SURROUNDING+self.WALLS_CUSTOM

################################################################################

    def _updateCounters(self):
        """

        """

        self._generationCountItem.setText('gen: '+str(self._population.generationCount))
        self._wonCountItem.setText('won: '+str(self._population.wonCount))
        self._exhaustedCountItem.setText('exh: '+str(self._population.exhaustedCount))
        self._deadCountItem.setText('ded: '+str(self._population.deadCount))

################################################################################

    def mousePressEvent(self, event):
        """

        """

        self._population.start()
        super().mousePressEvent(event)

################################################################################

    def keyPressEvent(self, event):
        """

        """

        key = event.key()
        if key == Qt.Key_Control:
            self._ctrlFlag = True
            self.update()
        super().keyPressEvent(event)

################################################################################

    def keyReleaseEvent(self, event):
        """

        """

        key = event.key()
        if key == Qt.Key_Control:
            self._ctrlFlag = False
            self.update()
        super().keyReleaseEvent(event)

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
        painter.drawEllipse(self.START_POINT, 5, 5)
        painter.setPen(Qt.green)
        painter.setBrush(Qt.green)
        painter.drawEllipse(self.GOAL_POINT, self.GOAL_TOLERANCE, self.GOAL_TOLERANCE)
        painter.setPen(Qt.black)
        super().drawBackground(painter, rect)

################################################################################

    def drawForeground(self, painter, rect):
        """

        """

        painter.setPen(QPen(Qt.red, 1, join=Qt.MiterJoin))
        painter.setBrush(Qt.red)
        for rect in self.WALLS_SURROUNDING:
            painter.drawRect(rect)
        for rect in self.WALLS_CUSTOM:
            painter.drawRect(rect)
        if self._ctrlFlag:
            painter.setPen(Qt.green)
            for edge in self.VISIBILITY_GRAPH.shortestRouteEdges:
                painter.drawLine(edge)
        else:
            painter.setPen(Qt.black)
            for edge in self.VISIBILITY_GRAPH.edges:
                painter.drawLine(edge)
        super().drawForeground(painter, rect)

################################################################################
