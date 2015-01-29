#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

try:
    from PySide import QtCore
    from PySide import QtWidgets
except:
    from PyQt5.QtCore import pyqtSlot as Slot
    from PyQt5 import QtCore
    from PyQt5 import QtWidgets

try:

    import cv2
    import sys
    import numpy


    from PyQt5.QtQuick import QQuickPaintedItem
    from PyQt5.QtCore import (pyqtProperty, pyqtSignal, Q_CLASSINFO, QCoreApplication, QDate, QObject, QTime, QUrl)
    from PyQt5.QtCore import QTimerEvent
    from PyQt5.QtCore import QTimer

    from PyQt5.QtCore import qDebug
    from PyQt5.QtGui import QPainter
    from PyQt5.QtWidgets import QStyleOptionGraphicsItem
    from PyQt5.QtWidgets import QWidget
    from PyQt5.QtWidgets import QGraphicsItem

    from PyQt5.QtQuick import QQuickItem
    from PyQt5.QtCore import pyqtProperty

    from PyQt5.QtCore import Qt
    from PyQt5.QtCore import QSize
    from PyQt5.QtCore import QPoint
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QColor
    from PyQt5.QtGui import QImage
except Exception as e:
    print("Error in importing modules ",e)



def gray2qimage(gray):
        """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
        colormap.  The first dimension represents the vertical image axis.

        ATTENTION: This QImage carries an attribute `ndimage` with a
        reference to the underlying numpy array that holds the data. On
        Windows, the conversion into a QPixmap does not copy the data, so
        that you have to take care that the QImage does not get garbage
        collected (otherwise PyQt will throw away the wrapper, effectively
        freeing the underlying memory - boom!)."""
        if len(gray.shape) != 2:
                raise ValueError("gray2QImage can only convert 2D arrays")

        gray = numpy.require(gray, numpy.uint8, 'C')

        h, w = gray.shape

        result = QImage(gray.data, w, h, QImage.Format_Indexed8)
        result.ndarray = gray
        for i in range(256):
                result.setColor(i, QColor(i, i, i).rgb())
        return result

def rgb2qimage(rgb):
        """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
        have three dimensions with the vertical, horizontal and RGB image axes.

        ATTENTION: This QImage carries an attribute `ndimage` with a
        reference to the underlying numpy array that holds the data. On
        Windows, the conversion into a QPixmap does not copy the data, so
        that you have to take care that the QImage does not get garbage
        collected (otherwise PyQt will throw away the wrapper, effectively
        freeing the underlying memory - boom!)."""
        if len(rgb.shape) != 3:
                raise ValueError("rgb2QImage can only convert 3D arrays")
        if rgb.shape[2] not in (3, 4):
                raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

        #h, w, channels = rgb.shape



        ## Qt expects 32bit BGRA data for color images:
        #bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
        #bgra[...,0] = rgb[...,2]
        #bgra[...,1] = rgb[...,1]
        #bgra[...,2] = rgb[...,0]
        #if rgb.shape[2] == 3:
                #bgra[...,3].fill(255)
                #fmt = QImage.Format_RGB32
        #else:
                #bgra[...,3] = rgb[...,3]
                #fmt = QImage.Format_ARGB32

        #result = QImage(bgra.data, w, h, fmt)
        #result.ndarray = bgra
        #return result
        height, width, bytesPerComponent = rgb.shape
        bytesPerLine = bytesPerComponent * width
        result  = QImage(rgb, width, height, bytesPerLine, QImage.Format_RGB888)
        return result.rgbSwapped()






class CustomOpenCVItem(QQuickPaintedItem):



    colorChanged = pyqtSignal()
    readyChanged = pyqtSignal(int)
    readySignal = pyqtSignal()
    #timerEvent

    def __init__(self, parent = None):
        super(CustomOpenCVItem, self).__init__(parent)
#        self.setFlag(QQuickItem.ItemHasContents, False)
#        print("What the fuck")
#        self._color = Qt.red

#        timer = QTimer(self)
#        timer.timeout.connect(self.update)
#        timer.start(100)
#        self.ready = 0
#        self.startTimer(100)


        self._capture = cv2.VideoCapture(0)
        # Take one frame to query height
        #frame = cv.QueryFrame(self._capture)
        ret, frame = self._capture.read()
        height, width, depth = frame.shape

        self.facialRecognition = False


        cascPath = 'face_cascade.xml'
        self.faceCascade = cv2.CascadeClassifier(cascPath)

        self.mOutH = 0 #image real rendering sizes
        self.mOutW = 0 #image real rendering sizes
        self.mImgratio = 4.0/3.0 # Default image ratio

        self.mPosX = 0 # top/left image coordinates, allow to render image in the center of the widget
        self.mPosY = 0 # top/left image coordinates, allow to render image in the center of the widget

        self._frame = None
        self._image = self._build_image(frame)
        # Paint every 16 ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.queryFrame)
        self._timer.start(16)



    def create_blank(self,width, height, rgb_color=(0, 0, 0)):
       """Create new image(numpy array) filled with certain color in RGB"""
       # Create black blank image
       image = numpy.zeros((height, width, 3), numpy.uint8)

       # Since OpenCV uses BGR, convert the color first
       color = tuple(reversed(rgb_color))
       # Fill image with color
       image[:] = color

       return image

    def _build_image(self, array):
       if numpy.ndim(array) == 2:
           return gray2qimage(array)
       elif numpy.ndim(array) == 3:
           return rgb2qimage(array)
       raise ValueError("can only convert 2D or 3D arrays")



#    def timerEvent(self, timer):
#        if self.ready >= 100:
#            self.killTimer(timer.timerId())
##            qDebug(self.readySignal)<<"readySignal"
#            print("Ready Signal called")
#            self.readySignal.emit()
#        else:
#            self.ready += 1
#            print('yo ',self.ready)
##            qDebug(self.readyChanged)
#            self.readyChanged.emit(self.ready)

#    def getReadyNumber(self):
#        return self.ready

##    @pyqtProperty("QColor", fget = color, fset = setColor, notify = colorChanged)
#    def getColor(self):
#        return self._color

##    @color.setter
#    def setColor(self,color):
#        if self._color != color:
#            self._color = color
#            self.colorChanged.emit()
#            self.update()



    def paint(self, painter):
        painter.drawImage(QPoint(self.mPosX, self.mPosY), self._image) #.scaled(self.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
#        painter.fillRect(self.contentsBoundingRect(), self._color);
        #print("damn")

    def queryFrame(self):
        #frame = cv.QueryFrame(self._capture)
        ret, frame = self._capture.read()
        #: It Works Yeah !!!!!!!!!!!!!

        if self.facialRecognition == True:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        self._image = self._build_image(frame)
        self.update()


    #THis fucking works yeah !!!!!!
#    color = pyqtProperty("QColor", fget=getColor, fset= setColor, notify=colorChanged)
#    value = pyqtProperty(int, fget=getReadyNumber, notify=readyChanged)

