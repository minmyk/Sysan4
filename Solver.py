import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from Optimizer import *
import warnings

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


def load_data(x_len, y_file, x_file, numbers_y, numbers_x):
    cols_x = []
    for j in range(len(numbers_x)):
        cols_x += ['X' + str(j + 1) + str(i + 1) for i in range(numbers_x[j])]
    cols_y = ['Y' + str(i + 1) for i in range(numbers_y)]
    x = []
    y = []
    read_x = open('data/' + x_file + ".txt", 'r')
    read_y = open('data/' + y_file + ".txt", 'r')
    for i in range(min(x_len, x_len)):
        x.append(list(map(lambda z: float(z.replace(',', '.')), (read_x.readline()).split())))
        y.append(list(map(lambda z: float(z.replace(',', '.')), (read_y.readline()).split())))
        x[i] = x[i][1:]
    df_x = pd.DataFrame(x, columns=cols_x)
    df_y = pd.DataFrame(y, columns=cols_y)
    return df_x, df_y


def set_vars(orders, numbers, x):
    variables = []
    for k in range(x.shape[0]):
        variables.append([])
        for j in range(0, numbers[0]):
            if j == 0:
                variables[k].append(1)
            for i in range((orders[0])):
                variables[k].append(x[k][j] ** (i + 1))
        for j in range(numbers[0], numbers[1] + numbers[0]):
            for i in range((orders[1])):
                variables[k].append(x[k][j] ** (i + 1))
        for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
            for i in range((orders[2])):
                variables[k].append(x[k][j] ** (i + 1))
    return np.array(variables)


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


def set_psy(coefc, numbers, orders, x, is_multi, min_poly=None):
    polynomial = []

    if is_multi:
        for k in range(x.shape[0]):
            polynomial.append([1])
            index = 0
            for j in range(0, numbers[0]):
                if j == 0:
                    index += 1
                else:
                    index += orders[0]
                polynomial[k].append(np.log(min_poly + predict(coefc[index: index + orders[0]],
                                                               x[k, index: index + orders[0]], is_multi, min_poly)))
            for j in range(0, numbers[1]):
                if j == 0:
                    index += orders[0]
                else:
                    index += orders[1]
                polynomial[k].append(np.log(min_poly + predict(coefc[index: index + orders[1]],
                                                               x[k, index: index + orders[1]], is_multi, min_poly)))
            for j in range(0, numbers[2]):
                if j == 0:
                    index += orders[1]
                else:
                    index += orders[2]
                polynomial[k].append(np.log(min_poly + predict(coefc[index: index + orders[2]],
                                                               x[k, index: index + orders[2]], is_multi, min_poly)))
    else:
        for k in range(x.shape[0]):
            polynomial.append([1])
            index = 0
            for j in range(0, numbers[0]):
                if j == 0:
                    index += 1
                else:
                    index += orders[0]
                polynomial[k].append(predict(coefc[index: index + orders[0]], x[k, index: index + orders[0]], is_multi))
            for j in range(0, numbers[1]):
                if j == 0:
                    index += orders[0]
                else:
                    index += orders[1]
                polynomial[k].append(predict(coefc[index: index + orders[1]], x[k, index: index + orders[1]], is_multi))
            for j in range(0, numbers[2]):
                if j == 0:
                    index += orders[1]
                else:
                    index += orders[2]
                polynomial[k].append(predict(coefc[index: index + orders[2]], x[k, index: index + orders[2]], is_multi))
    return np.array(polynomial)


def set_f(coefc, numbers, x, is_multi, min_poly=None):
    polynomial = []
    if is_multi:
        for k in range(x.shape[0]):
            polynomial.append([1])
            index = 1
            for j in range(0, len(numbers)):
                polynomial[k].append(np.log(min_poly + predict(coefc[index: index + numbers[j]],
                                                               x[k, index: index + numbers[j]], is_multi, min_poly)))
                index += numbers[j]
    else:
        for k in range(x.shape[0]):
            polynomial.append([1])
            index = 1
            for j in range(0, len(numbers)):
                polynomial[k].append(
                    predict(coefc[index: index + numbers[j]], x[k, index: index + numbers[j]], is_multi))
                index += numbers[j]
    return np.array(polynomial)


def fit(polynomial, y):
    return np.linalg.lstsq(polynomial, y, rcond=1)[0]


def predict(coefc, x, is_multi, min_poly=0):
    return np.exp(x @ np.array(coefc).T - min_poly) if is_multi else x @ np.array(coefc).T


def error(y, x, coefc, is_multi):
    difference = np.exp(y) - np.exp(x @ np.array(coefc).T) if is_multi \
        else x @ np.array(coefc).T - y
    return np.linalg.norm(difference)


def precision(y, x, kind, numbers, is_multi):
    warnings.filterwarnings("ignore")

    def func_to_opt(opt_x, _is_multi=is_multi):
        i, j, k = opt_x[0], opt_x[1], opt_x[2]
        pol_ = set_poly(kind, [i, j, k], numbers, x, _is_multi)[0]
        value = 0
        for t in range(y.shape[1]):
            lambd = fit(pol_, y[:, t - 1])
            value += error(y[:, t - 1], pol_, lambd, _is_multi)
        return value

    ga_holder = GeneticAlgorithm(initial_generation=np.random.randint(low=2, high=15, size=(5, 3)),
                                 scale=5,
                                 target_function=lambda l: func_to_opt(l),
                                 populations_to_take=2,
                                 precision=1e-8
                                 )
    result = ga_holder.fit()
    result = result['best_points'][-1]
    return result[0], result[1], result[2]


