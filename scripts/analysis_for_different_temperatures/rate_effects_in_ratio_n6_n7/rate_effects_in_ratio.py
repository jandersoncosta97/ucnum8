import matplotlib.pyplot as plt
import pandas as pd
from statistics import median
import os
from pathlib import Path
import numpy as np
import sys

class RatioRateConstants:

    def __init__(self, n):
        self.n = n
        if n < 10:
            self.k12 = f'0.{n}'
        elif n == 10:
            self.k12 = '1.0'
        else:
            sys.exit()
        self.temperatures = list(range(290, 361, 10))
        self.et_filepaths = {}
        self.filepaths = {}
        for temp in self.temperatures:
            self.et_filepaths[f'{temp}K, simulation_{n}'] = Path.cwd().as_posix() + f'/analysis/analysis_for_different_temperatures/T_{temp}K/pump_power_01_1/simulation_{n}/ET.INP'
        self.pop_names_to_plot = ['pop6', 'pop7']
        for temp in self.temperatures:
            self.filepaths[f'{temp}K, simulation_{n}'] = Path.cwd().as_posix() + f'/analysis/analysis_for_different_temperatures/T_{temp}K/pump_power_01_1/simulation_{n}'


    def get_values_of_rate_constants(self):
        values_k63 = {}
        values_k65 = {}
        values_k67 = {}
        for key, filepath in self.et_filepaths.items():
            with open(filepath, 'r', encoding='utf_8') as f:
                for line in f:
                    if 'k63' in line:
                        values_k63[f'{key} - k63'] = float(line.split()[0])
                    elif 'k65' in line:
                        values_k65[f'{key} - k65'] = float(line.split()[0])
                    elif 'k67' in line:
                        values_k67[f'{key} - k67'] = float(line.split()[0])
        return values_k63, values_k65, values_k67

    def calculate_ratios(self):
        values_k63, values_k65, values_k67 = self.get_values_of_rate_constants()
        ratios = []
        for k63, k65, k67 in zip(values_k63.values(), values_k65.values(),
                                 values_k67.values()):
            ratios.append((k67/(k65+k63)))
        return ratios

    def get_arrays(self):
        arrays = {}
        for path in self.filepaths.values():
            for pop in self.pop_names_to_plot:
                df = pd.read_csv(f'{path}/{pop}', sep='\s+', header=None,
                                 dtype=np.float64)
                arrays[f'{path}/{pop}'] = df.to_numpy()
        return arrays

    def get_values_at_stationary_state(self, pop_name, get_arrays):
        
        values = {}
        value_population = None
        for path, value in get_arrays.items():
            aux = True
            if pop_name in path:
                for time, value_population in value:
                    if time > 0.006 and aux:
                        values[path] = value_population
                        aux = False
        return values

    def get_ratios_n6_n7(self, *dict_pop_files_to_plot):
        values_n6 = dict_pop_files_to_plot[0]
        values_n7 = dict_pop_files_to_plot[1]
        
        ratios_n6_n7 = []
        
        for n6, n7 in zip(values_n6.values(), values_n7.values()):
            ratios_n6_n7.append(n6/n7)

        return ratios_n6_n7

    def plot(self, ratios_1, ratios_2):

        path_to_save_graphs = Path(f'{os.getcwd()}/outputs/analysis_for_different_temperatures/rate_effects_in_ratio_n6_n7')
        path_to_save_graphs.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots(figsize=(8.0, 6.5))
        plt.scatter(ratios_1, ratios_2)
        for i, T in enumerate(list(range(290, 361, 10))):
            plt.annotate(f'{T} K', xy=(ratios_1[i], ratios_2[i]), xytext=(ratios_1[i]-0.8, ratios_2[i]+0.3))
        plt.text(0.5, 0.9, f"k12 = {self.k12}", ha='center', transform=ax.transAxes, bbox=dict(facecolor='brown', alpha=0.5))
        plt.xlabel(r'$\frac{{k_{67}}}{{k_{65}}+k_{63}}$', fontname='Times New Roman', fontsize=15)
        plt.ylabel(r'$\frac{n_6}{n_7}$', fontname='Times New Roman', fontsize=15, rotation=0, labelpad=15)
        plt.savefig(f'{path_to_save_graphs}/k12_{self.k12.replace(".", "_")}.png')
