from pathlib import Path
import os
from shutil import copy as copy_by_shutil
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class EmissionIntensities:
    
    def __init__(self, directory: str):
        self.__directory = directory
        self.origin_cwd = os.getcwd()
        if 'k12_1' in self.__directory:
            self.k12_value = 1
        elif 'k12_5' in self.__directory and not 'k12_50' in self.__directory:
            self.k12_value = 5
        elif 'k12_30' in self.__directory:
            self.k12_value = 30
        elif 'k12_50' in self.__directory:
            self.k12_value = 50
        self.pop_names_to_plot = ['pop5', 'pop6', 'pop7']
        self.folders = []
        self.population_file_paths = None
        self.origin_path = os.getcwd()

    def create_folders(self):
        created_folders = []
        os.chdir(Path(self.__directory))
        for folder in [f'n1_{initial}' for initial in range(1, 61)]:
            if not os.path.exists(os.path.join(self.__directory,
                                               folder).replace('\\', '/')):
                os.mkdir(folder)
        for folder in os.listdir(Path(self.__directory)):
            if os.path.isdir(os.path.join(self.__directory,
                                          folder).replace('\\', '/')):
                created_folders.append(folder)
        folders = sorted(created_folders, key=lambda x: int(x.split('_')[1]))

        return folders

    def copy_et_inp_files(self, folders):
        self.folders = folders

        for arq in os.listdir(self.folders[0]):
            if arq == 'ET.INP':
                et_file = os.path.join(self.folders[0], arq).replace('\\', '/')
            elif arq == 'ucnum8.f':
                ucnum8_file = os.path.join(self.folders[0], arq).replace('\\', '/')

        for folder in self.folders[1:len(self.folders)]:
            copy_by_shutil(et_file, folder)
            copy_by_shutil(ucnum8_file, folder)



    def edit_radiative_rates(self):
        for folder in os.listdir(self.__directory):
            if 'n1_' in folder:
                path_et = os.path.join(self.__directory, folder, 'ET.INP').replace('\\', '/')
                with open(f'{path_et}', 'r') as f:
                    content = f.readlines()
                modified_content = ''
                for line in content:
                    if 'k53' in line or 'k63' in line or 'k73' in line:
                        new_line = line.replace(line.split()[0], '1.00E03')
                        modified_content += new_line
                    else:
                        modified_content += line
                with open(f'{path_et}', 'w', encoding='utf-8') as f:
                    f.write(modified_content)  
                          
    def edit_initial_concentration(self):
        for folder in os.listdir(self.__directory):
            if 'n1_' in folder:

                folder_number = folder.split('_')[1]
                path_et = os.path.join(self.__directory, folder, 'ET.INP')

                if os.path.isfile(path_et):
                    with open(path_et, 'r', encoding='utf_8') as f:
                        lines = f.readlines()

                    for i in range(len(lines)):
                        if 'y1' in lines[i]:
                            if float(folder_number) < 10: 
                                lines[i] = f"{folder_number}.0         y1\n"
                            else:
                                lines[i] = f"{folder_number}.0        y1\n"

                    with open(path_et, 'w', encoding='utf_8') as f:
                        f.writelines(lines)

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
        execute_command = f".\\{name_output_file}.exe"
        try:
            subprocess.run(execute_command, shell=True, check=True)
            print(f"Executed {name_output_file} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")

    def select_ucnum8_to_run(self):
        for folder in os.listdir(self.__directory):
            if 'n1_' in folder:
                os.chdir(os.path.join(self.__directory, folder).replace('\\', '/'))
                self.run_fortran_files()
        os.chdir(self.origin_cwd)
        
    def get_population_file_paths(self):
        internal_all_pop = {}
        internal_plot_pop = {}
        paths_arqs_pop = {}
        all_paths_pops = {}

        for folder in self.folders:
            for arq in os.listdir(os.path.join(self.__directory, folder)):
                if arq in self.pop_names_to_plot:
                    internal_plot_pop[arq] = os.path.join(os.path.join(
                        self.__directory, folder), arq).replace('\\', '/')
                if arq in [f'pop{i}' for i in range(1, 9)]:
                    internal_all_pop[arq] = os.path.join(os.path.join(
                        self.__directory, folder), arq).replace('\\', '/')

            paths_arqs_pop[folder] = internal_plot_pop
            all_paths_pops[folder] = internal_all_pop

            internal_plot_pop = {}
            internal_all_pop = {}
        return all_paths_pops

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
        self.population_file_paths = self.get_population_file_paths()
        for pops_paths in self.population_file_paths.values():
            for path_name in pops_paths.values():
                self.convert_format_scientific_notation(path_name, 'D', 'E')
                self.convert_numbers_to_float(arq=path_name)

    def get_dataframes(self):
        dict_populations_time = {}
        dict_populations_time_temporary = {}
        for folder in self.folders:
            for pop in self.pop_names_to_plot:
                dict_populations_time_temporary[pop] = pd.read_csv(f'{
                    self.population_file_paths[folder][pop]}', sep=r'\s+',
                    header=None, dtype=np.float64, engine='python').to_numpy()
            dict_populations_time[folder] = dict_populations_time_temporary
            dict_populations_time_temporary = {}
        return dict_populations_time

    def get_intensity_values_at_stationary_state(self, pop_name, get_dataframes):

        count = 0
        intensities = {}
        value_population = None

        for simulation, value1 in get_dataframes.items():
            for pop, array in value1.items():
                aux = True
                if pop == pop_name:
                    while count < len(array) and aux:
                        value_time = array[count][0]
                        if value_time > 0.006:
                            value_population = array[count][1]
                            aux = False
                        else:
                            count += 1
                    intensities[simulation] = value_population*500
        return intensities


    def plot(self, *dict_pop_files_to_plot):

        list_emission_5 = list(dict_pop_files_to_plot[0].values())
        list_emission_6 = list(dict_pop_files_to_plot[1].values())
        list_emission_7 = list(dict_pop_files_to_plot[2].values())
        
        path_to_save_graphs = f'{self.origin_cwd}/outputs/emission_intensities_versus_n1'
        os.makedirs(path_to_save_graphs, exist_ok=True)

        conc_y1 = [int(folder.split('_')[1]) for folder in self.folders]

        fig, ax = plt.subplots(figsize=(8.0, 4.8))
        plt.plot(conc_y1, list_emission_5, color='#6495EE', label=f'{
            self.pop_names_to_plot[0]} (k12 = {self.k12_value}.0)', marker='o',
            ms=2, mec='#6495EE', mfc='#6495EE')
        plt.plot(conc_y1, list_emission_6, color='#191970', label=f'{
            self.pop_names_to_plot[1]} (k12 = {self.k12_value}.0)', marker='o',
            ms=2, mec='#191970', mfc='#191970')
        plt.plot(conc_y1, list_emission_7, color='#660000', label=f'{
            self.pop_names_to_plot[2]} (k12 = {self.k12_value}.0)', marker='o',
            ms=2, mec='#660000', mfc='#660000')
        plt.legend(loc='center right', prop={"size":10, 'family': 'Times New Roman'})
        plt.xlabel('Concentration of Yb', fontsize=11.5, fontname="Times New Roman", weight='semibold')
        plt.ylabel(r'$I_{i3}$', fontsize=18, fontname="Times New Roman", weight='semibold')
        plt.grid(alpha=0.4, ls=':')
        plt.savefig(f'{path_to_save_graphs}/k12_{self.k12_value}.png')
        print(f'Graph saved at: {path_to_save_graphs}/k12_{self.k12_value}.png')