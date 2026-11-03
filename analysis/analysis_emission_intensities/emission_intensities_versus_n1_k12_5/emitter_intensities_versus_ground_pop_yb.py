print('Importing modules...')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from decimal import Decimal
from pathlib import Path
from shutil import copy as copy_by_shutil
import subprocess



def get_digits(ticks):
    ticks_list = []
    non_zeros = {}
    for i, tick in enumerate(ticks):
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

def modifying_ticks(ax):
    def format_ticks(value, num_digits):
        return str(Decimal(value).quantize(Decimal(f"1.{'0' * num_digits}")))

    ticks = ax.get_yticks()
    digits = get_digits(ticks)
    
    return lambda value: format_ticks(value, digits)



# Replace "E" for "E" in scientific notation
def converter_formato(caminho, character, novo_character):
    with open(caminho, 'r', encoding = 'utf_8') as f:
        conteudo = f.read()
    conteudo_modificado = conteudo.replace(character, novo_character)
    with open(caminho, 'w', encoding = 'utf_8') as f:
        f.write(conteudo_modificado)
     
     

       
        
# Defining initial variables

print('Working on the pop archive paths...')
paths_arqs_pop = {}
all_paths_pops = {}
dir_root = 'C:/Users/jande/Documents/Janderson/GitHub/Dissertacao---Ciencias-de-Materiais/gap_695/emission_intensities_versus_n1_k12_5'
pop_names = ['pop1', 'pop2', 'pop3', 'pop4', 'pop5','pop6','pop7', 'pop8']
pop_names_to_plot = ['pop1','pop5','pop6','pop7']
k12 = 5

def create_folders():
    created_folders = []    
    os.chdir(Path(dir_root))
    for folder in [f'n1_{initial}' for initial in range(1, 61)]:
        if not os.path.exists(os.path.join(dir_root, folder).replace('\\', '/')):
            os.mkdir(folder)
    for folder in os.listdir(Path(dir_root)):
        if os.path.isdir(os.path.join(dir_root, folder).replace('\\', '/')):
            created_folders.append(folder)
    
    folders = sorted(created_folders, key=lambda x: int(x.split('_')[1]))

    return folders

folders = create_folders()

def copy_et_file():
    print(folders)
    for arq in os.listdir(folders[0]):
        if arq == 'ET.INP':
            et_file = os.path.join(folders[0], arq).replace('\\', '/')
        elif arq == 'ucnum8.f':
            ucnum8_file = os.path.join(folders[0], arq).replace('\\', '/')

    for folder in folders[1:len(folders)]:
        copy_by_shutil(et_file, folder)
        copy_by_shutil(ucnum8_file, folder)
        
# copy_et_file()

def edit_et_files():
    for folder in os.listdir(dir_root):
        if 'n1_' in folder:

            folder_number = folder.split('_')[1]
            path_et = os.path.join(dir_root, folder, 'ET.INP')
            
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

# edit_et_files()

def running_fortran_codes():
    conda_env = 'dissertacao'
    name_input_file = 'ucnum8.f'
    name_output_file = 'ucnum8'

    compile_command = f"conda run -n {conda_env} gfortran {name_input_file} -o {name_output_file}"
    try:
        subprocess.run(compile_command, shell=True, check=True)
        print(f"Compiled {name_input_file} successfully to {name_output_file}.")
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



def select_ucnum8():
    for folder in os.listdir(dir_root):
        if 'n1_' in folder:
            os.chdir(os.path.join(dir_root, folder).replace('\\', '/'))
            running_fortran_codes()
        
select_ucnum8()


def select_pop_files():
    print(folders)
    internal_all_pop = {}; internal_plot_pop = {}
    for folder in folders:
        for arq in os.listdir(os.path.join(dir_root, folder)):
            if arq in ['pop1','pop5','pop6','pop7']:
                internal_plot_pop[arq] = os.path.join(os.path.join(dir_root, folder), arq).replace('\\', '/')
            if arq in pop_names:
                internal_all_pop[arq] = os.path.join(os.path.join(dir_root, folder), arq).replace('\\', '/')

        paths_arqs_pop[folder] = internal_plot_pop
        all_paths_pops[folder] = internal_all_pop
                
        internal_plot_pop = {}
        internal_all_pop = {}
    return all_paths_pops




def convert_to_float(arq):
    with open(arq, 'r', encoding='utf_8') as f1:
        lines = f1.readlines()
    if lines:
        lines[0] = '     0.0000000E+00  ' + ' '.join(lines[0].split()[1:]) + '\n'
    with open(arq, 'w', encoding='utf_8') as f2:
        f2.writelines(lines)


for folder_name, pops_paths in select_pop_files().items():
    for pop_name, path_name in pops_paths.items():
        converter_formato(path_name, 'D', 'E')
        convert_to_float(arq=path_name)

print('working on the DataFrames...')

