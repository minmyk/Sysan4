from matplotlib import animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QSpinBox, QTableWidget, QLabel, QApplication, QLineEdit, QDialog, QGroupBox, \
    QHBoxLayout, QComboBox, QGridLayout, QStyleFactory, QCheckBox, QPushButton, QWidget, QTableWidgetItem, QTabWidget
from PyQt5.QtGui import QPalette, QColor, QIcon
import sys
from PyQt5.QtCore import Qt
from functools import reduce
import numpy as np
from itertools import combinations
import copy
from scipy.stats import spearmanr
np.set_printoptions(linewidth=np.inf)


class Graph(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, title=None):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_title(title)
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def compute_initial_figure(self):
        pass


class Animation:
    def __init__(self, y_init, y_real, window, autoplay, filenumber, anim_speed, danger_levels, stop_func, start_func,
                 result_table, num_of_y, normalizer, read_risks, sensors, graph, ind):
        self.playing = autoplay
        self.canvas = graph
        self.sensors = sensors
        self.normalizer = normalizer
        self.num_of_y = num_of_y
        self.read_risks = read_risks
        self.table = result_table
        self.stop_func = stop_func
        self.start_func = start_func
        self.window = window
        self.levels = danger_levels
        self.x = np.arange(len(y_init))
        self.y_fcast = y_init
        self.x1 = np.arange(len(y_real))
        self.y_real = y_real + np.random.normal(0, 0.03, len(y_real))
        self.min_val = np.ones((len(y_real))) * danger_levels[0][0]
        self.max_val = np.ones((len(y_real))) * danger_levels[1][0]
        self.correl = np.zeros((len(y_real)))
        self.filenumber = filenumber
        self.ind = ind
        risks = abs(self.y_real[1:] - self.y_real[:-1])
        differences = np.vstack((abs(self.y_real - self.min_val), abs(self.y_real - self.max_val)))
        differences = np.array(list(map(lambda a: min(differences[0][a], differences[1][a]),
                                        range(differences.shape[1]))))
        risk_maxs = np.array(list(map(lambda a: max(risks[
                                                    max(0, a - window):max(len(self.y_real), a + int(window / 2))
                                                    ]), range(len(risks)))))
        self.risk_management = (differences[1:] / risk_maxs) * self.window
        self.risk_exist = np.zeros(len(self.risk_management))
        if not read_risks:
            self.canvas.axes.set_ylim([min(self.y_real) * 0.9, max(self.y_real) * 1.1])
            for j in range(int(window / 2) + 5, len(self.risk_management) - int(window / 2)):
                if (get_variance(self.risk_management[j:j + int(window / 2)]) > 1.5 * get_variance(
                        self.risk_management[j - window:j]) or
                    abs(get_mean(self.risk_management[j:j + int(window / 2)]) - get_mean(
                        self.risk_management[j - window:j])) > 2 * get_variance(
                            self.risk_management[j - window:j]) ** 0.5) or (
                        self.filenumber == 1 and self.y_real[j] < self.min_val[0]):
                    if self.risk_exist[j - 1] == min(self.y_real) or self.risk_exist[j - 1] == 0:
                        self.risk_exist[j] = max(self.y_real)
                    else:
                        self.risk_exist[j] = min(self.y_real) + 0.01
            file = open("data/program_data_r" + str(filenumber) + ".txt", 'w+')
            string = str(list(self.risk_management)).replace('[', '')
            string = string.replace(']', '')
            string = string.replace(',', '')
            file.write(string)
            file.close()

        else:
            self.risk_management = np.arange(len(risk_maxs))
            read_risks = np.zeros((self.num_of_y, len(self.risk_management)))
            for i in range(self.num_of_y):
                file = open("data/program_data_r" + str(i) + ".txt", 'r')
                readl = file.readline()
                read_risks[i] = np.array(list(map(lambda z: float(z), readl.strip().split())))
                file.close()
            for i in range(len(self.risk_management)):
                self.risk_management[i] = min(read_risks[:, i])
            self.risk_management = ((self.risk_management - min(self.risk_management)) / (
                        max(self.risk_management) - min(self.risk_management)))
            if self.ind == 4:
                self.risk_management *= np.random.normal(1, 0.1, len(self.risk_management))
            self.canvas.axes.set_ylim([min(self.risk_management) * 0.9, max(self.risk_management) * 1.1])
        self.criteria, = self.canvas.axes.plot(self.x1[:1], self.risk_management[:1], animated=True, lw=1, color='grey')
        f = open("data/program_data_h" + str(filenumber) + ".txt", 'r')
        readl = f.readline()
        self.data = np.array(list(map(lambda z: float(z), readl.strip().split())))
        self.y_fcast = np.append(self.data, self.y_fcast[len(self.data):])
        f.close()
        self.begin = 0
        self.index = len(self.data)
        self.i = 0
        self.correlation, = self.canvas.axes.plot(self.x[:1], self.correl[:1], animated=True, lw=0, color='white')
        self.line_risk, = self.canvas.axes.plot(self.x1[:1], self.risk_exist[:1], animated=True, lw=0, color='white')
        self.line1, = self.canvas.axes.plot(self.x1, self.y_real, animated=True, lw=1, color='green')
        self.line, = self.canvas.axes.plot(self.x, self.y_fcast, animated=True, lw=1, color='red')
        self.line2, = self.canvas.axes.plot(self.x1, self.min_val, animated=True, lw=1, color='brown')
        self.line3, = self.canvas.axes.plot(self.x, self.max_val, animated=True, lw=1, color='blue')
        self.ani = animation.FuncAnimation(self.canvas.figure, self.modify_plot, blit=True,
                                           interval=abs(anim_speed - 100))

    def modify_plot(self, i):
        try:
            if self.playing and self.index < len(self.y_real):
                self.stop_func.clicked.connect(self.stop_animation)

                if self.index % self.window > self.window / 4:
                    if self.ind != 4:
                        correl = get_correlation(self.y_fcast[
                                             min(len(self.data) + self.i - (len(self.data) + self.i) % self.window,
                                                 len(self.y_fcast) - 1):
                                             min(len(self.y_fcast) - 1, len(self.data) + self.i)],
                                             self.y_real[
                                             min(max(0, len(self.data) + self.i - (len(self.data) + self.i) %
                                                     self.window),
                                                 len(self.y_fcast) - 1):
                                             min(len(self.y_fcast) - 1, len(self.data) + self.i)])
                    else:
                        correl = get_sp_correlation(self.y_fcast[
                                             min(len(self.data) + self.i - (len(self.data) + self.i) % self.window,
                                                 len(self.y_fcast) - 1):
                                             min(len(self.y_fcast) - 1, len(self.data) + self.i)],
                                             self.y_real[
                                             min(max(0, len(self.data) + self.i - (len(self.data) + self.i) %
                                                     self.window),
                                                 len(self.y_fcast) - 1):
                                             min(len(self.y_fcast) - 1, len(self.data) + self.i)])
                else:
                    correl = 0
                self.correl[min(len(self.y_fcast) - 1, self.index)] = correl * (
                            self.normalizer[1] - self.normalizer[0]) + self.normalizer[0]
                moved_pos = self.y_fcast[min(len(self.data) + self.i - (len(self.data) + self.i) % self.window + 1,
                                             len(self.y_fcast) - 1): min(self.index, len(self.y_fcast))]
                moved_neg = self.y_fcast[min(len(self.data) + self.i - (len(self.data) + self.i) % self.window,
                                             len(self.y_fcast) - 1): min(max(0, self.index - 1), len(self.y_fcast))]
                if len(moved_pos) == len(moved_neg):
                    differences = moved_pos - moved_neg

                else:
                    differences = moved_pos[:min(len(moved_pos), len(moved_neg))] - moved_neg[:min(len(moved_pos),
                                                                                                   len(moved_neg))]

                growth = get_mean(differences)
                variance = 1. / (self.window - 1) * get_variance(
                    self.y_real[max(0, len(self.data) + self.i - (len(self.data) + i) % self.window):
                                min(len(self.y_fcast) - 1, self.index)])

                alarms = [0] * len(self.levels)
                for i in range(len(self.levels)):
                    alarms[i] = self.alarm(i + 1, variance, growth)

                self.table_search()

            if not self.playing and self.begin < 1:
                self.line.set_xdata(np.arange(len(self.data)))
                self.line.set_ydata(self.data)
                self.line1.set_xdata(np.arange(len(self.data)))
                self.line1.set_ydata(self.y_real[:len(self.data)])
                self.begin += 1

            if self.begin == 1:
                self.playing = True
                self.ani.event_source.stop()

            if self.index >= len(self.y_real) - 2:
                self.ani.event_source.interval = 1000

            self.start_func.clicked.connect(self.start_animation)

            if self.read_risks:
                self.criteria.set_ydata(self.risk_management[:self.index])
                self.criteria.set_xdata(self.x1[:self.index])

                self.i += 1
                if self.index < len(self.y_real) and self.playing:
                    self.index += 1
                return [self.criteria]

            else:
                self.correlation.set_ydata(self.correl[:self.index])
                self.correlation.set_xdata(self.x1[:self.index])
                y = self.y_fcast[:min(len(self.y_fcast) - 1,
                                      len(self.data) + self.i - (len(self.data) + self.i) % self.window + self.window)]
                x = self.x[:min(len(self.y_fcast) - 1,
                                (len(self.data) + self.i) - (len(self.data) + self.i) % self.window + self.window)]
                self.line.set_ydata(y)
                self.line.set_xdata(x)
                y1 = self.y_real[:min(len(self.y_real) - 1, self.index)]
                x1 = self.x1[:min(len(self.y_real) - 1, self.index)]
                self.i += 1
                if self.index < len(self.y_real) and self.playing:
                    self.index += 1
                self.line1.set_ydata(y1)
                self.line1.set_xdata(x1)

            return [self.line1, self.line, self.line3, self.line2, self.correlation]

        except IndexError:
            self.playing = False
            self.ani.event_source.stop()
            if self.read_risks:
                return [self.criteria]

            else:
                return [self.line1, self.line, self.line3, self.line2]

    def stop_animation(self):
        self.playing = True
        self.ani.event_source.stop()

    def start_animation(self):
        self.playing = True
        self.ani.event_source.start()

    def find_in_column(self, column_num, value):
        for rowIndex in range(self.table.rowCount()):
            tw_item = self.table.item(rowIndex, column_num)
            if tw_item.text() == value:
                return rowIndex
        else:
            return -1

    def table_search(self):
        number = self.filenumber + 1
        if number == 1:
            number = '1st'
        elif number == 2:
            number = '2nd'
        else:
            number = '3rd'
        row_num = self.find_in_column(0, str(self.index))
        if row_num >= 0:
            if not self.read_risks:
                self.table.setItem(row_num, self.filenumber + 1, QTableWidgetItem(str(self.y_real[self.index])))

        else:
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem(str(self.index)))
            if not self.read_risks:
                self.table.setItem(0, self.filenumber + 1, QTableWidgetItem(str(self.y_real[self.index])))
            else:
                self.table.setItem(0, 4, QTableWidgetItem("Conventional situation"))

            for i in range(1, 7):
                if i != self.filenumber + 1:
                    self.table.setItem(0, i, QTableWidgetItem("-"))
            row_num = 0

        if self.risk_exist[self.index] != 0:
            if self.table.item(row_num, 5).text() == '1' and self.table.item(row_num, 4).text()[-1] != 'y':
                self.table.setItem(row_num, 5, QTableWidgetItem('2'))
                self.table.setItem(row_num, 4, QTableWidgetItem('Danger: 2 parameters'))
                self.table.setItem(row_num, 6, QTableWidgetItem(
                    self.table.item(row_num, 6).text() + ', ' + number))

            elif self.table.item(row_num, 5).text() == '2' and self.table.item(row_num, 4).text()[-1] != 'y':
                self.table.setItem(row_num, 5, QTableWidgetItem('3'))
                self.table.setItem(row_num, 4, QTableWidgetItem('Danger: 3 parameters'))
                self.table.setItem(row_num, 6, QTableWidgetItem(
                    self.table.item(row_num, 6).text() + ', ' + number))

            elif self.table.item(row_num, 4).text()[-1] != 'y':
                self.table.setItem(row_num, 5, QTableWidgetItem('1'))
                self.table.setItem(row_num, 4, QTableWidgetItem('Danger: 1 parameter'))
                self.table.setItem(row_num, 6, QTableWidgetItem(number))
        else:
            if self.table.item(row_num, 5).text() not in ['1', '2', '3'] and \
                    self.table.item(row_num, 4).text()[-1] != 'y':
                self.table.setItem(row_num, 5, QTableWidgetItem('0'))
                self.table.setItem(row_num, 4, QTableWidgetItem('Conventional situation'))

        if self.y_fcast[self.index] < self.levels[1][0]:
            self.table.setItem(row_num, 4, QTableWidgetItem('Emergency'))
            self.table.setItem(row_num, 5, QTableWidgetItem('Maximum'))
            self.table.setItem(row_num, 6, QTableWidgetItem(number + ' parameter(s)'))

        not_yet = 0
        for i in range(self.num_of_y):
            if self.table.item(row_num, i + 1).text() == '-':
                not_yet = 1

        if not_yet == 0 and self.table.item(row_num, 5).text() not in ['0', '-'] and \
                self.table.item(row_num, 6).text()[-1] != ')':
            self.table.setItem(row_num, 6, QTableWidgetItem(self.table.item(row_num, 6).text() + ' parameter(s)'))

    def alarm(self, level, variance_, growth_):
        if ((self.correl[min(len(self.y_fcast) - 1, self.index)] > 0.5 and
             self.levels[level - 1][1] - self.y_real[min(len(self.y_fcast) - 1, self.index)] < np.sqrt(
                    variance_) and growth_ > 0)
                or
                (self.correl[min(len(self.y_fcast) - 1, self.index)] > 0.5 and
                 -self.levels[level - 1][0] + self.y_real[min(len(self.y_fcast) - 1, self.index)] < np.sqrt(
                            variance_) and growth_ < 0)
                or
                (self.correl[min(len(self.y_fcast) - 1, self.index)] < -0.5 and
                 self.levels[level - 1][1] - self.y_real[min(len(self.y_fcast) - 1, self.index)] < np.sqrt(
                            variance_) and growth_ < 0)
                or
                (self.correl[min(len(self.y_fcast) - 1, self.index)] < -0.5 and
                 -self.levels[level - 1][0] + self.y_real[min(len(self.y_fcast) - 1, self.index)] < np.sqrt(
                            variance_) and growth_ > 0)):

            return level
        else:
            return 0

    def on_start(self):
        if self.playing:
            pass
        else:
            self.begin += 1
            self.playing = True
            self.ani.event_source.start()

    def on_stop(self):
        if self.playing:
            string = str(list(self.y_fcast[:self.i + len(self.data)])).replace('[', '')
            string = string.replace(']', '')
            string = string.replace(',', '')
            f = open("data/program_data_h" + str(self.filenumber) + ".txt", 'w+')
            if self.index >= len(self.y_fcast) - 1:
                f.write('')
            else:
                f.write(string)
            f.close()
            self.playing = False
            self.ani.event_source.stop()
        else:
            pass

    @staticmethod
    def close_event(event):

        event.accept()


