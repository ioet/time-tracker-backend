import os


def check_variables_are_defined(variables):
    for var in variables:
        if var not in os.environ:
            raise EnvironmentError(
                "{} is not defined in the environment".format(var)
            )
