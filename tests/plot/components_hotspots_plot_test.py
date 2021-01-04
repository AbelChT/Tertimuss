import unittest

from tertimuss.plot_generator._component_hotspots_plot import generate_component_hotspots_plot
from tests.plot._generate_simulation_result import get_simulation_result


class ComponentsHotspotsPlotTest(unittest.TestCase):
    @unittest.skip("Manual visualization test")
    def test_component_hotspots_plot(self):
        tasks, _, simulation_result = get_simulation_result()

        fig = generate_component_hotspots_plot(schedule_result=simulation_result, title="Components hotspots")
        fig.show()