# Get the EataFrames of each pop file in the simulation a

def getdfs():
    dict_populations_time = {}; dict_populations_time_temporary = {}
    for folder in folders:
        for pop in pop_names_to_plot:
            dict_populations_time_temporary[pop] = pd.read_csv(f'{paths_arqs_pop[folder][pop]}', sep=r'\s+', header=None, dtype=np.float64, engine='python').to_numpy()
        dict_populations_time[folder] = dict_populations_time_temporary
        dict_populations_time_temporary = {}
    return dict_populations_time
    


def get_stationary_pop(pop_name):
    dict_populations_time_ = getdfs()
    soma = 0
    with open("c:/Users/jande/Documents/Janderson/GitHub/Dissertacao---Ciencias-de-Materiais/gap_695/emission_intensities_dataframe_k12_5.txt", 'w') as f:
        for value in dict_populations_time_.values():
            for value_key, value_value in value.items():
                f.write(f"{value_key}: {value_value.var()}\n")
                soma += value_value.var()
        f.write(f'TOTAL {soma}')
        
    count = 0
    pops_k12 = {}; value_population = None

    for simulation, value1 in dict_populations_time_.items():
        for pop, dataframe in value1.items():
            aux = True
            if pop == pop_name:
                while count < len(dataframe) and aux:
                    value_time = dataframe[count][0]
                    if value_time > 0.006:
                        value_population = dataframe[count][1]
                        aux = False
                    else:
                        count += 1
            pops_k12[simulation] = value_population
    return pops_k12
    

def get_each_pop():
    stationary_pops = {}
    for pop in pop_names_to_plot:
        stationary_pops[pop] = get_stationary_pop(pop)        
    return stationary_pops


def selected_pop_to_plot():
    pop_5 = {}; pop_6 = {}; pop_7 = {}
    dict_selected_pops = get_each_pop()
    for key_pop, value_pop in dict_selected_pops.items():
        if key_pop == 'pop5':
            pop_5[key_pop] = value_pop
        elif key_pop == 'pop6':
            pop_6[key_pop] = value_pop
        elif key_pop == 'pop7':
            pop_7[key_pop] = value_pop
    return pop_5, pop_6, pop_7

    
pop_5, pop_6, pop_7 = selected_pop_to_plot()

# -------------------- Plot of pop's as a function of the power density -----------------------

A_i3 = 500


def pop_data_to_plot():
    dict_pop_5 = {}; dict_pop_6 = {}; dict_pop_7 = {}
    dict_pop_5['pop5'] = [A_i3*v for d in list(pop_5.values()) for v in d.values()]
    dict_pop_6['pop6'] = [A_i3*v for d in list(pop_6.values()) for v in d.values()]
    dict_pop_7['pop7'] = [A_i3*v for d in list(pop_7.values()) for v in d.values()]
    return dict_pop_5, dict_pop_6, dict_pop_7


dict_pop_files_to_plot = pop_data_to_plot()


# ------------------ Plot the curves for simulation a - t = 0.01s -------------------------------------
path_to_save_graphs = Path('C:/Users/jande/Documents/Janderson/GitHub/Dissertacao---Ciencias-de-Materiais/resultados_gap_695/emission_intensities_versus_n1/emitter_intensities_versus_ground_pop_yb')


if not os.path.exists(path_to_save_graphs):
    os.chdir(os.getcwd())
    os.makedirs(path_to_save_graphs)






conc_y1 = [int(folder.split('_')[1]) for folder in folders]

print(
    os.path.basename(__file__),
    f'plotting the curves...'
)
fig, ax = plt.subplots(figsize=(8.0, 4.8))
plt.plot(conc_y1, dict_pop_files_to_plot[0][pop_names_to_plot[1]], color='#6495EE', label=f'{pop_names_to_plot[1]} (k12 = {k12}.0)', marker='o', ms=2, mec='#6495EE', mfc='#6495EE')
plt.plot(conc_y1, dict_pop_files_to_plot[1][pop_names_to_plot[2]], color='#191970', label=f'{pop_names_to_plot[2]} (k12 = {k12}.0)', marker='o', ms=2, mec='#191970', mfc='#191970')
plt.plot(conc_y1, dict_pop_files_to_plot[2][pop_names_to_plot[3]], color='#660000', label=f'{pop_names_to_plot[3]} (k12 = {k12}.0)', marker='o', ms=2, mec='#660000', mfc='#660000')
plt.legend(loc='center right', prop={"size":10, 'family': 'Times New Roman'})
plt.xlabel('n1', fontsize=11.5, fontname="Times New Roman", weight='semibold')
plt.ylabel(r'$I_{i3}$', fontsize=18, fontname="Times New Roman", weight='semibold')
plt.grid(alpha=0.4, ls=':')
plt.savefig(f'{path_to_save_graphs}/k12_{k12}.png')
