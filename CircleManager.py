from Circle import *


class CircleManager:

    head = None

    def __init__(self, workArea, width, height, mainW):
        self.workArea = workArea
        self.width = width
        self.height = height
        if CircleManager.head is None:
            CircleManager.head = FileCircle([50, (height - 90) / 2], 90, mainW)
            CircleManager.head.addImg(workArea)

