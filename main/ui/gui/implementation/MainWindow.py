from PyQt5.QtWidgets import QFileDialog, QDialog

from main.ui.common.JSONGlobalModelParser import JSONGlobalModelParser
from main.ui.common.SchedulerSelector import SchedulerSelector
from main.ui.common.TCPNThermalModelSelector import TCPNThermalModelSelector
from main.ui.common.TaskGeneratorSelector import TaskGeneratorSelector
from main.ui.gui.implementation.AddAutomaticTaskDialog import AddAutomaticTaskDialog
from main.ui.gui.implementation.AddFrequencyDialog import AddFrequencyDialog
from main.ui.gui.implementation.AddOriginDialog import AddOriginDialog
from main.ui.gui.implementation.AddOutputDialog import AddOutputDialog
from main.ui.gui.implementation.AddTaskDialog import AddTaskDialog
from main.ui.gui.ui_specification.implementation.gui_add_task_design import Ui_DialogAddTask
from main.ui.gui.ui_specification.implementation.gui_main_desing import *


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        # Energy generation model
        tcpn_model_names = TCPNThermalModelSelector.get_tcpn_model_names()

        for i in range(len(tcpn_model_names)):
            self.comboBox_simulation_energy_model.addItem("")
            self.comboBox_simulation_energy_model.setItemText(i, tcpn_model_names[i])

        # Available schedulers
        scheduler_names = SchedulerSelector.get_scheduler_names()

        for i in range(len(scheduler_names)):
            self.comboBox_scheduler_select.addItem("")
            self.comboBox_scheduler_select.setItemText(i, scheduler_names[i])

        # TODO: Delete
        self.__load_json_input("tests/cli/input-example-thermal-aperiodics-energy.json")

    def simulate_thermal_state_changed(self, state: bool):
        print("State changed")
        # Control thermal enabled/disabled
        self.doubleSpinBox_simulation_mesh_step.setEnabled(state)
        self.comboBox_simulation_energy_model.setEnabled(state)
        self.tab_environment.setEnabled(state)
        self.tab_board.setEnabled(state)
        self.tab_cpu_cores_physical.setEnabled(state)
        self.tab_cpu_cores_origins.setEnabled(state)
        self.tab_cpu_cores_energy.setEnabled(state)
        self.checkBox_cpu_cores_automatic_origins.setEnabled(state)

    def load_json(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load specification", "", "JSON (*.json)",
                                                   options=options)
        if file_name:
            self.__load_json_input(file_name)

    def __load_json_input(self, path: str):
        # Path of the input validate schema
        # Warning: In python paths are relative to the entry point script path
        input_schema_path = './main/ui/cli/input_schema/input-schema.json'

        # Read schema
        error, message, schema_object = JSONGlobalModelParser.read_input(input_schema_path)

        if error:
            self.label_status.setText(message)

        # Read input
        error, message, input_object = JSONGlobalModelParser.read_input(path)

        if error:
            self.label_status.setText(message)

        # Validate schema
        error, message = JSONGlobalModelParser.validate_input(input_object, schema_object)

        if error:
            self.label_status.setText(message)

        # Fill fields
        if input_object["simulate_thermal"]:
            # Fill simulation tab fields
            self.checkBox_simulation_thermal.setChecked(True)

            tcpn_model_names = TCPNThermalModelSelector.get_tcpn_model_names()

            self.comboBox_simulation_energy_model.setCurrentIndex(
                tcpn_model_names.index(input_object["tasks_specification"]["task_consumption_model"]))

            self.doubleSpinBox_simulation_mesh_step.setValue(input_object["simulation_specification"]["mesh_step"])

            self.doubleSpinBox_simulation_accuracy.setValue(input_object["simulation_specification"]["dt"])

        else:
            self.checkBox_simulation_thermal.setChecked(False)

        # Fill tasks tab fields
        if input_object["tasks_specification"]["task_generation_system"] == "Manual":
            tasks = input_object["tasks_specification"]["tasks"]
            for i in range(len(tasks)):
                new_row = [tasks[i]["type"],
                           tasks[i]["worst_case_execution_time"],
                           tasks[i].get("arrive"),
                           tasks[i].get("period") if tasks[i]["type"] == "Periodic" else tasks[i].get("deadline"),
                           tasks[i].get("energy_consumption")
                           ]
                self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, new_row)

        # Fill CPU tab fields
        # Fill core tab fields
        for i in input_object["cpu_specification"]["cores_specification"]["available_frequencies"]:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_available_frequencies, [i])

        for i in input_object["cpu_specification"]["cores_specification"]["cores_frequencies"]:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_selected_frequencies, [i])

        if input_object["simulate_thermal"]:
            automatic_origins = input_object["cpu_specification"]["cores_specification"]["cores_origins"] == "Automatic"
            self.checkBox_cpu_cores_automatic_origins.setChecked(automatic_origins)
            if not automatic_origins:
                for i in input_object["cpu_specification"]["cores_specification"]["cores_origins"]:
                    self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_origins_list, [i["x"], i["y"]])

            # Fill energy tab
            self.doubleSpinBox_cpu_cores_energy_dynamic_alpha.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "dynamic_alpha"])

            self.doubleSpinBox_cpu_cores_energy_dynamic_beta.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "dynamic_beta"])

            self.doubleSpinBox_cpu_cores_energy_leakage_alpha.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "leakage_alpha"])

            self.doubleSpinBox_cpu_cores_energy_leakage_delta.setValue(
                input_object["cpu_specification"]["cores_specification"]["energy_consumption_properties"][
                    "leakage_delta"])

            # Fill physical tab
            self.doubleSpinBox_cpu_cores_physical_x.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["x"])

            self.doubleSpinBox_cpu_cores_physical_y.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["y"])

            self.doubleSpinBox_cpu_cores_physical_z.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["z"])

            self.doubleSpinBox_cpu_cores_physical_p.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["density"])

            self.doubleSpinBox_cpu_cores_physical_c_p.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"][
                    "specific_heat_capacity"])

            self.doubleSpinBox_cpu_cores_physical_k.setValue(
                input_object["cpu_specification"]["cores_specification"]["physical_properties"]["thermal_conductivity"])

            # Fill board tab fields
            # Fill physical tab
            self.doubleSpinBox_cpu_board_physical_x.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["x"])

            self.doubleSpinBox_cpu_board_physical_y.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["y"])

            self.doubleSpinBox_cpu_board_physical_z.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["z"])

            self.doubleSpinBox_cpu_board_physical_p.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["density"])

            self.doubleSpinBox_cpu_board_physical_c_p.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"][
                    "specific_heat_capacity"])

            self.doubleSpinBox_cpu_board_physical_k.setValue(
                input_object["cpu_specification"]["board_specification"]["physical_properties"]["thermal_conductivity"])

        # Fill environment tab fields
        if input_object["simulate_thermal"]:
            self.doubleSpinBox_environment_env_temperature.setValue(
                input_object["environment_specification"]["environment_temperature"])
            self.doubleSpinBox_environment_max_temperature.setValue(
                input_object["environment_specification"]["maximum_temperature"])
            self.doubleSpinBox_environment_convection_factor.setValue(
                input_object["environment_specification"]["convection_factor"])

        # Fill scheduler tab fields
        scheduler_names = SchedulerSelector.get_scheduler_names()

        self.comboBox_scheduler_select.setCurrentIndex(
            scheduler_names.index(input_object["scheduler_specification"]["name"]))

        # Fill output tab fields
        self.label_output_path.setText(input_object["output_specification"]["output_path"])
        self.lineEdit_output_base_naming.setText(input_object["output_specification"]["output_naming"])
        for i in input_object["output_specification"]["selected_output"]:
            self.__add_new_row_to_table_widget(self.tableWidget_output_selected_drawers, [i])

    @staticmethod
    def __add_new_row_to_table_widget(table_widget: QtWidgets.QTableWidget, new_row: list):
        """
        Add row to table widget
        :param table_widget: Table widget where add the row
        :param new_row: New row with Nones in empty columns
        """
        actual_size = table_widget.rowCount()
        table_widget.setRowCount(actual_size + 1)

        for i in range(len(new_row)):
            if new_row[i] is not None:
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(new_row[i]))
                table_widget.setItem(actual_size, i, item)

    @staticmethod
    def __delete_selected_row_from_table_widget(table_widget: QtWidgets.QTableWidget):
        """
        Delete the selected row from the table widget
        :param table_widget: Table widget where add the row
        """
        current_selected_row = table_widget.currentRow()
        if current_selected_row != -1:
            table_widget.removeRow(current_selected_row)

    @staticmethod
    def __check_duplicated_row_from_table_widget(table_widget: QtWidgets.QTableWidget, value_to_search: str) -> bool:
        """
        Check if the value value_to_search is in the table table_widget
        :param table_widget: Table widget where add the row
        """
        item_list = []
        for i in range(table_widget.rowCount()):
            item = table_widget.item(i, 0)
            item_list.append(item.text())
        return any([i == value_to_search for i in item_list])

    def start_simulation(self):
        # TODO: Save as JSON
        # TODO: Use the JSON in the same way as CLI
        print("start_simulation")

    def add_task(self):
        is_thermal_enabled = self.checkBox_simulation_thermal.isChecked()
        is_energy_enabled = self.comboBox_simulation_energy_model.currentText() == "Energy based"
        dialog_ui = AddTaskDialog(is_thermal_enabled, is_energy_enabled, self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, return_value)

    def delete_task(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_tasks_list)

    def generate_automatic_tasks(self):
        dialog_ui = AddAutomaticTaskDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and return_value[0] < return_value[1]:
            period_start = return_value[0]
            period_end = return_value[1]
            number_of_tasks = return_value[2]
            utilization = return_value[3]
            algorithm_name = return_value[4]
            generator_algorithm = TaskGeneratorSelector.select_task_generator(algorithm_name)

            tasks = generator_algorithm.generate({
                "number_of_tasks": number_of_tasks,
                "utilization": utilization,
                "min_period_interval": period_start,
                "max_period_interval": period_end,
                "processor_frequency": 1
            })

            for task in tasks:
                self.__add_new_row_to_table_widget(self.tableWidget_tasks_list, [task.c, None, task.d, task.e])

    def add_origin(self):
        dialog_ui = AddOriginDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_origins_list, return_value)

    def delete_origin(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_origins_list)

    def add_available_frequency(self):
        dialog_ui = AddFrequencyDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and not self.__check_duplicated_row_from_table_widget(
                self.tableWidget_cpu_cores_available_frequencies, str(return_value[0])):
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_available_frequencies, return_value)

    def delete_available_frequency(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_available_frequencies)

    def add_selected_frequency(self):
        dialog_ui = AddFrequencyDialog(self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None:
            self.__add_new_row_to_table_widget(self.tableWidget_cpu_cores_selected_frequencies, return_value)

    def delete_selected_frequency(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_cpu_cores_selected_frequencies)

    def add_output(self):
        is_thermal_enabled = self.checkBox_simulation_thermal.isChecked()
        dialog_ui = AddOutputDialog(is_thermal_enabled, self)
        dialog_ui.exec()
        return_value = dialog_ui.get_return_value()
        if return_value is not None and not self.__check_duplicated_row_from_table_widget(
                self.tableWidget_output_selected_drawers, str(return_value[0])):
            self.__add_new_row_to_table_widget(self.tableWidget_output_selected_drawers, return_value)
            self.tableWidget_output_selected_drawers.sortItems(0)

    def delete_output(self):
        self.__delete_selected_row_from_table_widget(self.tableWidget_output_selected_drawers)

    def generate_automatic_origins_changed(self, state: bool):
        # Control automatic origins enabled/disabled
        self.tab_cpu_cores_origins.setEnabled(not state)

    def change_output_path(self):
        options = QFileDialog.Options()

        file_name = QFileDialog.getExistingDirectory(self, "Output path")

        print(file_name)

        # TODO: Open browser to search output
        print("change_output_path")
