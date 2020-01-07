import numpy as np
from itertools import combinations
import copy
np.set_printoptions(linewidth=np.inf)


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


'''
def set_poly(mode, orders, numbers, x, is_multi):
    
    applier = None                                      print('x ' + str(x))
    if mode == 'Chebyshev':                             print('y ' + str(y))
        applier = chebyshev                             print('forecast ' + str(window_forecast))
    if mode == 'Legendre':                              print('build ' + str(window_build))
        applier = legendre                              print('speed ' + str(speed))
    if mode == 'Hermite':                               print('kind ' + str(kind))
        applier = hermite                               print('numbers ' + str(numbers))
    if mode == 'Laguerre':                              print('orders ' + str(orders))
        applier = laguerre                              print('y ' + str(file_y))
    polynomial = []                                     print('x ' + str(file_x))
    min_poly = None                                     print('multi ' + str(is_multi))
    for k in range(x.shape[0]):                         print('parameters' + str(parameters))
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
 
'''


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
    return np.exp(x @ np.array(coefc).T - min_poly) if is_multi else x @ np.array(coefc).T


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
                                                                                          (j+1) * forecast_window +
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
