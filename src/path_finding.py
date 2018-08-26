__author__ = 'Tofu Gang'

from PyQt5.QtCore import QPointF, QLineF
from math import inf
from enum import Enum
from itertools import product

################################################################################

class PathFinding():

################################################################################

    @staticmethod
    def pointRectDist(point, rect):
        """
        Calculates shortest distance between a point and a rectangle. QLineF
        object is returned, where point1 is the input point and point2 is closest
        to it in the rectangle.

                    --left     --right
                    '          '
                I   |    II    |  III
              ------+==========+------   --top
               VIII |  IX (in) |  IV
              ------+==========+------   --bottom
               VII  |    VI    |   V
        """

        if point.x() < rect.left():
            # region I, VIII, or VII
            if point.y() < rect.top():
                # I
                point2 = rect.topLeft()
            elif point.y() > rect.bottom():
                # VII
                point2 = rect.bottomLeft()
            else:
                # VIII
                point2 = QPointF(rect.left(), point.y())
        elif point.x() > rect.right():
            # region III, IV, or V
            if point.y() < rect.top():
                # III
                point2 = rect.topRight()
            elif point.y() > rect.bottom():
                # V
                point2 = rect.bottomRight()
            else:
                # IV
                point2 = QPointF(rect.right(), point.y())
        else:
            # region II, IX, or VI
            if point.y() < rect.top():
                # II
                point2 = QPointF(point.x(), rect.top())
            elif point.y() > rect.bottom():
                # VI
                point2 = QPointF(point.x(), rect.bottom())
            else:
                # IX
                point2 = point

        return QLineF(point, point2)

################################################################################

    @staticmethod
    def intersects(rect, line):
        """

        """

        keyLine = 'line'
        keyIntersection = 'intersection'
        rectLines = [{keyLine: QLineF(rect.topLeft(), rect.bottomLeft()),
                      keyIntersection: QPointF()},
                     {keyLine: QLineF(rect.topRight(), rect.bottomRight()),
                      keyIntersection: QPointF()},
                     {keyLine: QLineF(rect.topLeft(), rect.topRight()),
                      keyIntersection: QPointF()},
                     {keyLine: QLineF(rect.bottomLeft(), rect.bottomRight()),
                      keyIntersection: QPointF()}]
        rectCorners = [rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()]
        intersectingBounded = [rectLine for rectLine in rectLines if rectLine[keyLine].intersect(line, rectLine[keyIntersection]) == QLineF.BoundedIntersection]
        intersectingUnbounded = [rectLine for rectLine in rectLines if rectLine[keyLine].intersect(line, rectLine[keyIntersection]) == QLineF.UnboundedIntersection]
        noIntersection = [rectLine for rectLine in rectLines if rectLine[keyLine].intersect(line, rectLine[keyIntersection]) == QLineF.NoIntersection]

        if len(intersectingBounded) == 0:
            # line is completely outside of the rectangle
            return False
        elif len(intersectingBounded) == 2 \
          and intersectingBounded[0][keyLine].intersect(intersectingBounded[1][keyLine], QPointF()) == QLineF.NoIntersection \
          and all([rectLine[keyIntersection] in rectCorners for rectLine in intersectingBounded]):
            # a rectangle side is part of the line
            return False
        elif len(intersectingBounded) == 2 and intersectingBounded[0][keyIntersection] == intersectingBounded[1][keyIntersection]:
            # one line end is a corner of the rectangle, second line end is completely outside of the rectangle;
            # line angle with both intersecting rectangle sides is different from 90°
            return False
        elif len(intersectingBounded) == 1 and len(intersectingUnbounded) == 1 and len(noIntersection) == 2:
            # one line end is a corner of the rectangle, second line end is completely outside of the rectangle;
            # the line is perpendicular to the intersecting (bounded and unbounded) rectangle sides
            return False
        else:
            return True

################################################################################

class VisibilityGraph():

    class VertexType(Enum):
        START = 0
        INSIDE = 1
        END = 2

################################################################################

    def __init__(self, startPoint, goalPoint, walls, allowedArea):
        """

        """

        self._graph = []
        self._keyPoint = 'point'
        self._keyEdgesTo = 'edges_to'
        self._keyDistance = 'distance'
        self._keyPointPrevious = 'point_previous'
        self._keyVisited = 'visited'
        self._keyVertexType = 'vertex_type'

        self._makeVertices(startPoint, walls, goalPoint, allowedArea)
        self._makeEdges(walls)
        self._dijkstra()

