from typing import Optional

from main.core.problem_specification.tasks_specification.Task import Task


class AperiodicTask(Task):
    """
    Aperiodic task specification
    """

    def __init__(self, c: float, a: float, d: float, e: Optional[float]):
        """
        :param c: Task worst case execution time in seconds at base frequency
        :param a: Task arrive time, must be lower or equal than the hyperperiod
        :param d: Task deadline time, must be lower or equal than the hyperperiod
        :param e: Energy consumption
        """
        super().__init__(c, e)
        self.a: float = a
        self.d: float = d