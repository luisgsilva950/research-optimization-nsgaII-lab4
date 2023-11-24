import random
from typing import List

import numpy as np
import numpy.random

from graphic_plotter import GraphicPlotter
from models import Customer, PA, Coordinate
from utils import DISTANCES


def get_customers() -> List[Customer]:
    customers = []
    with open('clientes.csv') as file:
        content = file.readlines()
        for index, row in enumerate(content):
            row = row.split(",")
            customer = Customer(coordinates=Coordinate(x=float(row[0]), y=float(row[1])),
                                consume=float(row[2]),
                                index=index)
            customers.append(customer)
    return customers


def get_pas() -> List[PA]:
    points = []
    for x in range(0, 1010, 10):
        for y in range(0, 1010, 10):
            points.append(PA(x=x, y=y, index=len(points)))
    return points


PAS = get_pas()
CUSTOMERS = get_customers()

for c in CUSTOMERS:
    for p in PAS:
        if DISTANCES[c.index][p.index] < 85:
            p.possible_customers.append(c)


class NSGAII:
    min_customers_attended = 570
    max_distance = 85
    max_active_points = 100
    max_consumed_capacity = 150

    def __init__(self, customers: List[Customer], points: List[PA], solution=None, priorities=None):
        self.customers = customers or []
        self.points = points or []
        self.solution = solution
        self.total_distance = 0
        self.pas_count = 0
        self.priorities = priorities

        # print(self.priorities)

    def get_solution(self, priorities: List[int] = None):
        if self.solution:
            return self

        if not priorities:
            priorities = np.random.permutation(len(self.points))

        count_pas, total_distance = 0, 0
        solution = [[] for _ in range(len(self.points))]
        customers_attended = set()
        for p in priorities:
            point = self.points[p]
            consume = 0
            for c in point.possible_customers:
                if c.index in customers_attended:
                    continue

                next_consume = consume + c.consume
                if next_consume > self.max_consumed_capacity:
                    break

                solution[p].append(c.index)
                customers_attended.add(c.index)
                consume = next_consume
                total_distance += DISTANCES[c.index][p]

        customers_count = 0
        for idx, l in enumerate(solution):
            if not l:
                continue
            count_pas += 1
            customers_count += len(l)

        self.priorities = priorities
        self.pas_count = count_pas
        self.total_distance = total_distance
        self.solution = solution

        return self

    def plot(self, idx: int = None):
        plotter = GraphicPlotter(f'NSGA Solution {idx or random.randint(0, 100)}', connexions=[
            (self.points[idx], [self.customers[cidx].coordinates for cidx in customers_idxs]) for idx, customers_idxs in
            enumerate(self.solution) if customers_idxs])

        plotter.plot()

    @staticmethod
    def from_csv() -> 'NSGAII':
        return NSGAII(customers=CUSTOMERS, points=PAS)

    def plot_customers(self):
        import matplotlib.pyplot as plt

        customers = self.customers
        pas = self.points

        r = np.random.random()
        b = np.random.random()
        g = np.random.random()
        color = (r, g, b)
        for customer in customers:
            plt.plot(customer.coordinates.x, customer.coordinates.y, 'o', c=color)

        r = np.random.random()
        b = np.random.random()
        g = np.random.random()
        color = (r, g, b)
        for pa in pas:
            plt.plot(pa.x, pa.y, '^', c=color)

        plt.grid()
        plt.show()

    def mutation(self):
        if random.random() > 0.7:
            return

        N = len(self.priorities)
        mutate_priorities = self.priorities

        n_exchanges = random.randint(1, 6)

        for _ in range(n_exchanges):
            i, j = random.randint(0, 100 - 1), random.randint(0, N - 1)
            mutate_priorities[i], mutate_priorities[j] = mutate_priorities[j], mutate_priorities[i]

        self.priorities = mutate_priorities


def dominate(solution1, solution2):  # verifica se geracao1 domina geracao2
    return (solution1.total_distance < solution2.total_distance and solution1.pas_count <= solution2.pas_count) or \
        (solution1.total_distance <= solution2.total_distance and solution1.pas_count < solution2.pas_count)