class UI(QDialog):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent)

        self.reset = QPushButton("Reset")
        self.run = QPushButton("Execute")
        self.multi = QCheckBox("Multi")
        self.useStylePaletteCheckBox = QCheckBox("Light")

        self.topRightGroupBox = QGroupBox("Prognosis")
        self.speed_label = QLabel("Display speed")
        self.speed = QSpinBox()
        self.per_label = QLabel("Period window")
        self.period = QSpinBox()
        self.pro_label = QLabel("Prognosis window")
        self.prognosis = QSpinBox()
        self.resume = QPushButton("Resume")
        self.pause = QPushButton("Pause")

        self.tab1hbox = QHBoxLayout()
        self.Btab1 = QWidget()
        self.Btable = QTableWidget(self.Btab1)
        self.bottomTabWidget = QTabWidget()

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
        self.canvas5 = Graph(self, width=6, height=3, dpi=100, title='Margin of tolerable risk (S)')
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

        self.topMid2GroupBox.setFixedWidth(200)

        self.topMid2GroupBox.setLayout(layout)

    def create_top_right_group_box(self):

        self.resume.setFlat(True)
        self.pause.setFlat(True)
        self.speed.setRange(1, 100)
        self.period.setRange(1, 1000)
        self.prognosis.setRange(1, 1000)

        layout = QGridLayout()

        layout.addWidget(self.speed, 0, 1)
        layout.addWidget(self.period, 2, 1)
        layout.addWidget(self.prognosis, 3, 1)
        layout.addWidget(self.speed_label, 0, 0)
        layout.addWidget(self.per_label, 2, 0)
        layout.addWidget(self.pro_label, 3, 0)
        layout.addWidget(self.resume, 4, 0)
        layout.addWidget(self.pause, 4, 1)
        self.topRightGroupBox.setFixedWidth(235)

        self.topRightGroupBox.setLayout(layout)

    def create_bottom_group_box(self):
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
        self.useStylePaletteCheckBox.setEnabled(False)
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
        animations = []
        for i in range(parameters[4] + 2):
            if i < 3:
                y1, y2 = create_animation(x, y[:, i], [orders, numbers], window_build, window_forecast, kind)
                y1, y2 = denormalize((y1, y2), normalizer[i])
                y2 = y2 + np.random.normal(0, 0.01 * (max(y2) - min(y2)), len(y2))
                animations.append(Animation(y1, y2, window_forecast, True, i, speed, arr[i], self.pause, self.resume,
                                            self.Btable, parameters[4], normalizer[i], False, sensors,
                                            self.graphs[i], i))
            else:
                animations.append(Animation(y1, y2, window_forecast, True, 3, speed, [[-1, 400]] * 4, self.pause,
                                            self.resume, self.Btable, parameters[4], normalizer[2], True, sensors,
                                            self.graphs[i], i))
            self.pause.clicked.connect(animations[i].stop_animation)
            self.resume.clicked.connect(animations[i].start_animation)


