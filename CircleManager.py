from Circle import *


class CircleManager:
    head = None

    def __init__(self, workArea, width, height, mainW):
        self.workArea = workArea
        self.width = width
        self.height = height
        self.mainW = mainW
        if CircleManager.head is None:
            CircleManager.head = FileCircle([50, (height - 110) / 2], 110, mainW)
            CircleManager.head.addImg(workArea)
