import numpy as np
from copy import deepcopy


def crossover(parents, offspring_size):
    offspring = np.empty(offspring_size)
    crossover_point = np.uint8(offspring_size[1] / 2)

    for k in range(offspring_size[0]):
        parent1_idx = np.random.randint(0, parents.shape[0])
        parent2_idx = np.random.randint(0, parents.shape[0])

        offspring[k, :crossover_point] = parents[parent1_idx, :crossover_point]
        offspring[k, crossover_point:] = parents[parent2_idx, crossover_point:]

    return offspring


class GeneticAlgorithm(object):
    def __init__(self, initial_generation, target_function, populations_to_take, precision, scale=50):
        self.initial_generation = initial_generation
        self.target_function = target_function
        self.scale = scale
        self.population_size = initial_generation.shape[0]
        self.populations_to_take = populations_to_take
        self.precision = precision
        self.best_score = np.inf
        self.mutation_additive = lambda: np.random.randint(low=0, high=scale, size=(initial_generation.shape[1]))

    def select_mating_pool(self, population, fitness):
        parents = np.empty((self.populations_to_take, population.shape[1]))

        for parent_num in range(self.populations_to_take):
            fitness_idx = np.argmin(fitness)
            parents[parent_num, :] = population[fitness_idx, :]
            fitness[fitness_idx] = np.inf

        return parents

    def mutation(self, offspring_crossover):

        for idx in range(offspring_crossover.shape[0]):
            offspring_crossover[idx, :] = offspring_crossover[idx, :] + self.mutation_additive()

        return offspring_crossover

    def apply_function_on_array(self, ar):
        return np.array([self.target_function(ar[i, :]) for i in range(ar.shape[0])])

    def fit(self):
        cur_population = self.initial_generation
        best_points = []
        best_fits = []
        generation = 0
        fitness = self.apply_function_on_array(cur_population)
        best_idx = np.argmin(fitness)

        best_points.append(deepcopy(cur_population[best_idx, :]))
        best_fits.append(fitness[best_idx])
        self.best_score = fitness[best_idx]

        while self.best_score > self.precision:
            parents = self.select_mating_pool(cur_population, fitness)

            offspring_crossover = crossover(parents, offspring_size=(
                                                 self.population_size - parents.shape[0], cur_population.shape[1]))

            offspring_mutation = self.mutation(offspring_crossover)

            cur_population[:parents.shape[0], :] = parents
            cur_population[parents.shape[0]:, :] = offspring_mutation

            fitness = self.apply_function_on_array(cur_population)

            best_idx = np.argmin(fitness)
            best_points.append(deepcopy(cur_population[best_idx, :]))
            best_fits.append(fitness[best_idx])
            self.best_score = fitness[best_idx]
            generation += 1
            print(generation, self.best_score)
            if generation > 2:
                break

        return {'best_points': best_points, 'best_fits': best_fits}
