import datetime
import random
from typing import List

import numpy as np
import numpy.random

from models import Customer, PA, Coordinate
from utils import DISTANCES


class NSGAII:
    min_customers_attended = 570
    max_distance = 85
    max_active_points = 100
    max_consumed_capacity = 150

    def __init__(self, customers: List[Customer], points: List[PA],
                 solution=None, active_points=None,
                 penal: float = 0.0, penal_fitness: float = 0.0,
                 fitness: float = 0.0, k: int = 1, total_distance: float = 0):
        self.customers = customers or []
        self.points = points or []
        self.k = k
        self.fitness = fitness
        self.penal_fitness = penal_fitness
        self.penal = penal
        self.active_points = active_points or set()
        self.total_distance = total_distance
        self.priorities = np.random.permutation(len(self.points))

        print(self.priorities)

        for c in self.customers:
            for p in self.points:
                if DISTANCES[c.index][p.index] < self.max_distance:
                    # ordenar por distancia
                    p.possible_customers.append(c)

        # for p in self.points:
        #     print(f"Ponto: {p.index}, clientes: {[c.index for c in p.possible_customers]}")

        sorted_pas = np.argsort(self.priorities)

        solution = [[] for _ in range(len(self.points))]
        customers_attended = set()
        for p in sorted_pas:
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
                self.total_distance += DISTANCES[c.index][p]

        count = 0
        customers_count = 0
        for idx, l in enumerate(solution):
            if not l:
                continue
            count += 1
            customers_count += len(l)
            print(idx, l, "\n")

        print("Numero de pontos", count, "Taxa de clientes atendidos", customers_count / len(self.customers),
              "Distância total", self.total_distance)

    @staticmethod
    def from_csv() -> 'NSGAII':

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

        return NSGAII(customers=get_customers(), points=get_pas())

    def plot_customers(self):
        import matplotlib.pyplot as plt

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
            for x in range(0, 1010, 20):
                for y in range(0, 1010, 20):
                    points.append(PA(x=x, y=y, index=len(points)))
            return points

        customers = get_customers()
        pas = get_pas()

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

    # def print(self)
    #
    #     for

    def get_initial_solution(self) -> 'NSGAII':
        numpy.random.seed(
            int((datetime.datetime.utcnow() - datetime.timedelta(days=365 * random.randint(0, 20))).timestamp()))
        access_points: List[PA] = numpy.random.choice(self.get_points_with_space_100(), size=50)
        for customer in self.customers:
            distances = [DISTANCES[customer.index][p.index] for p in access_points]
            closer_point: PA = customer.get_closer_point(points=access_points, distances=distances)
            if closer_point and closer_point.index not in [p.index for p in self.active_points]:
                self.active_points.add(closer_point)
                customer.point_idx = closer_point.index
        return NSGAII(customers=self.customers, points=self.points,
                      active_points=self.active_points, fitness=self.fitness,
                      penal=self.penal,
                      penal_fitness=self.penal_fitness,
                      k=self.k, total_distance=self.total_distance)


if __name__ == '__main__':
    solutions = []
    nsga = NSGAII.from_csv()

    # start = time.time()
    #
    # for i in range(50):
    #     s = nsga.get_initial_solution()
    #     solutions.append(s)
    #
    # print("Initial solution", min([m.penal_fitness for m in solutions]), f"{time.time() - start} seconds")
    #
    # start = time.time()
    #
    # for _ in range(500):
    #     size = len(solutions)
    #
    #     for i in range(size):
    #         solution: NSGAII = solutions[i]
    #         solution.k = random.randint(1, 3)
    #         start = time.time()
    #         # print("Shaking...")
    #         solutions.append(solution.shake())
    # print("Shake", f"{time.time() - start} seconds")

    # print("Finish to generate mutations", f"{time.time() - start} seconds")

    # start = time.time()

    # solutions = numpy.random.permutation(solutions)

    # print("Finish to permutate", f"{time.time() - start} seconds")

    # new_solutions = []
    #
    # start = time.time()

    # print("Comparing...")

    # for i in range(0, len(solutions), 2):
    #     s1, s2 = solutions[i], solutions[i + 1]
    #     s1.objective_function()
    #     s2.objective_function()
    #     if s1.penal_fitness <= s2.penal_fitness:
    #         new_solutions.append(s1)
    #     else:
    #         new_solutions.append(s2)
    #
    # solutions = new_solutions
    #
    # print("Final solution", min([m.penal_fitness for m in solutions]), f"{time.time() - start} seconds")
