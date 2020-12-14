from typing import Dict, Optional, List

from matplotlib import pyplot, patches
from matplotlib.figure import Figure

from ._color_palette import __obtain_color_palette
from tertimuss_simulation_lib.simulator import RawSimulationResult, calculate_major_cycle
from tertimuss_simulation_lib.system_definition import TaskSet, Job


def generate_task_execution_plot(task_set: TaskSet, schedule_result: RawSimulationResult, start_time: float = 0,
                                 end_time: Optional[float] = None, title: Optional[str] = None) -> Figure:
    """
    Generate tasks execution plot
    :param task_set: Task set
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    cpu_color_id: Dict[int, int] = {j: i for i, j in enumerate(schedule_result.job_sections_execution.keys())}

    color_palette = __obtain_color_palette(len(cpu_color_id))

    tasks_ids: List[int] = sorted([i.identification for i in task_set.periodic_tasks + task_set.aperiodic_tasks +
                                   task_set.sporadic_tasks])

    tasks_to_lines_assignation: Dict[int, int] = {j: i for i, j in enumerate(tasks_ids)}

    fig, ax = pyplot.subplots()

    for cpu_id, sections_list in schedule_result.job_sections_execution.items():
        for section in sections_list:
            ax.barh(tasks_to_lines_assignation[section.task_id],
                    width=section.execution_end_time - section.execution_start_time,
                    left=section.execution_start_time,
                    color=color_palette[cpu_color_id[cpu_id]])

    ax.set_yticks(range(len(tasks_ids)))
    ax.set_yticklabels([f'Task {i}' for i in tasks_ids])

    cpus_legend = [patches.Patch(color=color_palette[j], label=f'CPU {i}') for i, j in
                   sorted(cpu_color_id.items(), key=lambda k: k[0])]

    ax.legend(handles=cpus_legend, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    ax.set_xlim(start_time, end_time)

    # Set title
    if title is not None:
        ax.set_title(title)

    # Adjust layout
    fig.tight_layout()

    return fig


def generate_job_execution_plot(task_set: TaskSet, jobs: List[Job], schedule_result: RawSimulationResult,
                                start_time: float = 0, end_time: Optional[float] = None,
                                title: Optional[str] = None) -> Figure:
    """
    Generate jobs execution plot
    :param task_set: Task set
    :param jobs: Jobs in the system
    :param schedule_result: Result of the simulation
    :param start_time: Plot start time in seconds
    :param end_time: Plot end time in seconds
    :param title: Plot title
    :return: plot
    """
    cpu_color_id: Dict[int, int] = {j: i for i, j in enumerate(schedule_result.job_sections_execution.keys())}

    color_palette = __obtain_color_palette(len(cpu_color_id))

    jobs_ids: List[int] = sorted([i.identification for i in jobs])

    jobs_to_lines_assignation: Dict[int, int] = {j: i for i, j in enumerate(jobs_ids)}

    fig, ax = pyplot.subplots()

    for cpu_id, sections_list in schedule_result.job_sections_execution.items():
        for section in sections_list:
            ax.barh(jobs_to_lines_assignation[section.job_id],
                    width=section.execution_end_time - section.execution_start_time,
                    left=section.execution_start_time,
                    color=color_palette[cpu_color_id[cpu_id]])

    ax.set_yticks(range(len(jobs_ids)))
    ax.set_yticklabels([f'Jobs {i}' for i in jobs_ids])

    cpus_legend = [patches.Patch(color=color_palette[j], label=f'CPU {i}') for i, j in
                   sorted(cpu_color_id.items(), key=lambda k: k[0])]

    ax.legend(handles=cpus_legend, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    end_time = end_time if end_time is not None else calculate_major_cycle(task_set)

    ax.set_xlim(start_time, end_time)

    # Set title
    if title is not None:
        ax.set_title(title)

    # Adjust layout
    fig.tight_layout()

    return fig
