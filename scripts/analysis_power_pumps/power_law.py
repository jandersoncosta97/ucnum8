import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from math import log
import os
import subprocess
from pathlib import Path


class PowerLawAnalysis:

    def __init__(self, directory: str):
        self.__directory = directory
        self.origin_cwd = os.getcwd()
        self.folders = sorted(self.choose_folders().keys(), key=lambda x: int(x.split('_')[-1]))
        self.pop_names = [f'pop{i}' for i in range(1, 9)]
        if 'k12_01_1' in self.__directory:
            self.k12 = []
            for i in range(1, 11):
                self.k12.append(f'{str(i/10)}')
        if 'k12_1_10' in self.__directory:
            self.k12 = []
            for i in range(1, 11):
                self.k12.append(f'{str(i)}.0')
        if 'k12_10_100' in self.__directory:
            self.k12 = []
            for i in range(1, 11):
                self.k12.append(f'{str(i*10)}.0')
        self.population_file_paths = self.return_population_file_paths()
        self.log_values_n5 = []
        self.log_values_n6 = []
        self.log_values_n7 = []
        self.log_k12 = []
    
    def choose_folders(self):
        simulation_folders = {}
        for path in os.listdir(self.__directory):
            simulation_folders[path] = os.path.join(self.__directory, path)
        return simulation_folders

    def run_fortran_files(self):
        conda_env = 'ucnum8'
        name_input_file = 'ucnum8.f'
        name_output_file = 'ucnum8'

        compile_command = f"conda run -n {conda_env} gfortran {
            name_input_file} -o {name_output_file}"
        try:
            subprocess.run(compile_command, shell=True, check=True)
            print(f"Compiled {name_input_file} successfully to {
                name_output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}")
            exit(1)

        # Execute the compiled program
        execute_command = f"{name_output_file}"
        try:
            subprocess.run(execute_command, shell=True, check=True)
            print(f"Executed {name_output_file} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")

    def select_ucnum8_to_run(self):
        for folder in os.listdir(self.__directory):
            os.chdir(os.path.join(self.__directory, folder).replace('\\', '/'))
            self.run_fortran_files()
        os.chdir(self.origin_cwd)

    def convert_numbers_to_float(self, arq):
        with open(arq, 'r', encoding='utf_8') as f1:
            lines = f1.readlines()
        if lines:
            lines[0] = '     0.0000000E+00  ' + ' '.join(lines[0].split()[1:]) + '\n'
        with open(arq, 'w', encoding='utf_8') as f2:
            f2.writelines(lines)

    def convert_format_scientific_notation(self, path, character='D', new_character='E'):
        with open(path, 'r', encoding = 'utf_8') as f:
            content = f.read()
            modified_content = content.replace(character, new_character)
        with open(path, 'w', encoding = 'utf_8') as f:
            f.write(modified_content)
        print(f'SCIENTIFIC NOTATION CHANGED (D -> E)! {Path(path).name}')

    def return_population_file_paths(self):
        internal_all_pop = {}
        paths_arqs_pop = {}

        for folder in self.folders:
            for arq in os.listdir(os.path.join(self.__directory, folder)):
                if arq in self.pop_names:
                    internal_all_pop[arq] = os.path.join(os.path.join(
                        self.__directory, folder), arq).replace('\\', '/')

            paths_arqs_pop[folder] = internal_all_pop

            internal_all_pop = {}

        return paths_arqs_pop

    def run_converter(self):
        for pops_paths in self.population_file_paths.values():
            for path_name in pops_paths.values():
                self.convert_format_scientific_notation(path_name, 'D', 'E')
                self.convert_numbers_to_float(arq=path_name)
                
    def order_path(self):
        simulation_10 = self.population_file_paths.pop('simulation_10')
        self.population_file_paths['simulation_10'] = simulation_10
        return self.population_file_paths  

    def get_et_file_paths(self):
        et_file_paths = {}
        for folder in self.folders:
            et_file_paths[folder] = os.path.join(self.__directory, folder, 'ET.INP').replace('\\', '/')
        return et_file_paths

    def edit_power_pumps(self):
        et_file_paths = self.get_et_file_paths()
        for k12, path in zip(self.k12, et_file_paths.values()):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.readlines()
            modified_content = ''
            for line in content:
                if 'k12' in line:
                    new_line = line.replace(line.split()[0], k12)
                    modified_content += new_line
                else:
                    modified_content += line
            with open(path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

    
    def get_dataframes(self):
        dict_populations_time = {}
        dict_populations_time_temporary = {}
        for folder in self.folders:
            for pop in ['pop5', 'pop6', 'pop7']:
                dict_populations_time_temporary[pop] = pd.read_csv(f'{
                    self.population_file_paths[folder][pop]}', sep=r'\s+',
                    header=None, dtype=np.float64, engine='python').to_numpy()
            dict_populations_time[folder] = dict_populations_time_temporary
            dict_populations_time_temporary = {}
        return dict_populations_time


    def values_at_stationary_state(self, pop_name, get_dataframes):
        dict_populations_time_ = get_dataframes
        count = 0
        static_values = {}
        value_population = None
        for simulation, value1 in dict_populations_time_.items():
            for pop, array in value1.items():
                aux = True
                if pop == pop_name:
                    while count < len(array) and aux:
                        value_time = array[count][0]
                        if value_time > 0.004:
                            value_population = np.median(array[count:count+5, 1])  
                            aux = False
                        else:
                            count += 1
                    static_values[simulation] = value_population
        return static_values

    def get_values_stationary_state_population(self):
        dataframes = self.get_dataframes()
        values_n5 = self.values_at_stationary_state('pop5', dataframes)
        values_n6 = self.values_at_stationary_state('pop6', dataframes)
        values_n7 = self.values_at_stationary_state('pop7', dataframes)
        return values_n5, values_n6, values_n7

    def apply_model(self):
        values_n5, values_n6, values_n7 = self.get_values_stationary_state_population()

        for value in values_n5.values():
            self.log_values_n5.append(log(value, 10))
        for value in values_n6.values():
            self.log_values_n6.append(log(value, 10))
        for value in values_n7.values():
            self.log_values_n7.append(log(value, 10))
        for k12 in self.k12:
            self.log_k12.append(log(float(k12), 10))
        x = np.array(self.log_k12).reshape((-1, 1))

        y_n5 = np.array(self.log_values_n5)
        y_n6 = np.array(self.log_values_n6)
        y_n7 = np.array(self.log_values_n7)

        model_n5 = LinearRegression().fit(x, y_n5)
        model_n6 = LinearRegression().fit(x, y_n6)
        model_n7 = LinearRegression().fit(x, y_n7)

        return model_n5, model_n6, model_n7, x, y_n5, y_n6, y_n7

    def plot(self):
        k12_press = None
        model_n5, model_n6, model_n7, x, y_n5, y_n6, y_n7 = self.apply_model()

        if 'k12_1_10' in self.__directory:
            k12_press = [f'{i}.0' for i in range(1, 11)]
            path_graphs = os.getcwd()+'/outputs/power_pumps_1_10/power_law'
        if 'k12_01_1' in self.__directory:
            path_graphs = os.getcwd()+'/outputs/power_pumps_01_1/power_law'
            k12_press = [f'0.{i}' for i in range(1, 10)]
            k12_press.append('1.0')
        if 'k12_10_100' in self.__directory:
            path_graphs = os.getcwd()+'/outputs/power_pumps_10_100/power_law'
            k12_press = [f'{i}0.0' for i in range(1, 11)]
            
        os.makedirs(path_graphs, exist_ok=True)

        print('Plotting - Power Law for emission of level 5')
        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        plt.plot(self.log_k12, self.log_values_n5, color='#FF002B', label=f'Simulation t = 0.005 s\nk12 = {k12_press}', marker='o', ms=5, mec='#FF002B', mfc='#FF002B')
        plt.legend(loc='best', prop={'size': 10, 'family': 'Times New Roman'})
        plt.xlabel('log(k12)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.ylabel('log(n5)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.grid(alpha=0.4, ls=':')
        plt.text(0.28, 0.60, f"log(n5) = {float(model_n5.intercept_):,.5f} + {float(model_n5.coef_):,.5f}.log(k12)\nR² = {float(model_n5.score(x, y_n5)):,.5f}", ha='center', fontsize=11, fontname='Times New Roman', transform=ax.transAxes)
        plt.savefig(f'{path_graphs}/power_law_simulation_n5.png')
        print(f'Graph saved at: {path_graphs}/power_law_simulation_n5.png')

        print('Plotting - Power Law for emission of level 6')
        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        plt.plot(self.log_k12, self.log_values_n6, color='#32CD32', label=f'Simulation t = 0.005 s\nk12 = {k12_press}', marker='o', ms=5, mec='#32CD32', mfc='#32CD32')
        plt.legend(loc='best', prop={'size': 10, 'family': 'Times New Roman'})
        plt.xlabel('log(k12)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.ylabel('log(n6)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.grid(alpha=0.4, ls=':')
        plt.text(0.28, 0.60, f"log(n6) = {float(model_n6.intercept_):,.5f} + {float(model_n6.coef_):,.5f}.log(k12)\nR² = {float(model_n6.score(x, y_n6)):,.5f}", ha='center', fontsize=11, fontname='Times New Roman', transform=ax.transAxes)
        plt.savefig(f'{path_graphs}/power_law_simulation_n6.png')
        print(f'Graph saved at: {path_graphs}/power_law_simulation_n6.png')

        print('Plotting - Power Law for emission of level 7')
        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        plt.plot(self.log_k12, self.log_values_n7, color='#008000', label=f'Simulation t = 0.005 s\nk12 = {k12_press}', marker='o', ms=5, mec='#008000', mfc='#008000')
        plt.legend(loc='best', prop={'size': 10, 'family': 'Times New Roman'})
        plt.xlabel('log(k12)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.ylabel('log(n7)', fontsize=10, fontname='Times New Roman', weight='semibold')
        plt.grid(alpha=0.4, ls=':')
        plt.text(0.28, 0.60, f"log(n7) = {float(model_n7.intercept_):,.5f} + {float(model_n7.coef_):,.5f}.log(k12)\nR² = {float(model_n7.score(x, y_n7)):,.5f}", ha='center', fontsize=11, fontname='Times New Roman', transform=ax.transAxes)
        plt.savefig(f'{path_graphs}/power_law_simulation_n7.png')
        print(f'Graph saved at: {path_graphs}/power_law_simulation_n7.png')

