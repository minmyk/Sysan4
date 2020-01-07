from matplotlib import animation as animation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import *
from Solver import *


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
                 result_table, num_of_y, normalizer, read_risks, sensors, graph):
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
            self.risk_management = (self.risk_management - min(self.risk_management)) / (
                        max(self.risk_management) - min(self.risk_management))
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
                    correl = get_correlation(self.y_fcast[
                                         min(len(self.data) + self.i - (len(self.data) + self.i) % self.window,
                                             len(self.y_fcast) - 1):
                                         min(len(self.y_fcast) - 1, len(self.data) + self.i)],
                                         self.y_real[
                                         min(max(0, len(self.data) + self.i - (len(self.data) + self.i) % self.window),
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