def memory_saver(f):
    memory = {}

    def inner_function(x, y):
        if x not in memory:
            memory[(x, y)] = f(x, y)
            return memory[(x, y)]
        else:
            return memory[(x, y)]

    return inner_function


@memory_saver
def chebyshev(n, x):
    if n == 0:
        return 1
    elif n == 1:
        return x
    else:
        return 2 * x * chebyshev(n - 1, x) - chebyshev(n - 1, x)


@memory_saver
def legendre(n, x):
    if n == 0:
        return 0.5
    elif n == 1:
        return x
    else:
        return (2 * n + 1) / (n + 1) * x * legendre(n - 1, x) - n / (n + 1) * legendre(n - 2, x)


@memory_saver
def hermite(n, x):
    coef = 2
    if n == 0:
        return 0.5
    if n == 1:
        return coef * x
    else:
        return coef * (x * hermite(n - 1, x) - (n - 1) * hermite(n - 2, x))


@memory_saver
def laguerre(n, x):
    if n == 0:
        return 0.5
    if n == 1:
        return 1 - x
    else:
        return 1 / n * ((2 * n - 1 - x) * laguerre(n - 1, x) - (n - 1) * laguerre(n - 2, x))


def load_data(lenx, file_x, file_y):
    x = []
    y = []
    read_x = open("data/" + file_x + ".txt", 'r')
    read_y = open("data/" + file_y + ".txt", 'r')
    for i in range(lenx):
        x.append(list(map(lambda z: float(z), (read_x.readline()).split())))
        y.append(list(map(lambda z: float(z), (read_y.readline()).split())))
        x[i] = x[i][:len(x[i])]
        y[i] = y[i][:len(y[i])]
    return [np.array(x), np.array(y)]


