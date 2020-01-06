import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import warnings
from itertools import combinations


import copy
from matplotlib import animation
from IPython.display import display, clear_output
import sys, os, random
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation


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


def load_data(lenx, leny, file_x, file_y):
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
            arr[:, i] += np.random.normal(0, (max(arr[:, i]) - min(arr[:, i]))*0.001, len(arr[:, i]))
            m = min(arr[:, i])
            mbig = max(arr[:, i])
            normalizer.append([m, mbig])
            arr[:, i] -= m
            arr[:, i] /= (mbig - m)
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


def set_poly(mode, orders, numbers, x, is_multi):
    applier = None
    if mode == 'Chebyshev':
        applier = chebyshev
    if mode == 'Legendre':
        applier = legendre
    if mode == 'Hermite':
        applier = hermite
    if mode == 'Laguerre':
        applier = laguerre
    polynomial = []
    min_poly = None
    for k in range(x.shape[0]):
        polynomial.append([])
        for j in range(0, numbers[0]):
            if j == 0:
                polynomial[k].append(applier(0, 2 * x[k][j] - 1))
            for i in range((orders[0])):
                polynomial[k].append(applier(i + 1, 2 * x[k][j] - 1))
        for j in range(numbers[0], numbers[1] + numbers[0]):
            for i in range((orders[1])):
                polynomial[k].append(applier(i + 1, 2 * x[k][j] - 1))
        for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
            for i in range((orders[2])):
                polynomial[k].append(applier(i + 1, 2 * x[k][j] - 1))

    if is_multi:
        min_poly = abs(min(np.array(polynomial).flatten())) + 1
        polynomial = []
        for k in range(x.shape[0]):
            polynomial.append([])
            for j in range(0, numbers[0]):
                if j == 0:
                    polynomial[k].append(applier(0, 2 * x[k][j] - 1))
                for i in range((orders[0])):
                    polynomial[k].append(np.log(min_poly + applier(i + 1, 2 * x[k][j] - 1)))
            for j in range(numbers[0], numbers[1] + numbers[0]):
                for i in range((orders[1])):
                    polynomial[k].append(np.log(min_poly + applier(i + 1, 2 * x[k][j] - 1)))
            for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
                for i in range((orders[2])):
                    polynomial[k].append(np.log(min_poly + applier(i + 1, 2 * x[k][j] - 1)))
    return np.array(polynomial), min_poly


def fit(polynomial, y):
    return np.linalg.lstsq(polynomial, y, rcond=1)[0]


def predict(coefc, x, is_multi, min_poly=0):
    return np.exp(x @ np.array(coefc).T - min_poly) if is_multi else x @ np.array(coefc).T


# new lab 4


def form_data_animation(x, y, settings, build_window, forecast_window, mode):
    j = 0
    y2 = copy.copy(y)
    y1 = np.array([])
    for i in range(len(y2) - build_window):
        if i == j * forecast_window:
            pol = set_poly(mode, settings[0], settings[1],
                           x[j * forecast_window: j * forecast_window + build_window], False)
            lambd = fit(pol, y2[j * forecast_window: j * forecast_window + build_window])  # j * build_window

            ind1 = j * forecast_window + build_window
            ind2 = min(len(x), (j + 1) * forecast_window + build_window)
            predicted = predict(lambd, set_poly(mode, settings[0], settings[1], x[ind1:ind2], False)[0], False)

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


def crazylation(y, y_forecast):
    y_mean = get_mean(y)
    forecast_mean = get_mean(y_forecast)
    y_centralized = y - y_mean
    y_forecast_centralized = y_forecast - forecast_mean
    result = y_centralized @ y_forecast_centralized
    correlation = np.sqrt(get_variance(y) * get_variance(y_forecast))
    if correlation == 0:
        return 0
    return result / correlation


def indicator(y, window):
    combinat = list(combinations(np.arange(len(y)), 2))
    indicator_fail = np.zeros((len(combinat), len(y[0]) // window - 1))
    for i in range(len(y[0]) // window - 2):
        for j in range(len(combinat)):
            if crazylation(y[combinat[j][0]][i * window:(i + 1) * window],
                           y[combinat[j][1]][i * window:(i + 1) * window]) * \
                    crazylation(y[combinat[j][0]][(i + 1) * window:(i + 2) * window],
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
