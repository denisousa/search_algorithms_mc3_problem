from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.pntx import SinglePointCrossover
from nsga2_mutation import MyMutation
from nsga2_problem import MyProblem
from nsga2_utils import print_results
import time


def execute_nsga2():
    algorithm = NSGA2(
        pop_size=10,
        sampling=IntegerRandomSampling(),
        crossover=SinglePointCrossover(),
        mutation=MyMutation(),
        eliminate_duplicates=True,
    )

    problem = MyProblem()
    result = minimize(
        problem,
        algorithm,
        get_termination("time", "54:10:49"),
        seed=int(time.time()),
        verbose=True,
    )

    print_results(result)
