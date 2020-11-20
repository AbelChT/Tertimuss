import json
import math
from typing import List, Tuple
import statistics

import scipy.stats


def run_anderson_darling(x) -> float:
    # Obtained from
    # https://stats.stackexchange.com/questions/350443/how-do-i-get-the-p-value-of-ad-test-using-the-results-of-scipy
    # -stats-anderson
    ad, crit, sig = scipy.stats.anderson(x, dist='norm')
    ad = ad * (1 + (.75 / 50) + 2.25 / (50 ** 2))
    if ad >= .6:
        p = math.exp(1.2937 - 5.709 * ad - .0186 * (ad ** 2))
    elif ad >= .34:
        p = math.exp(.9177 - 4.279 * ad - 1.38 * (ad ** 2))
    elif ad > .2:
        p = 1 - math.exp(-8.318 + 42.796 * ad - 59.938 * (ad ** 2))
    else:
        p = 1 - math.exp(-13.436 + 101.14 * ad - 223.73 * (ad ** 2))
    return p


def do_plots():
    tests_base_names: List[Tuple[str, str]] = [("out/2/8/", "2/8"),
                                               ("out/2/16/", "2/16"),
                                               ("out/2/24/", "2/24"),
                                               ("out/2/32/", "2/32"),
                                               ("out/2/40/", "2/40"),

                                               ("out/4/16/", "4/16"),
                                               ("out/4/32/", "4/32"),
                                               ("out/4/48/", "4/48"),
                                               ("out/4/64/", "4/64"),
                                               ("out/4/80/", "4/80"),
                                               ]
    scheduler_name = "run"

    number_of_tests = 200

    # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
    grouped_info: List[List[Tuple[int, int, int]]] = []

    for tests_base_name, _ in tests_base_names:
        # [CS ALG1, CS ALG2, CS MANDATORY, M ALG1, M ALG2]
        local_grouped_info: List[Tuple[int, int, int]] = []

        for i in range(number_of_tests):
            name = "test_" + str(i)
            try:
                save_path = tests_base_name
                simulation_name = name + "_"
                with open(save_path + simulation_name + scheduler_name + "_context_switch_statics.json",
                          "r") as read_file:
                    decoded_json = json.load(read_file)
                    scheduler_produced_context_switch_number_scheduler_1 = decoded_json["statics"][
                        "scheduler_produced_context_switch_number"]
                    mandatory_context_switch_number = decoded_json["statics"]["mandatory_context_switch_number"]
                    migrations_number_scheduler_1 = decoded_json["statics"]["migrations_number"]

                local_grouped_info.append((scheduler_produced_context_switch_number_scheduler_1,
                                           mandatory_context_switch_number,
                                           migrations_number_scheduler_1))
            except Exception as e:
                print("Has fail", name)
                pass
        grouped_info.append(local_grouped_info)

    # Algorithm CS / JOBS
    algorithm_cs_ratio = [[CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local] for
                          grouped_info_local in grouped_info]

    algorithm_cs_ratio_means = [
        statistics.mean([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_cs_ratio_stdev = [
        statistics.pstdev([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_cs_ratio_quantiles = [
        statistics.quantiles([CS_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    # Algorithm M / JOBS
    algorithm_m_ratio = [[M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local] for
                         grouped_info_local in grouped_info]

    algorithm_m_ratio_means = [
        statistics.mean([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_m_ratio_stdev = [
        statistics.pstdev([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    algorithm_m_ratio_quantiles = [
        statistics.quantiles([M_ALG1 / CS_MANDATORY for (CS_ALG1, CS_MANDATORY, M_ALG1) in grouped_info_local]) for
        grouped_info_local in grouped_info]

    print("Statistics for context switch and migrations mean by experiment", scheduler_name)

    for experiment_name, cs_ratio, cs_ratio_mean, cs_ratio_stdev, cs_ratio_quantiles, m_ratio, m_ratio_mean, \
        m_ratio_stdev, m_ratio_quantiles in zip([i[1] for i in tests_base_names], algorithm_cs_ratio,
                                                algorithm_cs_ratio_means, algorithm_cs_ratio_stdev,
                                                algorithm_cs_ratio_quantiles, algorithm_m_ratio,
                                                algorithm_m_ratio_means, algorithm_m_ratio_stdev,
                                                algorithm_m_ratio_quantiles):
        print("\t", experiment_name)
        print("\t\t Preemption mean by experiment mean:              ", cs_ratio_mean)
        print("\t\t Preemption mean by experiment standard deviation:", cs_ratio_stdev)
        print("\t\t Preemption mean by experiment quantiles:         ", cs_ratio_quantiles)
        print("\t\t Migrations mean by experiment mean:              ", m_ratio_mean)
        print("\t\t Migrations mean by experiment standard deviation:", m_ratio_stdev)
        print("\t\t Migrations mean by experiment quantiles:         ", m_ratio_quantiles)

        # Check normality of data
        alpha = 0.05

        # Preemptions
        print("\t\t Checking normality of data for preemptions")

        # Shapiro-Wilk
        stat, p = scipy.stats.shapiro(cs_ratio)
        print("\t\t\t Shapiro-Wilk Test: W =", stat, ", p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")

        # D’Agostino’s K^2
        stat, p = scipy.stats.normaltest(cs_ratio)
        print("\t\t\t D’Agostino’s K^2 Test: W =", stat, ", p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")

        # Anderson-Darling
        p = run_anderson_darling(cs_ratio)
        print("\t\t\t Anderson-Darling Test: p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")

        # Migrations
        print("\t\t Checking normality of data for migrations")

        # Shapiro-Wilk
        stat, p = scipy.stats.shapiro(m_ratio)
        print("\t\t\t Shapiro-Wilk Test: W =", stat, ", p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")

        # D’Agostino’s K^2
        stat, p = scipy.stats.normaltest(m_ratio)
        print("\t\t\t D’Agostino’s K^2 Test: W =", stat, ", p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")

        # Anderson-Darling
        p = run_anderson_darling(m_ratio)
        print("\t\t\t Anderson-Darling Test: p =", p, ",",
              "(fail to reject H0)" if p > alpha else "(reject H0)")


if __name__ == '__main__':
    do_plots()