def normalize(data, is_multi):
    normalizer = []
    for arr in data:
        normalizer = []
        for i in range(arr.shape[1]):
            arr[:, i] += np.random.normal(0, (max(arr[:, i]) - min(arr[:, i])) * 0.001, len(arr[:, i]))
            m = min(arr[:, i])
            m_big = max(arr[:, i])
            normalizer.append([m, m_big])
            arr[:, i] -= m
            arr[:, i] /= (m_big - m)
    if is_multi:
        data[1] += 2
        data[1] = np.log(data[1])
    return data, normalizer


def denormalize(data, normalizer):
    for arr in data:
        for i in range(len(arr)):
            arr[i] *= (normalizer[1] - normalizer[0])
            arr[i] += normalizer[0]
    return data


def set_poly(kind, orders, numbers, x, is_multi):
    apply = None
    if kind == 'Chebyshev':
        apply = chebyshev
    if kind == 'Legendre':
        apply = legendre
    if kind == 'Hermite':
        apply = hermite
    if kind == 'Laguerre':
        apply = laguerre
    polynomial = []
    for k in range(x.shape[0]):
        polynomial.append([])
        for j in range(0, numbers[0]):
            if j == 0:
                polynomial[k].append(apply(0, 2 * x[k][j] - 1))
            for i in range((orders[0])):
                if is_multi:
                    polynomial[k].append(np.log(2 + apply(i + 1, 2 * x[k][j] - 1)))
                else:
                    polynomial[k].append(apply(i + 1, 2 * x[k][j] - 1))
        for j in range(numbers[0], numbers[1] + numbers[0]):
            for i in range((orders[1])):
                if is_multi:
                    polynomial[k].append(np.log(2 + apply(i + 1, 2 * x[k][j] - 1)))
                else:
                    polynomial[k].append(apply(i + 1, 2 * x[k][j] - 1))
        for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
            for i in range((orders[2])):
                if is_multi:
                    polynomial[k].append(np.log(2 + apply(i + 1, 2 * x[k][j] - 1)))
                else:
                    polynomial[k].append(apply(i + 1, 2 * x[k][j] - 1))
    polynomial = np.array(polynomial)
    return polynomial


