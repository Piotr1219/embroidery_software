
from PyQt5 import QtCore, QtGui, QtWidgets
from main_design_ui import Ui_MainWindow
from image_processing import *


class MainWindowDesign(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.image = None
        self.image_original = None

    def add_actions(self):
        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.scene.installEventFilter(self)
        self.actionOtw_rz.triggered.connect(self.getfiles)
        self.actionZapisz.triggered.connect(self.file_save)
        self.pushButton_3.clicked.connect(self.greyscale)
        self.pushButton_4.clicked.connect(self.reset)
        self.pushButton_2.clicked.connect(self.start_machine)

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
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)
        self.update_image()

    def reset(self):
        self.image = self.image_original
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