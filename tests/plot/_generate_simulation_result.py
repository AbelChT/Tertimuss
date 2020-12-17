"""
This file pretends to define an example simulation result that can be used to test the plotting packages
"""
from typing import Optional, Tuple, List

from tertimuss.simulation_lib.simulator import RawSimulationResult, JobSectionExecution, CPUUsedFrequency
from tertimuss.simulation_lib.system_definition import PeriodicTask, PreemptiveExecution, Criticality, TaskSet, Job


def create_implicit_deadline_periodic_task_h_rt(task_id: int, worst_case_execution_time: int,
                                                period: float, priority: Optional[int]) -> PeriodicTask:
    # Create implicit deadline task with priority equal to identification id
    return PeriodicTask(identification=task_id,
                        worst_case_execution_time=worst_case_execution_time,
                        relative_deadline=period,
                        best_case_execution_time=None,
                        execution_time_distribution=None,
                        memory_footprint=None,
                        priority=priority,
                        preemptive_execution=PreemptiveExecution.FULLY_PREEMPTIVE,
                        deadline_criteria=Criticality.HARD,
                        energy_consumption=None,
                        phase=None,
                        period=period)


def get_simulation_result() -> Tuple[TaskSet, List[Job], RawSimulationResult]:
    periodic_tasks = [
        create_implicit_deadline_periodic_task_h_rt(3, 3000, 7.0, 3),
        create_implicit_deadline_periodic_task_h_rt(2, 4000, 7.0, 2),
        create_implicit_deadline_periodic_task_h_rt(1, 4000, 14.0, 1),
        create_implicit_deadline_periodic_task_h_rt(0, 3000, 14.0, 0)
    ]

    jobs_list = [
        # Task 3
        Job(identification=0, activation_time=0.0, task=periodic_tasks[0]),
        Job(identification=1, activation_time=7.0, task=periodic_tasks[0]),

        # Task 2
        Job(identification=2, activation_time=0.0, task=periodic_tasks[1]),
        Job(identification=3, activation_time=7.0, task=periodic_tasks[1]),

        # Task 1
        Job(identification=4, activation_time=0.0, task=periodic_tasks[2]),

        # Task 0
        Job(identification=5, activation_time=0.0, task=periodic_tasks[3]),
    ]

    tasks = TaskSet(
        periodic_tasks=periodic_tasks,
        aperiodic_tasks=[],
        sporadic_tasks=[]
    )

    simulation_result = RawSimulationResult(have_been_scheduled=True, scheduler_acceptance_error_message=None,
                                            job_sections_execution={0: [
                                                JobSectionExecution(job_id=0, task_id=3, execution_start_time=0.0,
                                                                    execution_end_time=3.0,
                                                                    number_of_executed_cycles=3000),
                                                JobSectionExecution(job_id=2, task_id=2, execution_start_time=3.0,
                                                                    execution_end_time=4.0,
                                                                    number_of_executed_cycles=1000),
                                                JobSectionExecution(job_id=4, task_id=1, execution_start_time=4.0,
                                                                    execution_end_time=7.0,
                                                                    number_of_executed_cycles=3000),
                                                JobSectionExecution(job_id=1, task_id=3, execution_start_time=7.0,
                                                                    execution_end_time=10.0,
                                                                    number_of_executed_cycles=3000),
                                                JobSectionExecution(job_id=3, task_id=2, execution_start_time=10.0,
                                                                    execution_end_time=11.0,
                                                                    number_of_executed_cycles=1000)], 1: [
                                                JobSectionExecution(job_id=2, task_id=2, execution_start_time=0.0,
                                                                    execution_end_time=3.0,
                                                                    number_of_executed_cycles=3000),
                                                JobSectionExecution(job_id=4, task_id=1, execution_start_time=3.0,
                                                                    execution_end_time=4.0,
                                                                    number_of_executed_cycles=1000),
                                                JobSectionExecution(job_id=5, task_id=0, execution_start_time=4.0,
                                                                    execution_end_time=7.0,
                                                                    number_of_executed_cycles=3000),
                                                JobSectionExecution(job_id=3, task_id=2, execution_start_time=7.0,
                                                                    execution_end_time=10.0,
                                                                    number_of_executed_cycles=3000)]},
                                            cpus_frequencies={0: [
                                                CPUUsedFrequency(frequency_used=1000, frequency_set_time=0.0,
                                                                 frequency_unset_time=14.0)], 1: [
                                                CPUUsedFrequency(frequency_used=1000, frequency_set_time=0.0,
                                                                 frequency_unset_time=14.0)]},
                                            scheduling_points=[0.0, 3.0, 4.0, 7.0, 10.0], temperature_measures={},
                                            hard_real_time_deadline_missed_stack_trace=None)
    return tasks, jobs_list, simulation_result
