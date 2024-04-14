from pymoo.core.mutation import Mutation
import yaml
import random

with open("parameters.yml", "r") as file:
    search_space = yaml.safe_load(file)


class MyMutation(Mutation):
    def __init__(self):
        super().__init__()

    def _do(self, problem, X, **kwargs):
        for i in range(len(X)):
            r = random.random()
            if r <= 0.05:
                index_parameter_will_mutated = random.randint(0, len(X[i]) - 1)

                possible_values = list(search_space.values())[
                    index_parameter_will_mutated
                ]
                len_possible_values = len(possible_values)

                random_index = random.choice(
                    [
                        num
                        for num in range(0, len_possible_values)
                        if num != X[i][index_parameter_will_mutated]
                    ]
                )

                X[i][index_parameter_will_mutated] = random_index

        return X