def show_apr(mode, orders, numbers, coefc, is_multi):
    if mode == 'Chebyshev':
        pol = 'T'
    elif mode == 'Legendre':
        pol = 'Leg'
    elif mode == 'Hermite':
        pol = 'H'
    elif mode == 'Laguerre':
        pol = 'Lag'
    else:
        pol = 'Error!'
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    k = 0
    string = ''
    if is_multi:
        for j in range(0, numbers[0]):
            if j == 0:
                k += 1
            for i in range((orders[0])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += "(" + "1 " + sign + str(round(coefc[k], 5)) + (pol + str(i + 1) +
                                                                         '(x' + str(j + 1) + ')').translate(sub) + ")"
                k += 1
        for j in range(numbers[0], numbers[1] + numbers[0]):
            for i in range((orders[1])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += "(" + "1 " + sign + str(round(coefc[k], 5)) + (pol + str(i + 1) +
                                                                         '(x' + str(j + 1) + ')').translate(sub) + ")"
                k += 1
        for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
            for i in range((orders[2])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += "(" + "1 " + sign + str(round(coefc[k], 5)) + (pol + str(i + 1) +
                                                                         '(x' + str(j + 1) + ')').translate(sub) + ")"
                k += 1
    else:
        for j in range(0, numbers[0]):
            if j == 0:
                string += str(round(coefc[k], 5))
                k += 1
            for i in range((orders[0])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += sign + str(round(coefc[k], 5)) + str((pol + str(i + 1) +
                                                                '(x' + str(j + 1) + ')')).translate(sub)
                k += 1
        for j in range(numbers[0], numbers[1] + numbers[0]):
            for i in range((orders[1])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += sign + str(round(coefc[k], 5)) + str((pol + str(i + 1) +
                                                                '(x' + str(j + 1) + ')')).translate(sub)
                k += 1
        for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
            for i in range((orders[2])):
                if coefc[k] < 0:
                    sign = ''
                else:
                    sign = '+'
                string += sign + str(round(coefc[k], 5)) + str((pol + str(i + 1) +
                                                                '(x' + str(i + 1) + ')')).translate(sub)
                k += 1
    return string


def show_vars(orders, numbers, coefc):
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    k = 0
    string = ''
    for j in range(0, numbers[0]):
        if j == 0:
            string += str(round(coefc[k], 5))
            k += 1
        for i in range((orders[0])):
            if coefc[k] < 0:
                sign = ''
            else:
                sign = '+'
            string += sign + str(round(coefc[k], 5)) + 'x' + (str(j + 1)).translate(sub) + '^' + str(str(i + 1))
            k += 1
    for j in range(numbers[0], numbers[1] + numbers[0]):
        for i in range((orders[1])):
            if coefc[k] < 0:
                sign = ''
            else:
                sign = '+'
            string += sign + str(round(coefc[k], 5)) + 'x' + (str(j + 1)).translate(sub) + '^' + str(str(i + 1))
            k += 1
    for j in range(numbers[1] + numbers[0], numbers[1] + numbers[0] + numbers[2]):
        for i in range((orders[2])):
            if coefc[k] < 0:
                sign = ''
            else:
                sign = '+'
            string += sign + str(round(coefc[k], 5)) + 'x' + (str(j + 1)).translate(sub) + '^' + str(str(i + 1))
            k += 1
    return string


def show_psy(numbers, coefc, is_multi):
    string = ''
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    if not is_multi:
        string += str(round(coefc[0], 5))
    for i in range(1, sum(numbers) + 1):
        if coefc[i] < 0:
            sign = ''
        else:
            sign = '+'
        if is_multi:
            string += "(" + "1 " + sign + str(round(coefc[i], 5)) + ('\u03C8' + str(i) +
                                                                     '(x' + str(i) + ')').translate(sub) + ")"
        else:
            string += sign + str(round(coefc[i], 5)) + ('\u03C8' + str(i) + '(x' + str(i) + ')').translate(sub)
    return string


def show_f(numbers, coefc, is_multi):
    string = ''
    sub = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
    if not is_multi:
        string += str(round(coefc[0], 5))
    for i in range(1, len(numbers) + 1):
        if coefc[i] < 0:
            sign = ''
        else:
            sign = '+'
        if is_multi:
            string += "(" + "1 " + sign + str(round(coefc[i], 5)) + ('\u03C6' + str(i) +
                                                                     '(x' + str(i) + ')').translate(sub) + ")"
        else:
            string += sign + str(round(coefc[i], 5)) + ('\u03C6' + str(i) + '(x' + str(i) + ')').translate(sub)
    return string


def visualize(y, x, coefc, t, kind, scaler, normal, is_multi, min_poly, err):
    if is_multi and not normal:
        normal = True
    rc('axes', linewidth=0.6)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.figure(figsize=(7.55, 3.73))
    if not normal:
        x1 = scaler.inverse_transform((x @ np.array(coefc).T).reshape((-1, 1))).flatten()
        y1 = scaler.inverse_transform(np.array(y).reshape((-1, 1))).flatten()
    else:
        x1 = x @ np.array(coefc).T
        y1 = np.array(y)
    n = np.arange(0, len(y), 1)
    if is_multi:
        plt.plot(n, np.exp(x1) - min_poly)
        plt.plot(n, np.exp(y1) - min_poly)
    else:
        plt.plot(n, x1)
        plt.plot(n, y1)
    plt.gca().legend(('Y' + str(t + 1), 'Approximation'))
    plt.title(str(kind) + ' error: ' + str(err))
    plt.savefig('data/fig' + str(t + 1) + '.png', orientation='landscape')