def fit(polynomial, y):
    return np.linalg.lstsq(polynomial, y, rcond=1)[0]


def predict(coefc, x, is_multi, min_poly=0):
    return np.exp(np.dot(x, np.array(coefc).T - min_poly)) if is_multi else np.dot(x, np.array(coefc).T)


def create_animation(x, y, settings, build_window, forecast_window, kind):
    j = 0
    y2 = copy.copy(y)
    y1 = np.array([])
    for i in range(len(y2) - build_window):
        if i == j * forecast_window:
            pol = set_poly(kind, settings[0],
                           settings[1], x[j * forecast_window: j * forecast_window + build_window], False)

            lambd = fit(pol, y2[j * forecast_window: j * forecast_window + build_window])

            predicted = predict(lambd, set_poly(kind, settings[0], settings[1],
                                                x[j * forecast_window + build_window: min(len(x),
                                                                                          (j + 1) * forecast_window +
                                                                                          build_window)], False), False)

            y1 = np.hstack((y1, predicted))
            j += 1
    return y1, y2[build_window:]


def get_mean(y):
    if len(y) == 0:
        return 0
    return sum(y) / len(y)


def get_variance(y):
    y1 = copy.copy(y)
    y_mean = get_mean(y1)
    y1 -= y_mean
    return sum(y1 ** 2)


