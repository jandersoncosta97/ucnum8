import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from copy import deepcopy
import sys
from utils.modify_characters import ModifyCharacters
from utils.list_dirs import ListDirs
from utils.run_fortran import RunFortran
import matplotlib.cm as cm

class ProcessTemporalCurvesTemperatureRange:
    
    def __init__(self):
        self.pop_names = ['pop1','pop2','pop3','pop4','pop5','pop6','pop7','pop8']
        self.temps = [290, 300, 310, 320, 330, 340, 350, 360]
        cwd_path = os.getcwd().replace('\\', '/')
        self.modify_characters = ModifyCharacters()
        self.list_dirs = ListDirs()
        self.runfortran = RunFortran()
        self.paths = {}
        for temp in self.temps:
            self.paths[temp] = f"{cwd_path}/analysis/analysis_for_different_temperatures/T_{temp}K/pump_power_01_1"
        self.__selected_temp = None
        self.dict_paths_arqs_pop = {}
        self.simulation_folders = [None]*10

    def choose_temperature(self):
        choice = input("Choose a temperature (290, 300, 310, 320, 330, 340, 350, 360), q to quit: ")
        while choice not in [str(temp) for temp in self.temps] + ['q']: 
            choice = input("Invalid option! Choose a temperature (290, 300, 310, 320, 330, 340, 350, 360), q to quit: ")
        if choice == 'q':
            sys.exit()
        elif choice.isdigit() and int(choice) in self.temps:
            self.__selected_temp = int(choice)
            return self.__selected_temp

    def edit_et_files(self):
        print("Editing ET files...")
        pump_power = '0.1'
        for simulation_folder in self.simulation_folders:
            path_on_simulation_folder = os.path.join(self.paths[self.__selected_temp], simulation_folder).replace('\\', '/')
            self.modify_characters.modify_non_decay_rates_parameters_in_ET_INP(path_on_simulation_folder, 'k12', pump_power)
            pump_power = str(round(float(pump_power) + 0.1, 1))

    def select_folders(self):
        # Placeholder for selecting folders
        i1 = 0
        choice = self.choose_temperature()
        for simulation_folder in os.listdir(self.paths[choice]):
            if not os.path.isfile(os.path.join(self.paths[choice], simulation_folder).replace('\\', '/')):
                self.simulation_folders[i1] = simulation_folder
                i1 += 1

    def order_folders(self):
        # Placeholder for ordering self.simulation_folders
        self.simulation_folders = sorted(self.simulation_folders, key=lambda x: int(x.split('simulation_')[1]))

    def get_paths_pop_files(self):
        print("Getting paths of population files...")
        # Placeholder for getting paths to population files
        dict_internal = {}
        dict_middle = {}

        for path, temp in zip(self.paths.values(), self.temps):
            for simulation_folder in self.simulation_folders:
                for folder_arq in os.listdir(os.path.join(path, simulation_folder).replace('\\', '/')):
                    if folder_arq in ['pop1','pop2','pop3','pop4','pop5','pop6','pop7','pop8']:
                        pop_file = folder_arq
                        dict_internal[pop_file] = os.path.join(path, simulation_folder, pop_file).replace('\\', '/')
                dict_middle[simulation_folder] = dict_internal
                dict_internal = {}
            self.dict_paths_arqs_pop[temp] = dict_middle 
            dict_middle = {}
            
    def run_fortran(self):
        for simulation_folder in self.simulation_folders:
            path_dir_files = os.path.join(self.paths[self.__selected_temp], simulation_folder).replace('\\', '/')
            self.runfortran.run_fortran(path_dir_files)

    def convert_format_pop_files(self):
        for simulation_folder in self.simulation_folders:
            for pop_name in self.pop_names:
                pop_file_path = self.dict_paths_arqs_pop[self.__selected_temp][simulation_folder][pop_name]
                self.modify_characters.convert_format_scientific_notation(pop_file_path, 'D', 'E')
                self.modify_characters.modify_first_character_pop_file(pop_file_path, '0.0000000E+00')
    
    def get_dataframes(self):
        print("Working on the DataFrames...")
        dict_df = {}
        dict_df_internal = {}
        dict_df_middle = {}
        dict_df_populations = {}
        dict_df_internal_populations = {}
        dict_df_middle_populations = {}
        dict_df_time = {}
        dict_df_internal_time = {}
        dict_df_middle_time = {}
        for key1, value1 in self.dict_paths_arqs_pop.items():
            for key2, value2 in value1.items():
                for key3, value3 in value2.items():
                    dict_df_internal[key3] = pd.read_csv(f'{value3}', sep='\s+', header=None, dtype=np.float64, engine='python').to_numpy()                
                    dict_df_internal_populations[key3] = deepcopy(dict_df_internal[key3][:,1])
                    dict_df_internal_time[key3] = deepcopy(dict_df_internal[key3][:,0])
                dict_df_middle[key2] = dict_df_internal
                dict_df_middle_populations[key2] = deepcopy(dict_df_internal_populations)
                dict_df_middle_time[key2] = deepcopy(dict_df_internal_time)
                dict_df_internal = {}
                dict_df_internal_populations = {}
                dict_df_internal_time = {}
            dict_df[key1] = dict_df_middle
            dict_df_populations[key1] = deepcopy(dict_df_middle_populations)
            dict_df_time[key1] = deepcopy(dict_df_middle_time)
            dict_df_middle = {}
            dict_df_middle_populations = {}
            dict_df_middle_time = {}

        return dict_df_populations, dict_df_time


    def plot_temporal_curves(self):

        csv_data_pop_data, csv_data_time_data = self.get_dataframes()

        if isinstance(self.__selected_temp, int):
            for pop_name in self.pop_names:
                paths_to_save_graphs = f"outputs/analysis_for_different_temperatures/T_{self.__selected_temp}K/population_curves"
                os.makedirs(paths_to_save_graphs, exist_ok=True)

                fig, ax = plt.subplots(figsize=(8.0, 4.8))

                n = len(self.simulation_folders)
                colors = cm.get_cmap('tab10', n)

                for i, simulation_folder in enumerate(self.simulation_folders):
                    k12_value = round(0.1 + i * 0.1, 1)
                    label = f'{pop_name} (k12 = {k12_value})'
                    
                    time = csv_data_time_data[self.__selected_temp][simulation_folder][pop_name]
                    data = csv_data_pop_data[self.__selected_temp][simulation_folder][pop_name]
                    
                    ax.plot(time, data, label=label, color=colors(i), marker='o', ms=2, mec=colors(i), mfc=colors(i))

                ax.legend(loc='center right', prop={"size": 10, 'family': 'Times New Roman'})
                ax.set_xlabel('Time', fontsize=11.5, fontname="Times New Roman", weight='semibold')
                ax.set_ylabel('Population', fontsize=11.5, fontname="Times New Roman", weight='semibold')
                ax.grid(alpha=0.4, ls=':')

                fig.savefig(f'{paths_to_save_graphs}/{pop_name}_k12_01_to_1.png')
                plt.close(fig)
                print(f'PLOT: analysis_for_different_temperatures -> {pop_name} - k12_01_to_1')