def crossover(solutionA, solutionB):
    N = len(solutionA.priorities)
    C = [0] * N

    A = solutionA.priorities
    B = solutionB.priorities

    A_idxs = np.argsort(A)
    B_idxs = np.argsort(B)

    for i in range(1, int(N / 2)):
        indice = A[A_idxs[i]]
        C[indice] = A[indice]

    for i in range(int(N / 2) + 1, N):
        indice = B[B_idxs[i]]
        if C[indice] == 0:
            C[indice] = B[indice]
        else:
            for j in range(N):
                if C[j] == 0:
                    C[j] = B[indice]
                    break
    return C


def get_next_generation_solutions(front):  # get the first N/2 front elements to the next generation
    next_gen_solutions = []

    for i in range(len(front)):
        for objeto in front[i]:
            if len(next_gen_solutions) < 50:
                if 50 - len(next_gen_solutions) > len(front[i]):
                    next_gen_solutions.append(objeto)
                else:
                    next_gen_solutions = next_gen_solutions + (
                        crowding_distance_(front[i], 50 - len(next_gen_solutions)))

    return next_gen_solutions


def crowding_distance_(front_component, N):
    points = []

    for i in range(len(front_component)):
        points.append((front_component[i].pas_count, front_component[i].pas_count))

    def crowding_distance(point, other_points):
        distances = [np.sqrt((point[0] - p[0]) ** 2 + (point[1] - p[1]) ** 2) for p in other_points]
        return sum(sorted(distances)[1:-1])

    selected_points = []

    for _ in range(N):
        crowding_dict = {i: crowding_distance(point, points) for i, point in enumerate(points)}
        max_crowding_index = max(crowding_dict, key=crowding_dict.get)
        selected_points.append(points[max_crowding_index])

    selected_solutions = []

    for i in range(len(selected_points)):
        indice = points.index(selected_points[i])
        selected_solutions.append(front_component[indice])

    return selected_solutions


if __name__ == '__main__':
    solution_number = 50
    generation = []
    first_pop = []

    for i in range(solution_number):
        s = NSGAII.from_csv()
        s.get_solution()
        first_pop.append(s)

    print("Soluções iniciais geradas...")
    generation = []

    NSGAII_interactions = 50

    population = first_pop

    for count in range(NSGAII_interactions):
        front = []

        # print("NSGAII_interactions")
        children_priorities = []
        children = []
        for i in range(len(population)):
            # print("i_population")
            j, k = random.sample(range(0, len(population)), 2)
            children_priorities.append(crossover(population[j], population[k]))

        for i in range(len(children_priorities)):
            # print("i_children_priorities")
            c = NSGAII(customers=CUSTOMERS, points=PAS, priorities=children_priorities[i])
            c.mutation()
            c.get_solution()
            children.append(c)

        population = population + children

        new_solutions_count = 0
        while new_solutions_count < 100:
            remove_idxs = set()
            front_atual = []
            for i in range(len(population)):
                Sp = []
                non_p = 0

                for j in range(len(population)):
                    if dominate(population[i], population[j]):
                        Sp.append(population[i])
                    elif dominate(population[j], population[i]):
                        non_p += 1

                if non_p == 0:
                    new_solutions_count += 1
                    remove_idxs.add(i)
                    front_atual.append(population[i])

            population = [p for idx, p in enumerate(population) if idx not in remove_idxs]

            front.append(front_atual)

        # for solutions in front:
        #     import matplotlib.pyplot as plt
        #
        #     r = numpy.random.random()
        #     b = numpy.random.random()
        #     g = numpy.random.random()
        #     color = (r, g, b)
        #     for s in solutions:
        #         plt.plot(s.pas_count, s.total_distance, '^', c=color)
        #         plt.grid()
        #
        # plt.show()

        generation.append(front[0])

        min_pas_count = min([n.pas_count for n in front[0]])
        min_total_distance = min([n.total_distance for n in front[0]])
        print([min_pas_count, min_total_distance])

        population = get_next_generation_solutions(front)
