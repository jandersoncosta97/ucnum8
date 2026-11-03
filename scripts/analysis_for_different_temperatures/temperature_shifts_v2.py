import re
from pathlib import Path
import subprocess
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class TemperatureShifts:
    
    def __init__(self):
        self.paths = {}
        self.origin_cwd = Path.cwd().as_posix()
        self.pop_names = [f'pop{i}' for i in range(1, 9)]
        
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

    def get_stationary_populations(self):
        stationary_value_internal = {}
        stationary_value = {}
        for paths in self.paths.values():
            for path in paths:
                for pop in ['pop6', 'pop7']:
                    stationary_value_internal[pop] = pd.read_csv(f'{path}/{pop}', sep=r'\s+',
                        header=None, dtype=np.float64, engine='python').to_numpy()[-10:, 1].mean()
                stationary_value[path] = stationary_value_internal
                stationary_value_internal = {}
        return stationary_value
    

    def sort_dict_by_temperature_and_simulation(self, data):
        
        def sort_key(path):

            temp = int(re.search(r'T_(\d+)K', path).group(1))
            

            sim = int(re.search(r'simulation_(\d+)', path).group(1))
            
            return (sim, temp)
        
        return dict(sorted(data.items(), key=lambda item: sort_key(item[0])))


    def get_ratios_pop6_pop7(self, stationary_values):
        ratios = {}
        for path, values in stationary_values.items():
            ratio = values['pop6'] / values['pop7'] if values['pop7'] != 0 else np.nan
            ratios[path] = ratio
        return ratios

    def get_predicted_temperature(self, ratios):
        predicted_temperatures = []
        kb = 0.6950348004
        deltaE76 = 690.8895
        for ratio in ratios.values():
            predicted_temperatures.append((deltaE76/kb)/np.log(ratio))
        return predicted_temperatures


    def plot(self, predicted_temperatures):

        real_temperatures = np.array(list(range(290, 361, 10)))

        predicted_array = np.array(predicted_temperatures).reshape(10, 8)

        for (sim_index, sim_values), k12 in zip(enumerate(predicted_array), ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']):

            shifts = ((sim_values - real_temperatures) / real_temperatures) * 100

            plt.figure(figsize=(8, 5))

            plt.bar(
                real_temperatures,
                shifts,
                color='green',
                width=6
            )

            plt.axhline(0, color='black', linestyle='--')

            plt.xlabel('Temperature (K)')
            plt.ylabel('Deviation (%)')
            if k12 != '10':    
                plt.title(
                    f'Temperature shifts - simulation {sim_index + 1} '
                    f'(k12 = 0.{k12})'
                )
            else:
                plt.title(
                    f'Temperature shifts - simulation {sim_index + 1} '
                    f'(k12 = 1.0)'
                )

            plt.xticks(real_temperatures)

            plt.savefig(
                f'{self.origin_cwd}/outputs/'
                f'analysis_for_different_temperatures/'
                f'temperature_shifts/'
                f'temperature_shifts_simulation_{sim_index + 1}.png',
                dpi=300,
                bbox_inches='tight'
            )
            print(f'saved - {self.origin_cwd}/outputs/'
                f'analysis_for_different_temperatures/'
                f'temperature_shifts/'
                f'temperature_shifts_simulation_{sim_index + 1}.png')
            plt.close()
