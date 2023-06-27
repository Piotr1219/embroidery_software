
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSlider

from main_design_ui import Ui_MainWindow
from image_processing import *
import numpy as np


class MainWindowDesign(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.image_original = None
        self.temp_image = None
        self.last_operation = 0

    def add_actions(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.scene.installEventFilter(self)
        self.actionOtw_rz.triggered.connect(self.getfiles)
        self.actionZapisz.triggered.connect(self.file_save)
        self.pushButton_3.clicked.connect(self.greyscale)
        self.pushButton_4.clicked.connect(self.reset)
        self.pushButton_2.clicked.connect(self.start_machine)
        self.pushButton_color.clicked.connect(lambda: self.reduce_colors())
        self.pushButton_background.clicked.connect(self.remove_background)
        self.pushButton_sketch.clicked.connect(lambda: self.to_sketch())
        self.horizontalSlider.valueChanged.connect(lambda: self.update_label(self.horizontalSlider.value()))
        self.horizontalSlider_2.valueChanged.connect(lambda: self.update_label_2(self.horizontalSlider_2.value()))
        self.horizontalSlider.sliderReleased.connect(lambda: self.to_sketch(self.horizontalSlider.value()))
        self.horizontalSlider_2.sliderReleased.connect(lambda: self.reduce_colors(self.horizontalSlider_2.value()))

    def getfiles(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilters(["*.png", "*.jpg", "*.jpeg"])
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            print(filenames[0])
            f = open(filenames[0], 'r')
            with f:
                self.image = open_image(filenames[0])
                self.image_original = self.image
                self.update_image()

    def file_save(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.png)", options=options)
        if fileName:
            save_image(self.image, fileName)

    def update_image(self):
        self.scene.clear()
        img = image_resize(self.image, self.graphicsView.width()-2, self.graphicsView.height()-2)
        height, width = img.shape[:2]
        print('hq', height, width)
        widthStep = width * 3
        image_disp = QtGui.QImage(
            img.data, width, height, widthStep, QtGui.QImage.Format_BGR888
        )
        pixMap = QtGui.QPixmap.fromImage(image_disp)
        self.pixmap_item = self.scene.addPixmap(pixMap)

    def greyscale(self):
        self.last_operation = 1
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        self.update_image()

    def reset(self):
        self.last_operation = 0
        self.image = self.image_original
        self.label.setVisible(False)
        self.horizontalSlider.setVisible(False)
        self.temp_image = None
        self.update_image()

    def reduce_colors(self, k=6):
        if self.last_operation != 3:
            self.temp_image = self.image
        self.last_operation = 3
        self.label.setVisible(False)
        self.horizontalSlider.setVisible(False)
        if self.temp_image is None:
            self.image = self.image_original
        else:
            self.image = self.temp_image
        self.horizontalSlider_2.setVisible(True)
        self.horizontalSlider_2.setMinimum(3)
        self.horizontalSlider_2.setMaximum(15)
        self.horizontalSlider_2.setValue(k)
        self.horizontalSlider.setUpdatesEnabled(True)
        self.label_2.setVisible(True)
        self.label_2.setText(f"{self.horizontalSlider_2.value()}")
        self.label.update()
        self.horizontalSlider.update()
        pixel_vals = self.image.reshape((-1, 3))
        pixel_vals = np.float32(pixel_vals)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.85)
        print("Start")
        retval, labels, centers = cv2.kmeans(pixel_vals, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        print("Koniec")

        # convert data into 8-bit values
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]

        # reshape data into the original image dimensions
        self.image = segmented_data.reshape((self.image.shape))
        self.update_image()

    def to_sketch(self, size=21):
        if self.last_operation != 4:
            self.temp_image = self.image
        self.last_operation = 4
        self.label_2.setVisible(False)
        self.horizontalSlider_2.setVisible(False)
        if self.temp_image is None:
            self.image = self.image_original
        else:
            self.image = self.temp_image
        self.horizontalSlider.setVisible(True)
        self.horizontalSlider.setMinimum(3)
        self.horizontalSlider.setMaximum(55)
        self.horizontalSlider.setValue(size)
        self.horizontalSlider.setTickPosition(QSlider.TicksBothSides)
        self.horizontalSlider.setTickInterval(2)
        self.horizontalSlider.setSingleStep(2)
        self.horizontalSlider.setUpdatesEnabled(True)
        self.label.setVisible(True)
        self.label.setText(f"{self.horizontalSlider.value()}")
        self.label.update()
        self.horizontalSlider.update()
        grey_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        invert = cv2.bitwise_not(grey_img)
        if size % 2 == 0:
            self.horizontalSlider.setValue(size-1)
            size = size-1
        blur = cv2.GaussianBlur(invert, (size, size), 0)
        invertedblur = cv2.bitwise_not(blur)
        sketch = cv2.divide(grey_img, invertedblur, scale=256.0)
        cv2.imwrite("./sketch.png", sketch)  # converted image is saved as mentioned name
        self.image = cv2.imread("./sketch.png")
        self.update_image()

    def update_label(self, val):
        self.label.setText(f"{val}")

    def update_label_2(self, val):
        self.label_2.setText(f"{val}")

    def remove_background(self):
        self.last_operation = 2
        from rembg import remove
        # self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image = remove(self.image)
        cv2.imwrite("./test.png", self.image)
        self.image = cv2.imread("./test.png")
        self.update_image()

    def start_machine(self):
        dlg = CustomDialog()
        if dlg.exec():
            print("Starting machine!")
        else:
            print("Start canceled!")


class CustomDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Confirm!")

        QBtn = QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Are you sure you want to start machine?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)