################################################################################

    @property
    def edges(self):
        """

        """

        edges = []
        for graphEntry in self._graph:
            point = graphEntry[self._keyPoint]
            neighbours = graphEntry[self._keyEdgesTo]
            for neighbour in neighbours:
                edge = QLineF(point, neighbour)
                edgeRev = QLineF(neighbour, point)
                if edgeRev not in edges:
                    edges.append(edge)
        return edges

################################################################################

    @property
    def shortestRouteDistance(self):
        """

        """

        return sum(edge.length() for edge in self.shortestRouteEdges)

################################################################################

    @property
    def shortestRouteEdges(self):
        """

        """

        edges = []
        endEntry = sorted([graphEntry for graphEntry in self._graph if graphEntry[self._keyVertexType] == self.VertexType.END], key=lambda graphEntry: graphEntry[self._keyDistance])[0]
        graphEntry = endEntry
        while graphEntry[self._keyDistance] != 0:
            point = graphEntry[self._keyPoint]
            pointPrevious = graphEntry[self._keyPointPrevious]
            edges.append(QLineF(point, pointPrevious))
            graphEntry = self._graphEntry(pointPrevious)
        return edges

################################################################################

    def _makeVertices(self, startPoint, walls, goalPoint, allowedArea):
        """

        """

        # fill the graph with the starting point and all wall corners
        self._graph.append({self._keyPoint: startPoint,
                            self._keyEdgesTo: [],
                            self._keyDistance: 0,
                            self._keyPointPrevious: None,
                            self._keyVisited: False,
                            self._keyVertexType: self.VertexType.START})
        wallCorners = [wall.topLeft() for wall in walls] \
                     +[wall.topRight() for wall in walls] \
                     +[wall.bottomLeft() for wall in walls] \
                     +[wall.bottomRight() for wall in walls]
        wallCorners = [corner for corner in wallCorners if allowedArea.contains(corner)]
        for wallCorner in wallCorners:
            self._graph.append({self._keyPoint: wallCorner,
                                self._keyEdgesTo: [],
                                self._keyDistance: inf,
                                self._keyPointPrevious: None,
                                self._keyVisited: False,
                                self._keyVertexType: self.VertexType.INSIDE})

        # add the goal point
        self._graph.append({self._keyPoint: goalPoint,
                            self._keyEdgesTo: [],
                            self._keyDistance: inf,
                            self._keyPointPrevious: None,
                            self._keyVisited: False,
                            self._keyVertexType: self.VertexType.END})

################################################################################

    def _makeEdges(self, walls):
        """

        """

        for pair in product(self._graph, repeat=2):
            graphEntry1 = pair[0]
            graphEntry2 = pair[1]
            if graphEntry1 is not graphEntry2:
                point1 = graphEntry1[self._keyPoint]
                point2 = graphEntry2[self._keyPoint]
                edge = QLineF(point1, point2)
                for wall in walls:
                    if PathFinding.intersects(wall, edge):
                        break
                else:
                    if not point2 in graphEntry1[self._keyEdgesTo]:
                        graphEntry1[self._keyEdgesTo].append(point2)
                    if not point1 in graphEntry2[self._keyEdgesTo]:
                        graphEntry2[self._keyEdgesTo].append(point1)

################################################################################

    def _minDistanceUnvisited(self):
        """

        """

        distanceMin = inf
        graphEntryMin = None
        for graphEntry in self._graph:
            distance = graphEntry[self._keyDistance]
            visited = graphEntry[self._keyVisited]
            if not visited and distance < distanceMin:
                distanceMin = distance
                graphEntryMin = graphEntry
        return graphEntryMin

################################################################################

    def _graphEntry(self, point):
        """

        """

        return [graphEntry for graphEntry in self._graph if graphEntry[self._keyPoint] == point][0]

################################################################################

    def _dijkstra(self):
        """

        """

        minDistGraphEntry = self._minDistanceUnvisited()
        while minDistGraphEntry is not None:
            point = minDistGraphEntry[self._keyPoint]
            neighbours = minDistGraphEntry[self._keyEdgesTo]
            for neighbour in neighbours:
                neighbourEntry = self._graphEntry(neighbour)
                neighbourVisited = neighbourEntry[self._keyVisited]
                if not neighbourVisited:
                    distanceCurrent = minDistGraphEntry[self._keyDistance]
                    distanceNext = distanceCurrent+QLineF(point, neighbour).length()
                    distanceNextCurrent = neighbourEntry[self._keyDistance]
                    if distanceNext < distanceNextCurrent:
                        neighbourEntry[self._keyDistance] = distanceNext
                        neighbourEntry[self._keyPointPrevious] = point
            minDistGraphEntry[self._keyVisited] = True
            minDistGraphEntry = self._minDistanceUnvisited()

################################################################################
