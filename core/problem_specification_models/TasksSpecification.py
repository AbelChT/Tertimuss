from typing import Optional

import scipy


class TasksSpecification(object):
    """
    System tasks
    """

    def __init__(self, tasks: list):
        """
        :param tasks: List of tasks
        """
        self.tasks = tasks
        self.h = scipy.lcm.reduce(list(map(lambda a: a.t, tasks)))  # Hyper period


class Task(object):
    """
    Task specification
    """

    def __init__(self, c: float, t: int, e: Optional[float]):
        """

        :param c: Task worst case execution time in CPU cycles
        :param t: Task period, equal to deadline
        :param e: Energy consumption
        """
        self.c = c
        self.t = t
        self.e = e
