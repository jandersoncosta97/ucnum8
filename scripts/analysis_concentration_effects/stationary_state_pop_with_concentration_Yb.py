import os
import subprocess
from pathlib import Path
from decimal import Decimal
from shutil import copy as copy_by_shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class StationaryStatePopWithConcentrationYb:
    
    def __init__(self, directory):
        self.__directory = directory
        self.origin_cwd = os.getcwd()
        self.pop_names = [f'pop{i}' for i in range(1, 9)]
        
        
    def get_digits(self, ticks):
        ticks_list = []
        non_zeros = {}
        for tick in ticks:
            tick = f"{tick:.9f}"
            aux = True
            cont = 0
            for keys, values in enumerate(tick.split('.')[1]):
                while aux == True and cont <= keys:
                    if values != '0':
                        non_zeros[keys] = values
                        cont += 1
                    else:
                        aux = False

            ticks_list.append(float(tick))
        digits = max([len(str(tick).split('.')[1]) for tick in ticks_list if len(str(tick).split('.')) > 1])
        return digits

    def modifying_ticks(self, ax):
        def format_ticks(value, num_digits):
            return str(Decimal(value).quantize(Decimal(f"1.{'0' * num_digits}")))

        ticks = ax.get_yticks()
        digits = self.get_digits(ticks)
        
        return lambda value: format_ticks(value, digits)

    def create_folders(self):
        created_folders = []
        os.chdir(Path(self.__directory))
        for folder in [f'n1_{initial}' for initial in range(10, 101, 10)]:
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

        print(f'\nCurrent directory: {os.getcwd()}')

        input_path = Path(name_input_file).resolve()
        exe_path = Path(f'{name_output_file}.exe').resolve()

        print(f'Fortran source: {input_path}')
        print(f'Executable: {exe_path}')

        compile_command = (
            f"conda run -n {conda_env} "
            f"gfortran {name_input_file} -o {name_output_file}"
        )

        try:
            subprocess.run(
                compile_command,
                shell=True,
                check=True
            )

            print(f"Compiled {name_input_file} successfully.")
            print(f"Executable exists: {exe_path.exists()}")

        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}")
            return

        execute_command = [str(exe_path)]

        print(f"Executing: {execute_command}")

        try:
            subprocess.run(
                execute_command,
                check=True
            )

            print(f"Executed {name_output_file}.exe successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")


    def select_ucnum8_to_run(self):

        for folder in os.listdir(self.__directory):

            if 'n1_' in folder:

                folder_path = Path(self.__directory) / folder

                os.chdir(folder_path)

                print(f'\nRunning: {folder_path.resolve()}')

                self.run_fortran_files()

        os.chdir(self.origin_cwd)


    def population_file_paths(self):
        population_file_paths_internal = {}
        population_file_paths = {}
        folders = os.listdir(f'{self.origin_cwd}/{self.__directory}')
        folders = sorted(folders, key=lambda x: int(x.split('_')[1]))
        for folder in folders:
            for pop_name in self.pop_names:
                population_file_paths_internal[pop_name] = os.path.join(self.origin_cwd, self.__directory, folder, pop_name).replace('\\', '/')
            population_file_paths[folder] = population_file_paths_internal
            population_file_paths_internal = {}
        return population_file_paths
    
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
        for pops_paths in self.population_file_paths().values():
            for path_name in pops_paths.values():
                self.convert_format_scientific_notation(path_name, 'D', 'E')
                self.convert_numbers_to_float(arq=path_name)
                

    def get_arrays(self, paths):
        dict_array_internal = {}
        dict_array = {}
        for folder, dict_paths in paths.items():
            for pop_name, path in dict_paths.items():
                dict_array_internal[pop_name] = pd.read_csv(path, sep=r'\s+',
                    header=None, dtype=np.float64, engine='python').to_numpy()
            dict_array[folder] = dict_array_internal
            dict_array_internal = {}
        return dict_array
    
    def get_values_stationary_state(self, arrays):
        values_stationary_state_internal = {}
        values_stationary_state = {}
        for folder, dict_arrays in arrays.items():
            for pop_name, array in dict_arrays.items():
                values_stationary_state_internal[pop_name] = np.mean(array[array[
                    :, 0] > 0.006, 1])
            values_stationary_state[folder] = values_stationary_state_internal
            values_stationary_state_internal = {}
        return values_stationary_state
    
    def get_ratio(self, values_stationary_state):
        values_n1_10 = []
        ratios_internal = {}
        ratios = {}
        for folder, dict_values in values_stationary_state.items():
            if folder == 'n1_10':
                for pop_name, value in dict_values.items():
                    values_n1_10.append(value)
        for folder, dict_values in values_stationary_state.items():
            for id, (pop_name, value) in enumerate(dict_values.items()):
                ratios_internal[pop_name] = value / values_n1_10[id]
            ratios[folder] = ratios_internal
            ratios_internal = {}
        return ratios
    
    def transpose_dict(self, data: dict) -> dict:
        result = {}

        for outer_key, inner_dict in data.items():
            for inner_key, value in inner_dict.items():
                if inner_key not in result:
                    result[inner_key] = {}
                result[inner_key][outer_key] = value

        return result
    
    def create_path(self):
        path = self.origin_cwd+"/outputs/analysis_concentration_effects/population_stationary_states_versus_conc_y1"
        os.makedirs(path, exist_ok=True)
        return path

    def plot(self, values_ratios, path):
        plt.figure()
        
        n_curves = len(values_ratios)
        cmap = plt.cm.plasma
        colors = cmap(np.linspace(0, 1, n_curves))
        
        for (folder, dict_values), color in zip(values_ratios.items(), colors):
            plt.plot(
                list(range(10, 110, 10)),
                list(dict_values.values()),
                label=folder,
                color=color
            )
        
        plt.legend()
        plt.xlabel("Concentration of Yb")
        plt.ylabel('population/population_10')
        plt.savefig(f'{path}/population_stationary_states_versus_concentration_y1.png', dpi=300)
        print(f'Plot saved at: {path}/population_stationary_states_versus_concentration_y1.png')

