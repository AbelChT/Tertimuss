from typing import List
import numpy

import main.core.execution_simulator.system_modeling.ThermalModel
from main.core.problem_specification.cpu_specification import CpuSpecification
from main.core.problem_specification.tasks_specification.TasksSpecification import TasksSpecification


class ThermalModelFrequencyAware(main.core.execution_simulator.system_modeling.ThermalModel.ThermalModel):
    """
    Thermal model where cpu frequency is used to simulate the tasks heat generation
    """

    @staticmethod
    def _get_dynamic_power_consumption(cpu_specification: CpuSpecification,
                                       tasks_specification: TasksSpecification,
                                       clock_relative_frequencies: List[float]) -> numpy.ndarray:
        """
        Method to implement. Return an array with shape (m , n). Each place contains the weight in the
        arcs t_exec_n -> cpu_m

        :param cpu_specification: Cpu specification
        :param tasks_specification: Tasks specification
        :param clock_relative_frequencies: Core frequencies
        :return: an array with shape (m , n). Each place contains the weight in the arcs t_exec_n -> cpu_m
        """

        n: int = len(tasks_specification.periodic_tasks) + len(tasks_specification.aperiodic_tasks)

        consumption_by_cpu = [
            (cpu_specification.cores_specification.energy_consumption_properties.dynamic_alpha * (f ** 3) +
             cpu_specification.cores_specification.energy_consumption_properties.dynamic_beta) for f in
            clock_relative_frequencies]

        return numpy.repeat(numpy.asarray(consumption_by_cpu).reshape((-1, 1)), n, axis=1)