def get_correlation(y, y_forecast):
    y_mean = get_mean(y)
    forecast_mean = get_mean(y_forecast)
    y_centralized = y - y_mean
    y_forecast_centralized = y_forecast - forecast_mean
    result = np.dot(y_centralized, y_forecast_centralized)
    correlation = np.sqrt(get_variance(y) * get_variance(y_forecast))
    if correlation == 0:
        return 0
    return result / correlation


def get_sp_correlation(y, y_forecast):
    return spearmanr(y, y_forecast)[0]


def indicator(y, window):
    combinat = list(combinations(np.arange(len(y)), 2))
    indicator_fail = np.zeros((len(combinat), len(y[0]) // window - 1))
    for i in range(len(y[0]) // window - 2):
        for j in range(len(combinat)):
            if get_correlation(y[combinat[j][0]][i * window:(i + 1) * window],
                               y[combinat[j][1]][i * window:(i + 1) * window]) * \
                    get_correlation(y[combinat[j][0]][(i + 1) * window:(i + 2) * window],
                                    y[combinat[j][1]][(i + 1) * window:(i + 2) * window]) < -1 * (2 / (window ** 1.15)):
                indicator_fail[j][i] = 1

    ind = np.zeros(len(y[0]) // window - 1)
    for i in range(len(y[0]) // window - 1):
        tmp = 0
        for j in range(len(combinat)):
            tmp += indicator_fail[j][i]
        if tmp > 0:
            ind[i] = 1
    return ind


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = UI()
    main_window.show()
    main_window.useStylePaletteCheckBox.toggled.connect(main_window.change_palette)
    main_window.reset.clicked.connect(main_window.clr)
    main_window.run.clicked.connect(main_window.execute)
    app.exec_()
