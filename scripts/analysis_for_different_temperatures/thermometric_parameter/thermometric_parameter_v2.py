import subprocess
from pathlib import Path
import os
from math import log
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


class AnalysisThermometricParameter:
    def __init__(self):
        self.paths = {}
        self.origin_cwd = Path.cwd().as_posix()
        self.pop_names = [f'pop{i}' for i in range(1, 9)]
        self.k12 = None
        
    def get_paths(self):
        for temperature in list(range(290, 361, 10)):
            self.paths[temperature] = [f'{Path.cwd().as_posix()}/analysis/analysis_for_different_temperatures/T_{temperature}K/pump_power_01_1/simulation_{i}' for i in range(1, 11)]
        return self.paths

    def edit_et_files(self):
        for temperature, paths in self.paths.items():
            for path in paths:
                power_pump = str(round(float(int(path.split('/')[-1].split('_')[-1])*0.1), 1))
                with open(f'{path}/ET.INP') as f:
                    content = f.readlines()
                modified_content = ''
                for line in content:
                    if 'k12' in line:
                        new_line = line.replace(line.split()[0], power_pump)
                        modified_content += new_line
                    else:
                        modified_content += line
                with open(f'{path}/ET.INP', 'w', encoding='utf-8') as f:
                    f.write(modified_content)

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
        for paths in self.paths.values():
            for path in paths:
                os.chdir(path)
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
        
    def run_converter(self):
        for paths in self.paths.values():
            for path in paths:
                for pop_name in self.pop_names:
                    path_name = os.path.join(path, pop_name).replace('\\', '/')
                    self.convert_format_scientific_notation(path_name, 'D', 'E')
                    self.convert_numbers_to_float(arq=path_name)

    def get_dataframes(self):
        dict_populations_time = {}
        dict_populations_time_temporary = {}
        for paths in self.paths.values():
            for path in paths:
                for pop in ['pop6', 'pop7']:
                    dict_populations_time_temporary[pop] = pd.read_csv(f'{path}/{pop}', sep=r'\s+',
                        header=None, dtype=np.float64, engine='python').to_numpy()
                dict_populations_time[path] = dict_populations_time_temporary
                dict_populations_time_temporary = {}
        return dict_populations_time

    def get_values_at_stationary_state(self, pop_name, dataframes):

        count = 0
        values_at_stationary_state = {}
        value_population = None

        for simulation, value1 in dataframes.items():
            for pop, array in value1.items():
                aux = True
                if pop == pop_name:
                    while count < len(array) and aux:
                        value_time = array[count][0]
                        if value_time > 0.006:
                            value_population = np.median(array[count:count+10, 1])
                            aux = False
                        else:
                            count += 1
                    values_at_stationary_state[simulation] = value_population
        return values_at_stationary_state              

    def apply_model_linear_regression(self, pop6, pop7, simulation):
        value_pop6 = []
        value_pop7 = []
        data_to_plot_X = []
        for key in pop6.keys():
            if simulation == Path(key).name:
                value_pop6.append(pop6[key])
                self.k12 = float(int(simulation.split('_')[1])/10)
        for key in pop7.keys():
            if simulation == Path(key).name:
                value_pop7.append(pop7[key])
        for pop6, pop7 in zip(value_pop6, value_pop7):
            data_to_plot_X.append(pop6 / pop7)

        list_X = []
        for item in data_to_plot_X:
            list_X.append(log(item/data_to_plot_X[0]))
        self.data_to_plot_X = np.array(list_X).reshape(-1, 1)

        list_Y = []
        for item in range(290, 361, 10):
            list_Y.append((1/item))
        self.data_to_plot_Y = np.array(list_Y)

        self.model = LinearRegression().fit(self.data_to_plot_X,
                                            self.data_to_plot_Y)

    def plot_curves_thermometric_parameter(self):

        intercept = float(self.model.intercept_)
        coef = float(self.model.coef_)

        expressao_0 = (
            r'$\frac{1}{T} = '
            f'{intercept:.6f} '
            f'{coef:+.6f}'
            r'\cdot \ln\left(\frac{\Delta}{\Delta_0}\right)$'
            f'\n$R^2 = {self.model.score(self.data_to_plot_X, self.data_to_plot_Y):.7f}$'
        )
        save = f"{Path.cwd()}/outputs/analysis_for_different_temperatures/thermometric_parameter/linear_regression"
        Path(save).mkdir(parents=True, exist_ok=True)
        
        print(f'Plotting the linear regression k12 = {self.k12}...')
        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        plt.plot(self.data_to_plot_X, self.data_to_plot_Y, color='#A1FF', marker='o', label=expressao_0)
        plt.xlabel(r'$\ln\left(\frac{\Delta}{\Delta_0}\right)$')
        plt.ylabel(r'$\frac{1}{T}$', rotation=0, labelpad=15, fontname='Times New Roman', fontsize=14)
        plt.legend(loc='best', prop={"size": 10, 'family': 'Times New Roman'})
        plt.grid(alpha=0.4, ls=':')
        plt.savefig(f'{save}/linear_regression_k12_{self.k12}.png')
        print(f'Graph saved at: {save}/linear_regression_k12_{self.k12}.png')