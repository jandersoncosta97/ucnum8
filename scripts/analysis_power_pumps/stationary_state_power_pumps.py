import pandas as pd
import numpy as np
import os
from pathlib import Path
from matplotlib import pyplot as plt


class StationaryStatePowerPumps:

    def __init__(self, path):
        self.path = path
        if '10_100' in self.path:
            self.k12 = list(range(10, 110, 10))
            self.range_k12 = '10_100'
        elif '1_10' in self.path:
            self.k12 = list(range(1, 11))
            self.range_k12 = '1_10'
        elif '01_1' in self.path:
            self.k12 = []
            self.range_k12 = '01_1'
            for i in range(1, 11):
                self.k12.append(round(0.1*i, 2))
        else:
            raise ValueError("Invalid path. Path should contain '10_100', '1_10', or '01_1'.")

    def get_arrays_pop_k12(self):
        array = {}
        array_list = []
        folders = os.listdir(self.path)
        folders = sorted(folders, key=lambda x: int(x.split('_')[-1]))
        for folder in folders:
            path = os.path.join(self.path, folder).replace('\\', '/')
            for pop in [f'pop{i}' for i in range(1, 9)]:
                array_list.append(pd.read_csv(f'{path}/{pop}', sep=r'\s+', header=None, dtype=np.float64, engine='python').to_numpy())
            array[folder] = array_list
            array_list = []
        return array


    def get_values_at_stationary_state(self, array):

        values_at_stationary_state = {}

        for simulation, array_list in array.items():

            value_population = {}

            for pop, arr in zip([f'pop{i}' for i in range(1, 9)], array_list):

                count = 0
                aux = True
                while count < len(arr) and aux:
                    value_time = arr[count][0]

                    if value_time > 0.004:
                        
                        value_population[pop] = np.median(arr[count:count+10, 1])
                        aux = False

                    count += 1

            values_at_stationary_state[simulation] = value_population

        return values_at_stationary_state
    
    def order_values(self, values_at_stationary_state):
        values_pop1 = []
        values_pop2 = []
        values_pop3 = []
        values_pop4 = []
        values_pop5 = []
        values_pop6 = []
        values_pop7 = []
        values_pop8 = []
        for value in values_at_stationary_state.values():
            for key2, value2 in value.items():
                if key2 == 'pop1':
                    values_pop1.append(value2)
                elif key2 == 'pop2':
                    values_pop2.append(value2)
                elif key2 == 'pop3':
                    values_pop3.append(value2)
                elif key2 == 'pop4':
                    values_pop4.append(value2)
                elif key2 == 'pop5':
                    values_pop5.append(value2)
                elif key2 == 'pop6':
                    values_pop6.append(value2)
                elif key2 == 'pop7':
                    values_pop7.append(value2)
                elif key2 == 'pop8':
                    values_pop8.append(value2)
                else:                    
                    raise ValueError("Invalid population. Population should be 'pop1', 'pop2', 'pop3', 'pop4', 'pop5', 'pop6', 'pop7', or 'pop8'.")
        return values_pop1, values_pop2

    def get_ratio(self, ordered_values):
        ratio_pop = []
        ratio_pop_dict = {}
        for i in range(len(ordered_values)):
            for value in ordered_values[i]:
                ratio_pop.append(value/ordered_values[i][0])
            ratio_pop_dict[i] = ratio_pop
            ratio_pop = []

        return ratio_pop_dict
        
    def plot_curves(self, ratio_pop_dict):
        path_to_save = f"{os.getcwd()}/outputs/power_pumps_{self.range_k12}/population_stationary_states_versus_k12"
        
        plt.figure(figsize=(10, 6))

        for i, label in zip([0, 1], ['pop1', 'pop2']):
            plt.plot(self.k12, ratio_pop_dict[i], marker='o', label=f'{label}')

        plt.xlabel('k12 (s-1)', fontsize=14)
        plt.ylabel('pop(k12)/pop(k12=10)', fontsize=14)

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

        plt.legend(fontsize=11)
        plt.grid(True, linestyle='--', alpha=0.5)

        plt.savefig(f'{path_to_save}/ratios_stationary_states_k12_{self.range_k12}_simulations_v5.png')
        print(f"plotted - {path_to_save}/ratios_stationary_states_k12_{self.range_k12}_simulations_v5.png")
