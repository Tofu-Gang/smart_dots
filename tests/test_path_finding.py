from unittest import TestCase, main
from PyQt5.QtCore import QRectF, QPointF, QLineF
from src.path_finding import PathFinding

################################################################################

class TestPathFinding(TestCase):

################################################################################

    def setUp(self):
        """

        """

        #       --left     --right
        #       '          '
        #   I   |    II    |  III
        # ------+==========+------   --top
        #  VIII |  IX (in) |  IV
        # ------+==========+------   --bottom
        #  VII  |    VI    |   V

        self._offset = 10
        self._rect = QRectF(QPointF(-20, -10), QPointF(20, 10))
        self._pointI = QPointF(self._rect.left()-self._offset, self._rect.top()-self._offset)
        self._pointII = QPointF(self._rect.center().x(), self._rect.top()-self._offset)
        self._pointIII = QPointF(self._rect.right()+ self._offset, self._rect.top()- self._offset)
        self._pointIV = QPointF(self._rect.right()+self._offset, self._rect.center().y())
        self._pointV = QPointF(self._rect.right()+self._offset, self._rect.bottom()+self._offset)
        self._pointVI = QPointF(self._rect.center().x(), self._rect.bottom()+self._offset)
        self._pointVII = QPointF(self._rect.left()-self._offset, self._rect.bottom()+self._offset)
        self._pointVIII = QPointF(self._rect.left()-self._offset, self._rect.center().y())
        self._pointIX = self._rect.center()

        self._lineI_VII = QLineF(self._pointI, self._pointVII)
        self._lineI_V = QLineF(self._pointI, self._pointV)
        self._lineII = QLineF(self._pointII, QPointF(self._rect.center().x(), self._rect.top()))
        self._lineII_IV = QLineF(QPointF(self._rect.right()-self._offset, self._rect.top()-self._offset),
                                 QPointF(self._rect.right()+self._offset, self._rect.top()+self._offset))

################################################################################

    def testPointRectDist(self):
        """

        """

        lineI = PathFinding.pointRectDist(self._pointI, self._rect)
        self.assertEqual(lineI.p2(), self._rect.topLeft())
        self.assertEqual(lineI.length(), pow(pow(self._offset, 2)+pow(self._offset, 2), 0.5))
        lineII = PathFinding.pointRectDist(self._pointII, self._rect)
        self.assertEqual(lineII.p2(), QPointF(self._rect.center().x(), self._rect.top()))
        self.assertEqual(lineII.length(), self._offset)
        lineIII = PathFinding.pointRectDist(self._pointIII, self._rect)
        self.assertEqual(lineIII.p2(), self._rect.topRight())
        self.assertEqual(lineIII.length(), pow(pow(self._offset, 2)+pow(self._offset, 2), 0.5))
        lineIV = PathFinding.pointRectDist(self._pointIV, self._rect)
        self.assertEqual(lineIV.p2(), QPointF(self._rect.right(), self._rect.center().y()))
        self.assertEqual(lineIV.length(), self._offset)
        lineV = PathFinding.pointRectDist(self._pointV, self._rect)
        self.assertEqual(lineV.p2(), self._rect.bottomRight())
        self.assertEqual(lineV.length(), pow(pow(self._offset, 2)+pow(self._offset, 2), 0.5))
        lineVI = PathFinding.pointRectDist(self._pointVI, self._rect)
        self.assertEqual(lineVI.p2(), QPointF(self._rect.center().x(), self._rect.bottom()))
        self.assertEqual(lineVI.length(), self._offset)
        lineVII = PathFinding.pointRectDist(self._pointVII, self._rect)
        self.assertEqual(lineVII.p2(), self._rect.bottomLeft())
        self.assertEqual(lineVII.length(), pow(pow(self._offset, 2)+pow(self._offset, 2), 0.5))
        lineVIII = PathFinding.pointRectDist(self._pointVIII, self._rect)
        self.assertEqual(lineVIII.p2(), QPointF(self._rect.left(), self._rect.center().y()))
        self.assertEqual(lineVIII.length(), self._offset)
        lineIX = PathFinding.pointRectDist(self._pointIX, self._rect)
        self.assertEqual(lineIX.p2(), self._pointIX)
        self.assertEqual(lineIX.length(), 0)

################################################################################

    def testIntersects(self):
        """

        """

        rect = QRectF(QPointF(-50, -10), QPointF(50, 10))
        # line completely outside of the rectangle
        self.assertFalse(PathFinding.intersectPoint(rect, QLineF(QPointF(-100, -50), QPointF(-100, 50))))
        # the line is a top side of the rectangle
        self.assertFalse(PathFinding.intersectPoint(rect, QLineF(rect.topLeft(), rect.topRight())))
        # the line starts at the left corner of the rectangle and is not perpendicular to any of the rectangle sides;
        # the line ends outside of the rectangle, not going through it
        self.assertFalse(PathFinding.intersectPoint(rect, QLineF(rect.topLeft(), QPointF(-100, -100))))
        # the line starts at the left corner of the rectangle and is perpendicular to the top side of the rectangle;
        # the line ends outside of the rectangle, not going through it
        self.assertFalse(PathFinding.intersectPoint(rect, QLineF(rect.topLeft(), QPointF(rect.left(), rect.top() - 100))))
        # the line is horizontal and goes straight through the center of the rectangle
        self.assertTrue(PathFinding.intersectPoint(rect, QLineF(QPointF(-100, 0), QPointF(100, 0))))
        # the line is vertical and goes straight through the center of the rectangle
        self.assertTrue(PathFinding.intersectPoint(rect, QLineF(QPointF(0, -100), QPointF(0, 100))))
        # the line is vertical and goes up from the bottom right corner of the rectangle
        self.assertFalse(PathFinding.intersectPoint(rect, QLineF(rect.bottomRight(), QPointF(rect.right(), rect.top() - 100))))
        # the line is diagonal of the rectangle
        self.assertTrue(PathFinding.intersectPoint(rect, QLineF(rect.topLeft(), rect.bottomRight())))

################################################################################

if __name__ == '__main__':
    main()

################################################################################