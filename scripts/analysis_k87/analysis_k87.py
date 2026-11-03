import matplotlib.pyplot as plt
import os
from pathlib import Path
import subprocess
import numpy as np
import pandas as pd

class AnalysisK87:

    def __init__(self, directory: str):
        self.__directory = directory
        self.origin_cwd = os.getcwd()
        self.pop_names = [f'pop{i}' for i in range(1, 9)]

    def select_folders(self):
        file_paths = []
        population_file_paths = []
        for folder in os.listdir(self.__directory):
            file_paths.append(os.path.join(self.__directory,
                                                           folder).replace("\\", '/'))

        for path in file_paths:
            for item in os.listdir(path):
                if ('pop6' in item) or ('pop7' in item):
                    population_file_paths.append(os.path.join(path, item).replace('\\', '/'))
                    
        return population_file_paths

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
        for path in self.population_file_paths:
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

    def run_converter(self, population_file_paths):
        for pop_path in population_file_paths:
            self.convert_format_scientific_notation(pop_path, 'D', 'E')
            self.convert_numbers_to_float(arq=pop_path)
    
    def get_stationary_populations(self, paths_pop_files):
        stationary_value_internal = {}
        stationary_value = {}
        for path in paths_pop_files:
            stationary_value_internal[Path(path).name] = pd.read_csv(f'{path}', sep=r'\s+',
                header=None, dtype=np.float64, engine='python').to_numpy()[-10:, 1].mean()
            stationary_value[path] = stationary_value_internal
            stationary_value_internal = {}
        return stationary_value

    def get_ratios(self, stationary_populations):
        ratios = {}
        for path, pop_values in stationary_populations.items():
            if 'pop6' in Path(path).name:
                pop6 = pop_values['pop6']
            if 'pop7' in Path(path).name:
                pop7 = pop_values['pop7']
                ratios[Path(path).parent.name] = pop6 / pop7
        return ratios
    
    def plot(self, ratios):
        plt.figure(figsize=(8, 4.8))
        k87 = list(ratios.split('_')[-1] for ratios in ratios.keys())
        plt.plot(k87, list(ratios.values()), marker='o')
        plt.xlabel('k87')
        plt.ylabel('Population Ratio (pop6/pop7)')
        plt.savefig('outputs/k87/population_ratios_k87.png')
        print(f'Graph saved at: outputs/k87/population_ratios_k87.png')        
