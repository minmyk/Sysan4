from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QThread, Qt, QRect
from Solver import *
from sklearn.preprocessing import MinMaxScaler
from Animations import *


class PowersThread(QThread):
    def __init__(self, window):
        QThread.__init__(self)
        self.window = window

    def run(self):
        data = self.window.collect_data()
        numbers = [data[5], data[6], data[7]]
        kind = self.window.RcomboBox.currentText()
        is_multi = self.window.multi.isChecked()
        xd, yd = load_data(data[0], data[1], data[2], data[4], [data[5], data[6], data[7]])
        scale_x = MinMaxScaler()
        scale_y = MinMaxScaler()
        x = scale_x.fit_transform(xd)
        y = scale_y.fit_transform(yd)
        if is_multi:
            x = np.log(x + 2)
        self.window.poly.setEnabled(True)


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
        self.topRightGroupBox = QGroupBox("Polynoms")
        self.results = QLabel()
        self.originalPalette = QApplication.palette()
        self.topLayout = QHBoxLayout()
        self.powers_thread = PowersThread(self)
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setWindowTitle("Solver")
        self.setWindowIconText('Solver')
        self.showMaximized()
        self.inputs = []
        self.tabs = []
        self.create_top_left_group_box()
        self.create_top_mid_group_box()
        self.create_top_mid2_group_box()
        self.create_top_right_group_box()
        self.create_bottom_group_box()
        self.create_menu()
        #
        self.canvas1 = MyMplCanvas(self, width=9, height=3, dpi=100)
        self.canvas2 = MyMplCanvas(self, width=6, height=3, dpi=100)
        self.canvas3 = MyMplCanvas(self, width=6, height=3, dpi=100)
        self.canvas4 = MyMplCanvas(self, width=6, height=3, dpi=100)
        self.canvas5 = MyMplCanvas(self, width=6, height=3, dpi=100)
        #
        self.mainLayout = QGridLayout()

        self.mainLayout.addLayout(self.topLayout, 1, 0, 1, 4)
        self.mainLayout.addWidget(self.topLeftGroupBox, 0, 0)
        self.mainLayout.addWidget(self.topMidGroupBox, 0, 1)
        self.mainLayout.addWidget(self.topMid2GroupBox, 0, 3)
        self.mainLayout.addWidget(self.topRightGroupBox, 0, 2)
        # self.mainLayout.addWidget(self.topRightGroupBox, 0, 5)
        self.mainLayout.addWidget(self.bottomTabWidget, 2, 0, 1, 4)
        self.mainLayout.addWidget(self.canvas1, 0, 4)
        self.mainLayout.addWidget(self.canvas2, 1, 4, 2, 1)
        self.mainLayout.addWidget(self.canvas3, 4, 4)
        self.mainLayout.addWidget(self.canvas4, 4, 0, 1, 2)
        self.mainLayout.addWidget(self.canvas5, 4, 2, 1, 2)
        # self.mainLayout.addLayout(self.topLayout, 3, 0, 1, 4)
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
        self.resume = QPushButton("Resume")
        self.pause = QPushButton("Pause")
        self.reset = QPushButton("Reset")
        self.run = QPushButton("Execute")
        self.multi = QCheckBox("Multi")
        self.useStylePaletteCheckBox = QCheckBox("Light")

        self.useStylePaletteCheckBox.setChecked(True)
        self.multi.setChecked(False)
        self.reset.setFlat(True)
        self.resume.setFlat(True)
        self.pause.setFlat(True)
        self.run.setFlat(True)

        self.topLayout.addWidget(self.useStylePaletteCheckBox)
        self.topLayout.addWidget(self.multi)
        self.topLayout.addStretch(1)
        self.topLayout.addWidget(self.run)
        self.topLayout.addWidget(self.resume)
        self.topLayout.addWidget(self.pause)
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
        self.topLeftGroupBox.setFixedWidth(260)
        self.topLeftGroupBox.setLayout(layout)

    def create_top_right_group_box(self):

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

        #self.topRightGroupBox.setFixedHeight(190)
        self.topRightGroupBox.setFixedWidth(200)

        self.topRightGroupBox.setLayout(layout)

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

        #self.topMidGroupBox.setFixedHeight(190)
        self.topMidGroupBox.setFixedWidth(200)

        self.topMidGroupBox.setLayout(layout)

    def create_top_mid2_group_box(self):
        self.topMid2GroupBox = QGroupBox("Prognosis")
        self.speed_label = QLabel("Speed (meters per second)")
        self.speed = QSpinBox()
        self.per_label = QLabel("Period window")
        self.period = QSpinBox()
        self.pro_label = QLabel("Prognosis window")
        self.prognosis = QSpinBox()
        self.adeq_label = QLabel("Adequacy of measurements")
        self.adeq = QComboBox()
        self.adeq.addItems(["1", "2", "3", "4"])
        # self.inputs.append(self.MspinBox4)

        self.speed.setRange(1, 100)
        self.period.setRange(1, 100)
        self.prognosis.setRange(1, 100)

        layout = QGridLayout()

        layout.addWidget(self.speed, 0, 1)
        layout.addWidget(self.period, 2, 1)
        layout.addWidget(self.prognosis, 3, 1)
        layout.addWidget(self.adeq, 4, 1)
        layout.addWidget(self.speed_label, 0, 0)
        layout.addWidget(self.per_label, 2, 0)
        layout.addWidget(self.pro_label, 3, 0)
        layout.addWidget(self.adeq_label, 4, 0)
        # self.topMidGroupBox.setFixedHeight(190)
        self.topMid2GroupBox.setFixedWidth(260)

        self.topMid2GroupBox.setLayout(layout)

    def add_tabs(self, i):
        tab = QWidget()
        tab.setObjectName("tab_" + str(i + 1))
        image = QPixmap('data/fig' + str(i + 1) + '.png')
        image_label = QLabel(tab)
        image_label.setText("")
        image_label.setObjectName("image_label_" + str(i + 1))
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(image.scaled(755, 373))
        self.bottomTabWidget.addTab(tab, "Plot " + str(i + 1))
        self.tabs.append(tab)

    def remove_tabs(self):
        n = len(self.tabs)
        for i in range(1, n + 1):
            to_del = self.tabs[n - i]
            self.tabs.remove(to_del)
            to_del.deleteLater()

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
                                               "                            Status                            ",
                                               "              Danger level              ",
                                               "                Cause                "])
        self.Btable.resizeColumnsToContents()
        #self.Btable.
        self.bottomTabWidget = QTabWidget()
        #self.BtextEdit.setPlaceholderText("Here will be displayed the results after pressing 'Execute'\n")
        #self.BtextEdit.setReadOnly(True)

        self.tab1hbox.setContentsMargins(5, 5, 5, 5)
        self.tab1hbox.addWidget(self.Btable)

        self.Btab1.setLayout(self.tab1hbox)

        self.bottomTabWidget.addTab(self.Btab1, "Results")

    def clr(self):
        self.poly.setEnabled(True)
        self.Btable.clear()
        self.results.clear()
        self.remove_tabs()
        if self.powers_thread.isRunning():
            self.powers_thread.terminate()
            self.powers_thread.wait(10)

    def collect_data(self):
        values = [el.value() if type(el) != QLineEdit else el.text() for el in self.inputs]
        return values

    def execute(self):
        self.remove_tabs()
        self.Btable.clear()
        data = self.collect_data()
        numbers = [data[5], data[6], data[7]]
        kind = self.RcomboBox.currentText()
        is_multi = self.multi.isChecked()
        orders = data[-3:]
        xd, yd = load_data(data[0], data[1], data[2], data[4], [data[5], data[6], data[7]])
        scaler_x = MinMaxScaler()
        scaler_y = MinMaxScaler()
        y_scales = []
        for col in yd.columns:
            y_scales.append(MinMaxScaler())
            y_scales[-1].fit(yd[col].to_numpy().reshape(-1, 1))

        x = scaler_x.fit_transform(xd)
        y = scaler_y.fit_transform(yd)
        pol, min_poly = set_poly(kind, orders, numbers, x, is_multi)
        if is_multi:
            y = np.log(y + min_poly)
        self.Btable.clear()
        self.Btable.append("Polynoms: " + str(kind) + "\n")
        for t in range(data[4]):
            variables = set_vars(orders, numbers, x)
            lamb = fit(pol, y[:, t])
            psy = set_psy(lamb, numbers, orders, pol, is_multi, min_poly)
            a = fit(psy, y[:, t])
            fs = set_f(a, numbers, psy, is_multi, min_poly)

            visualize(y[:, t], pol, lamb, t, kind, y_scales[t], self.normalize.isChecked(), is_multi, min_poly,
                      error(y[:, t], pol, lamb, is_multi))

            self.add_tabs(t)

        f = open('data/' + data[3] + ".txt", "w+")
        f.write('\nResult: \n')
        f.write(self.Btable.toPlainText())

    def calculate_powers(self):
        self.poly.setEnabled(False)
        self.results.setText('Computing...')
        self.powers_thread.start()
