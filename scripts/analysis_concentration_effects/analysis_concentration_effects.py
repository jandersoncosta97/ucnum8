from matplotlib.ticker import FuncFormatter, FormatStrFormatter
from pathlib import Path
import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class ProcessTemporalCurvesConcentrationEffects:
    def __init__(self, directory):
        self.directory = directory
        self.pop_names = [f'pop{i}' for i in range(1, 9)]
        self.origin_cwd = os.getcwd()

    def select_folders(self):
        folders = []
        for folder in os.listdir(self.directory):
            folders.append(folder)
        return folders
    
    def order_folders(self):
        folders = self.select_folders()
        folders = sorted(folders, key=lambda x: int(x.split('_')[1]))
        return folders
    
    def get_paths_pop_files(self, folders_ordered):
        paths_pop_files_internal = {}
        paths_pop_files = {}
        for pop_name in self.pop_names:
            for folder in folders_ordered:
                paths_pop_files_internal[folder] = os.path.join(Path.cwd().as_posix(), self.directory, folder, pop_name).replace('\\', '/')
            paths_pop_files[pop_name] = paths_pop_files_internal
            paths_pop_files_internal = {}
            
        return paths_pop_files

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
        path = os.path.join(Path.cwd().as_posix(), self.directory).replace('\\', '/')
        for folder in os.listdir(path):
            os.chdir(f'{path}/{folder}')
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

    def run_converter(self, paths_pop_files_dict):
        for pops_paths in paths_pop_files_dict.values():
            for path_name in pops_paths.values():
                self.convert_format_scientific_notation(path_name, 'D', 'E')
                self.convert_numbers_to_float(arq=path_name)

    def create_folders_to_save_graphs(self):
        path = self.origin_cwd + '/output/analysis_concentration_effects/population_curves'
        os.makedirs(path, exist_ok=True)

    def get_dataframes(self, paths):
        array_internal = {}
        array = {}
        for pop_name, dict_path in paths.items():
            for simulation, path in dict_path.items():
                array_internal[simulation] = pd.read_csv(path, sep=r'\s+', header=None,
                                    dtype=np.float64, engine='python'
                                    ).to_numpy()
            array[pop_name] = array_internal
            array_internal = {}

        return array

    def plot_temporal_curves(self, arrays):

        time_label = 't = 0.005s'
        letter_idx_list = ['a','b','c','d','a','b','c','d']
        for letter_idx, pop_name in zip(letter_idx_list, self.pop_names):
            print(
                f'plotting the curves of: {time_label}, {pop_name}...'
            )
            fig, ax = plt.subplots(figsize=(8.0, 4.8))
            plt.plot(arrays[pop_name]['simulation_1'][:, 0], arrays[pop_name]['simulation_1'][:, 1], color='#6495ED', label=f'{pop_name} (conc = 2.0)', marker='o', ms=2, mec='#6495ED', mfc='#6495ED')
            plt.plot(arrays[pop_name]['simulation_2'][:, 0], arrays[pop_name]['simulation_2'][:, 1], color='#191970', label=f'{pop_name} (conc = 4.0)', marker='o', ms=2, mec='#191970', mfc='#191970')
            plt.plot(arrays[pop_name]['simulation_3'][:, 0], arrays[pop_name]['simulation_3'][:, 1], color='#ADD8E6', label=f'{pop_name} (conc = 6.0)', marker='o', ms=2, mec='#ADD8E6', mfc='#ADD8E6')
            plt.plot(arrays[pop_name]['simulation_4'][:, 0], arrays[pop_name]['simulation_4'][:, 1], color='#708090', label=f'{pop_name} (conc = 8.0)', marker='o', ms=2, mec='#708090', mfc='#708090')
            plt.plot(arrays[pop_name]['simulation_5'][:, 0], arrays[pop_name]['simulation_5'][:, 1], color='#7FFFD4', label=f'{pop_name} (conc = 10.0)', marker='o', ms=2, mec='#7FFFD4', mfc='#7FFFD4')
            plt.plot(arrays[pop_name]['simulation_6'][:, 0], arrays[pop_name]['simulation_6'][:, 1], color='#00FA9A', label=f'{pop_name} (conc = 12.0)', marker='o', ms=2, mec='#00FA9A', mfc='#00FA9A')
            plt.plot(arrays[pop_name]['simulation_7'][:, 0], arrays[pop_name]['simulation_7'][:, 1], color='#ADFF2F', label=f'{pop_name} (conc = 14.0)', marker='o', ms=2, mec='#ADFF2F', mfc='#ADFF2F')
            plt.plot(arrays[pop_name]['simulation_8'][:, 0], arrays[pop_name]['simulation_8'][:, 1], color='#A0522D', label=f'{pop_name} (conc = 16.0)', marker='o', ms=2, mec='#A0522D', mfc='#A0522D')
            plt.plot(arrays[pop_name]['simulation_9'][:, 0], arrays[pop_name]['simulation_9'][:, 1], color='#F5DEB3', label=f'{pop_name} (conc = 18.0)', marker='o', ms=2, mec='#F5DEB3', mfc='#F5DEB3')
            plt.plot(arrays[pop_name]['simulation_10'][:, 0], arrays[pop_name]['simulation_10'][:, 1], color='#FF1493', label=f'{pop_name} (conc = 20.0)', marker='o', ms=2, mec='#FF1493', mfc='#FF1493')
            plt.legend(loc='center right', prop={"size":10, 'family': 'Times New Roman'})
            plt.xlabel('Time', fontsize=11.5, fontname="Times New Roman", weight='semibold')
            plt.ylabel('Population', fontsize=11.5, fontname="Times New Roman", weight='semibold')
            plt.grid(alpha=0.4, ls=':')
            plt.title(f'({letter_idx})', fontsize=13, fontname="Times New Roman", weight='bold', pad=15)
            plt.savefig(f'{self.origin_cwd}/outputs/analysis_concentration_effects/population_curves/{pop_name}_temporal_curve.png', dpi=300, bbox_inches='tight')
            print(f'Graph saved at: {self.origin_cwd}/outputs/analysis_concentration_effects/population_curves/{pop_name}_temporal_curve.png')
            