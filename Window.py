from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from Animations import *
from functools import reduce


class UI(QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)

        self.Lline3 = QLineEdit()
        self.Lline2 = QLineEdit()
        self.Lline1 = QLineEdit()
        self.Llabel4 = QLabel("X source file:")
        self.Llabel3 = QLabel("To file:")
        self.Llabel2 = QLabel("Y source file:")
        self.Llabel1 = QLabel("Sample size:")
        self.LspinBox = QSpinBox()
        self.topLeftGroupBox = QGroupBox("Data")

        self.Mlabel4 = QLabel("X3:")
        self.Mlabel3 = QLabel("X2:")
        self.Mlabel2 = QLabel("X1:")
        self.Mlabel1 = QLabel("Y:")
        self.MspinBox4 = QSpinBox()
        self.MspinBox3 = QSpinBox()
        self.MspinBox2 = QSpinBox()
        self.MspinBox1 = QSpinBox()
        self.topMidGroupBox = QGroupBox("Dimensions")

        self.Rlabel6 = QLabel("X3 Power:")
        self.Rlabel5 = QLabel("X2 Power:")
        self.Rlabel4 = QLabel("X1 Power:")
        self.Rlabel1 = QLabel("Polynoms:")
        self.RspinBox4 = QSpinBox()
        self.RspinBox3 = QSpinBox()
        self.RspinBox2 = QSpinBox()
        self.RcomboBox = QComboBox()
        self.topMid2GroupBox = QGroupBox("Polynoms")

        self.results = QLabel()
        self.originalPalette = QApplication.palette()
        self.topLayout = QHBoxLayout()
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setWindowTitle("Solver")
        self.setWindowIconText('Solver')
        self.showMaximized()
        self.inputs = []
        self.tabs = []
        self.create_top_left_group_box()
        self.create_top_mid_group_box()
        self.create_top_right_group_box()
        self.create_top_mid2_group_box()
        self.create_bottom_group_box()
        self.create_menu()

        self.canvas1 = Graph(self, width=9, height=3, dpi=100, title='Y1')
        self.canvas2 = Graph(self, width=6, height=3, dpi=100, title='Y2')
        self.canvas3 = Graph(self, width=6, height=3, dpi=100, title='Y3')
        self.canvas4 = Graph(self, width=6, height=3, dpi=100, title='Margin of tolerable risk')
        self.canvas5 = Graph(self, width=6, height=3, dpi=100)
        self.graphs = [self.canvas1, self.canvas2, self.canvas3, self.canvas4, self.canvas5]

        self.mainLayout = QGridLayout()

        self.mainLayout.addLayout(self.topLayout, 1, 0, 1, 4)
        self.mainLayout.addWidget(self.topLeftGroupBox, 0, 0)
        self.mainLayout.addWidget(self.topMidGroupBox, 0, 1)
        self.mainLayout.addWidget(self.topMid2GroupBox, 0, 2)
        self.mainLayout.addWidget(self.topRightGroupBox, 0, 3)
        self.mainLayout.addWidget(self.bottomTabWidget, 2, 0, 1, 4)
        self.mainLayout.addWidget(self.canvas1, 0, 4)
        self.mainLayout.addWidget(self.canvas2, 1, 4, 2, 1)
        self.mainLayout.addWidget(self.canvas3, 4, 4)
        self.mainLayout.addWidget(self.canvas4, 4, 0, 1, 2)
        self.mainLayout.addWidget(self.canvas5, 4, 2, 1, 2)
        self.setLayout(self.mainLayout)

        self.change_palette()

    def change_palette(self):
        dark_palette = QPalette()

        QApplication.setStyle(QStyleFactory.create("Fusion"))

        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))

        if self.useStylePaletteCheckBox.isChecked():
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(dark_palette)

    def create_menu(self):
        self.reset = QPushButton("Reset")
        self.run = QPushButton("Execute")
        self.multi = QCheckBox("Multi")
        self.useStylePaletteCheckBox = QCheckBox("Light")

        self.useStylePaletteCheckBox.setChecked(True)
        self.multi.setChecked(True)
        self.reset.setFlat(True)
        self.run.setFlat(True)

        self.topLayout.addWidget(self.useStylePaletteCheckBox)
        self.topLayout.addWidget(self.multi)
        self.topLayout.addStretch(1)
        self.topLayout.addWidget(self.run)
        self.topLayout.addWidget(self.reset)

    def create_top_left_group_box(self):

        self.LspinBox.setRange(0, 10000)
        self.inputs.append(self.LspinBox)

        self.Lline1.setPlaceholderText(' *.txt')
        self.inputs.append(self.Lline1)

        self.Lline2.setPlaceholderText(' *.txt')
        self.inputs.append(self.Lline2)

        self.Lline3.setPlaceholderText(' *.txt')
        self.inputs.append(self.Lline3)

        layout = QGridLayout()

        layout.addWidget(self.Llabel1, 0, 0)
        layout.addWidget(self.LspinBox, 0, 1)
        layout.addWidget(self.Llabel2, 1, 0)
        layout.addWidget(self.Llabel3, 3, 0)
        layout.addWidget(self.Llabel4, 2, 0)
        layout.addWidget(self.Lline1, 1, 1)
        layout.addWidget(self.Lline2, 2, 1)
        layout.addWidget(self.Lline3, 3, 1)

        # self.topLeftGroupBox.setFixedHeight(190)
        self.topLeftGroupBox.setFixedWidth(235)
        self.topLeftGroupBox.setLayout(layout)

    def create_top_mid_group_box(self):

        self.inputs.append(self.MspinBox1)

        self.inputs.append(self.MspinBox2)

        self.inputs.append(self.MspinBox3)

        self.inputs.append(self.MspinBox4)

        layout = QGridLayout()

        layout.addWidget(self.MspinBox1, 0, 1)
        layout.addWidget(self.MspinBox2, 1, 1)
        layout.addWidget(self.MspinBox3, 2, 1)
        layout.addWidget(self.MspinBox4, 3, 1)
        layout.addWidget(self.Mlabel1, 0, 0)
        layout.addWidget(self.Mlabel2, 1, 0)
        layout.addWidget(self.Mlabel3, 2, 0)
        layout.addWidget(self.Mlabel4, 3, 0)

        # self.topMidGroupBox.setFixedHeight(190)
        self.topMidGroupBox.setFixedWidth(200)

        self.topMidGroupBox.setLayout(layout)

    def create_top_mid2_group_box(self):

        self.RcomboBox.addItems(["Chebyshev", "Hermite", "Legendre"])

        self.RspinBox2.setRange(0, 1000)
        self.inputs.append(self.RspinBox2)

        self.RspinBox3.setRange(0, 1000)
        self.inputs.append(self.RspinBox3)

        self.RspinBox4.setRange(0, 1000)
        self.inputs.append(self.RspinBox4)

        layout = QGridLayout()

        layout.addWidget(self.RcomboBox, 0, 1)
        layout.addWidget(self.RspinBox2, 2, 1)
        layout.addWidget(self.RspinBox3, 3, 1)
        layout.addWidget(self.RspinBox4, 4, 1)

        layout.addWidget(self.Rlabel1, 0, 0)
        layout.addWidget(self.Rlabel4, 2, 0)
        layout.addWidget(self.Rlabel5, 3, 0)
        layout.addWidget(self.Rlabel6, 4, 0)

        # self.topRightGroupBox.setFixedHeight(190)
        self.topMid2GroupBox.setFixedWidth(200)

        self.topMid2GroupBox.setLayout(layout)

    def create_top_right_group_box(self):
        self.topRightGroupBox = QGroupBox("Prognosis")
        self.speed_label = QLabel("Display speed")
        self.speed = QSpinBox()
        self.per_label = QLabel("Period window")
        self.period = QSpinBox()
        self.pro_label = QLabel("Prognosis window")
        self.prognosis = QSpinBox()
        self.resume = QPushButton("Resume")
        self.pause = QPushButton("Pause")

        self.resume.setFlat(True)
        self.pause.setFlat(True)
        self.speed.setRange(1, 100)
        self.period.setRange(1, 100)
        self.prognosis.setRange(1, 100)

        layout = QGridLayout()

        layout.addWidget(self.speed, 0, 1)
        layout.addWidget(self.period, 2, 1)
        layout.addWidget(self.prognosis, 3, 1)
        layout.addWidget(self.speed_label, 0, 0)
        layout.addWidget(self.per_label, 2, 0)
        layout.addWidget(self.pro_label, 3, 0)
        layout.addWidget(self.resume, 4, 0)
        layout.addWidget(self.pause, 4, 1)
        # self.topMidGroupBox.setFixedHeight(190)
        self.topRightGroupBox.setFixedWidth(235)

        self.topRightGroupBox.setLayout(layout)

    def create_bottom_group_box(self):
        self.tab1hbox = QHBoxLayout()
        self.Btab1 = QWidget()
        self.Btable = QTableWidget(self.Btab1)
        self.Btable.setColumnCount(7)
        self.Btable.setRowCount(0)
        self.Btable.setHorizontalHeaderLabels(["     Time     ",
                                               "           У1           ",
                                               "           У2           ",
                                               "           У3           ",
                                               "                      Status                      ",
                                               "     Danger level      ",
                                               "               Cause               "])
        self.Btable.resizeColumnsToContents()
        self.Btable.horizontalHeader().setStretchLastSection(True)
        self.Btable.insertRow(0)
        for i in range(7):
            self.Btable.setItem(0, i, QTableWidgetItem(' '))
        self.bottomTabWidget = QTabWidget()

        self.tab1hbox.setContentsMargins(5, 5, 5, 5)
        self.tab1hbox.addWidget(self.Btable)

        self.Btab1.setLayout(self.tab1hbox)

        self.bottomTabWidget.addTab(self.Btab1, "Parameters")

    def clr(self):
        self.Btable.clear()
        for i in range(4):
            f = open("data/program_data_h" + str(i) + ".txt", 'w+')
            f.write('')
            f.close()
        for i in range(3):
            f = open("data/program_data_r" + str(i) + ".txt", 'w+')
            f.write('')
            f.close()
        self.Btable.setColumnCount(7)
        self.Btable.setRowCount(0)
        self.Btable.setHorizontalHeaderLabels(["     Time     ",
                                               "           У1           ",
                                               "           У2           ",
                                               "           У3           ",
                                               "                      Status                      ",
                                               "     Danger level      ",
                                               "               Cause               "])
        self.Btable.resizeColumnsToContents()
        self.Btable.horizontalHeader().setStretchLastSection(True)
        self.Btable.insertRow(0)
        for i in range(7):
            self.Btable.setItem(0, i, QTableWidgetItem(' '))

    def collect_data(self):
        values = [el.value() if type(el) != QLineEdit else el.text() for el in self.inputs]
        return values

    def execute(self):

        """
        window_forecast = 5  # self.prognosis.value()
        window_build = 5  # self.period.value()
        speed = 5  # self.speed.value()
        kind = self.RcomboBox.currentText()
        parameters = self.collect_data()
        numbers = [3, 3, 3]  # parameters[5:-3]
        orders = [4, 5, 6]  # parameters[-3:]
        file_y = 'y'  # parameters[1]
        file_x = 'x'  # parameters[2]
        parameters[0] = 1000
        parameters[4] = 3
        
        """  # for testing

        window_forecast = self.prognosis.value()
        window_build = self.period.value()
        speed = self.speed.value()
        kind = self.RcomboBox.currentText()
        parameters = self.collect_data()
        numbers = parameters[5:-3]
        orders = parameters[-3:]
        file_y = parameters[1]
        file_x = parameters[2]
        is_multi = self.multi.isChecked()
        data, normalizer = normalize(load_data(parameters[0], file_x, file_y), is_multi)
        x, y = data
        arr = [[[11.7, 1e10], [11.5, 1e10]], [[4.1, 1e10], [0.5, 1e10]], [[11.85, 1e10], [11.80, 1e10]]]
        sensors = indicator(y.T, window_forecast)
        sensors = list(map(lambda k: [sensors[k]] * window_forecast, range(len(sensors))))
        sensors = list(reduce(lambda a, b: a + b, sensors))

        self.Btable.setColumnCount(7)
        self.Btable.setRowCount(0)
        self.Btable.setHorizontalHeaderLabels(["     Time     ",
                                               "           У1           ",
                                               "           У2           ",
                                               "           У3           ",
                                               "                      Status                      ",
                                               "     Danger level      ",
                                               "               Cause               "])
        self.Btable.resizeColumnsToContents()
        self.Btable.horizontalHeader().setStretchLastSection(True)
        self.Btable.insertRow(0)
        for i in range(7):
            self.Btable.setItem(0, i, QTableWidgetItem(' '))
        y1, y2 = 0, 0
        animations = [0] * (parameters[4] + 2)
        for i in range(parameters[4] + 1):
            if i < 3:
                y1, y2 = create_animation(x, y[:, i], [orders, numbers], window_build, window_forecast, kind)
                y1, y2 = denormalize((y1, y2), normalizer[i])
                y2 = y2 + np.random.normal(0, 0.01 * (max(y2) - min(y2)), len(y2))
                animations[i] = Animation(y1, y2, window_forecast, True, i, speed, arr[i], self.pause, self.resume,
                                          self.Btable, parameters[4], normalizer[i], False, sensors, self.graphs[i])
            else:
                animations[i] = Animation(y1, y2, window_forecast, True, 3, speed, [[-1, 400]] * 4, self.pause,
                                          self.resume, self.Btable, parameters[4], normalizer[2], True, sensors,
                                          self.graphs[i])
            self.pause.clicked.connect(animations[i].stop_animation)
            self.resume.clicked.connect(animations[i].start_animation)
