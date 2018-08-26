__author__ = 'Tofu Gang'

from PyQt5.QtCore import QObject, pyqtSignal as Signal
from src.dot import Dot
from random import uniform

################################################################################

class Population(QObject):
    POPULATION_SIZE = 100
    VECTORS_COUNT = 400
    updateCounters = Signal()

################################################################################

    def __init__(self, scene):
        """

        """

        super().__init__()
        self._scene = scene
        self._finishedCounter = 0
        self._generationCount = 0
        self._wonCount = 0
        self._exhaustedCount = 0
        self._deadCount = 0
        self._population = []
        self._maxVectorsCount = self.VECTORS_COUNT

        for _ in range(self.POPULATION_SIZE):
            dot = Dot(self)
            dot.setPos(self._scene.START_POINT)
            self._scene.addItem(dot)
            self._population.append(dot)
            dot.brain.finished.connect(self._dotFinished)

################################################################################

    @property
    def maxVectorsCount(self):
        """

        """

        return self._maxVectorsCount

################################################################################

    @property
    def generationCount(self):
        """

        """

        return self._generationCount

################################################################################

    @property
    def wonCount(self):
        """

        """

        return self._wonCount

################################################################################

    @property
    def exhaustedCount(self):
        """

        """

        return self._exhaustedCount

################################################################################

    @property
    def deadCount(self):
        """

        """

        return self._deadCount

################################################################################

    def start(self):
        """

        """

        [dot.start() for dot in self._population]

################################################################################

    def _dotFinished(self):
        """

        """

        self._finishedCounter += 1
        dotsWon = [dot for dot in self._population if dot.state is dot.State.WON]
        self._wonCount = len(dotsWon)
        if len(dotsWon) > 0:
            self._maxVectorsCount = min(dot.usedVectorsCount for dot in dotsWon)
        self._exhaustedCount = len([dot for dot in self._population if dot.state is dot.State.EXHAUSTED])
        self._deadCount = len([dot for dot in self._population if dot.state is dot.State.DEAD])

        if self._finishedCounter == len(self._population):
            self._nextGeneration()
            self.start()

        self.updateCounters.emit()

################################################################################

    def _nextGeneration(self):
        """

        """

        newGeneration = []
        self._generationCount += 1
        self._finishedCounter = 0
        self._wonCount = 0
        self._exhaustedCount = 0
        self._deadCount = 0

        # get the champion
        champion = sorted([dot for dot in self._population], key=lambda dot: dot.fitnessFunction)[-1]
        child = champion.child
        child.dotType = child.Type.CHAMPION
        child.setPos(self._scene.START_POINT)
        self._scene.addItem(child)
        newGeneration.append(child)
        child.brain.finished.connect(self._dotFinished)

        # population size - 1 because of the champion already being in the next generation
        for i in range(self.POPULATION_SIZE-1):
            parent = self._getParent()
            child = parent.child
            child.mutate()
            child.setPos(self._scene.START_POINT)
            self._scene.addItem(child)
            newGeneration.append(child)
            child.brain.finished.connect(self._dotFinished)

        [self._scene.removeItem(dot) for dot in self._population]
        self._population.clear()
        del self._population
        self._population = newGeneration

################################################################################

    def _getParent(self):
        """

        """

        rand = uniform(0, sum(dot.fitnessFunction for dot in self._population))
        partialFitnessSum = 0

        for dot in self._population:
            partialFitnessSum += dot.fitnessFunction
            if partialFitnessSum > rand:
                return dot

################################################################################
