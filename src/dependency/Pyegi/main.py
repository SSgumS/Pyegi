from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QMovie
import os
import json
import sys

# dependency_dir = f"{os.getenv('APPDATA')}/Aegisub/automation/dependency/Pyegi/"
dependency_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
scriptPath = dependency_dir + 'PythonScripts/'
system_inputs = sys.argv

class Ui_SecondWindow(object):
    def setupUi(self, MainWindow, script_name):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(450, 200)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        script_settings = scriptPath + f'{script_name}/settings.json'
        f = open(script_settings)
        widgets = json.load(f)
        f.close()

        defW = 120 # default width
        defH = 25 # default height
        offX = 20 # offset in the X axis direction
        offY = 25 # offset in the Y axis direction
        Wfinal = 0 # final width of the window
        Hfinal = 0 # final height of the window
        lua_pyqt_conversion = {
            'label': 'QLabel',
            'edit': 'QLineEdit',
            'intedit': 'QSpinBox',
            'floatedit': 'QDoubleSpinBox',
            'textbox': 'QTextEdit',
            'dropdown': 'QComboBox',
            'checkbox': 'QCheckBox',
            'color': 'QPushButton',
            'coloralpha': 'QPushButton',
            'alpha': 'QLineEdit'
            }
        for widget in widgets['Controls']:
            name1 = widget['name']
            class1 = widget['class']
            exec(f'self.{name1} = QtWidgets.{lua_pyqt_conversion.get(class1, "QLabel")}(self.centralwidget)')
            Xtemp = offX + defW*widget["x"]
            Ytemp = offY + defH*widget["y"]
            Wtemp = defW*widget["width"]
            Htemp = defH*widget["height"]
            if Xtemp + Wtemp > Wfinal:
                Wfinal = Xtemp + Wtemp
            if Ytemp + Htemp > Hfinal:
                Hfinal = Ytemp + Htemp
            exec(f'self.{name1}.setGeometry(QtCore.QRect({Xtemp}, {Ytemp}, {Wtemp}, {Htemp}))')
            exec(f'self.{name1}.setObjectName(name1)')
        Wfinal += offX
        Hfinal += offY + 70
        MainWindow.resize(Wfinal, Hfinal)

        self.cancel_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_pushButton.setGeometry(QtCore.QRect(offX, Hfinal-offY-30, 80, 30))
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.cancel_pushButton.clicked.connect(QtCore.QCoreApplication.instance().quit)

        self.apply_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.apply_pushButton.setGeometry(QtCore.QRect(Wfinal-offX-80, Hfinal-offY-30, 80, 30))
        self.apply_pushButton.setObjectName("apply_pushButton")
        self.apply_pushButton.clicked.connect(lambda: self.apply_inputs(widgets, script_name, dependency_dir))

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 569, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow, widgets, script_name)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow, widgets, script_name):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", script_name))
        for widget in widgets['Controls']:
            name1 = widget['name']
            class1 = widget['class']
            text1 = ""
            if class1 == 'label':
                text1 = widget["label"]
            else:
                text2 = f'{widget["hint"]}'.encode(encoding='UTF-8')
                exec(f'self.{name1}.setToolTip(_translate("MainWindow", {text2}))')
            if class1 == 'floatedit' or class1 == 'intedit':
                try:
                    exec(f'self.{name1}.setMinimum({widget["min"]})')
                except:
                    pass
                try:
                    exec(f'self.{name1}.setMaximum({widget["max"]})')
                except:
                    pass
                if class1 == 'floatedit':
                    exec(f'self.{name1}.setSingleStep({widget["step"]})')
                exec(f'self.{name1}.setProperty("value", {widget["value"]})')
            if class1 == 'label':
                exec(f'self.{name1}.setText(_translate("MainWindow", "{text1}"))')
            if class1 == 'dropdown':
                exec(f'self.{name1}.addItems({widget["items"]})')
                exec(f'self.{name1}.setCurrentText(_translate("MainWindow", "{widget["value"]}"))')
        
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.apply_pushButton.setText(_translate("MainWindow", "Apply"))
    
    def apply_inputs(self, widgets, script_name, dependency_dir):
        for widget in widgets['Controls']:
            name1 = widget['name']
            class1 = widget['class']
            if class1 == 'floatedit':
                exec(f"widget['value'] = float(self.{name1}.text())")
            if class1 == 'dropdown':
                exec(f"widget['value'] = self.{name1}.currentText()")
        
        py_parameters_file_path = system_inputs[3]
        with open(py_parameters_file_path, 'w') as outfile:
            json.dump(widgets, outfile)
        
        os.system(f'""{dependency_dir}.venv/Scripts/python.exe" "{scriptPath}{script_name}/main.py" "{system_inputs[1]}" "{system_inputs[2]}" "{py_parameters_file_path}""')
        #MainWindow.close()
        sys.exit()

class Ui_MainWindow(object):
    def openWindow(self, script_name):
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_SecondWindow()
        self.ui.setupUi(self.window, script_name)
        self.window.show()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 81, 16))
        self.label.setObjectName("label")
        self.scriptNames_comboBox = QtWidgets.QComboBox(self.centralwidget, currentIndexChanged = lambda: self.preview())
        self.scriptNames_comboBox.setGeometry(QtCore.QRect(120, 20, 651, 22))
        self.scriptNames_comboBox.setObjectName("scriptNames_comboBox")
        self.preview_label = QtWidgets.QLabel(self.centralwidget)
        self.preview_label.setGeometry(QtCore.QRect(20, 60, 761, 431))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.preview_label.setFont(font)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setObjectName("preview_label")
        self.cancel_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancel_pushButton.setGeometry(QtCore.QRect(20, 510, 121, 31))
        self.cancel_pushButton.setObjectName("cancel_pushButton")
        self.cancel_pushButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self.settings_pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.settings_pushButton.setGeometry(QtCore.QRect(340, 510, 121, 31))
        self.settings_pushButton.setObjectName("settings_pushButton")
        self.next_pushButton = QtWidgets.QPushButton(self.centralwidget, clicked = lambda: self.openWindow(self.scriptNames_comboBox.currentText()))
        self.next_pushButton.setGeometry(QtCore.QRect(650, 510, 121, 31))
        self.next_pushButton.setObjectName("next_pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        first_item = True
        main_gif_path = ''
        for file in os.listdir(scriptPath):
            if os.path.isdir(scriptPath+file):
                self.scriptNames_comboBox.addItem(file)
                if first_item:
                    first_item = False
                    for file2 in os.listdir(scriptPath+file):
                        if file2.endswith(".gif"):
                            main_gif_path = scriptPath+file+'/'+file2
        
        if main_gif_path != '':
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Select Script"))
        self.preview_label.setText(_translate("MainWindow", "Preview"))
        self.cancel_pushButton.setText(_translate("MainWindow", "Cancel"))
        self.settings_pushButton.setText(_translate("MainWindow", "Settings"))
        self.next_pushButton.setText(_translate("MainWindow", "Next"))

    def preview(self):
        main_gif_path = ''
        scriptFolder = self.scriptNames_comboBox.currentText()
        for file in os.listdir(scriptPath+scriptFolder):
            if file.endswith(".gif"):
                main_gif_path = scriptPath+scriptFolder+'/'+file
        if main_gif_path != '':
            self.movie = QMovie(main_gif_path)
            self.preview_label.setMovie(self.movie)
            self.movie.start()
            self.movie.setPaused(False)
            #self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            #print(self.movie.CacheMode(0))
            #self.movie.loopCount()
        else:
            self.preview_label.setText('No Preview')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
