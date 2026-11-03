
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FormatStrFormatter
import numpy as np
import pandas as pd
import os
import re
from pathlib import Path
from dirs.dirs import DIR_POWER_PUMPS
from utils.ticksformatter import TicksFormatter



class ProcessTemporalCurves:

    def __init__(self):
        self.root_dirs = [DIR_POWER_PUMPS.K12_01_1.value, 
                          DIR_POWER_PUMPS.K12_1_10.value, 
                          DIR_POWER_PUMPS.K12_10_100.value]
        self.folders = [None]*10
        self.pop_names = ['pop1', 'pop2', 'pop3', 'pop4', 'pop5', 'pop6', 'pop7', 'pop8']
        self.paths_arqs_pop_files = [[None]*8 for _ in range(10)]
        self.chosen_dir = None
        self.path_to_save_graphs = None
        self.choice = None
        self.pump_power = None

    def select_folders(self):
        self.choice = input('Enter the power pump (0 for k12_01_1, 1 for k12_1_10, 2 for k12_10_100): ')
        while self.choice not in ['0', '1', '2']:
            print('Invalid input. Please enter 0, 1, or 2.')
            self.choice = input('Enter the power pump (0 for k12_01_1, 1 for k12_1_10, 2 for k12_10_100): ')
        self.choice = int(self.choice)
        self.chosen_dir = self.root_dirs[self.choice]
        if self.choice == 0:
            self.pump_power = '01_1'
        elif self.choice == 1:
            self.pump_power = '1_10'
        elif self.choice == 2:
            self.pump_power = '10_100'
        else:
            raise ValueError("Invalid choice for pump power.")
        
        i1 = 0
        for folder_arq in os.listdir(self.chosen_dir):
            if os.path.isdir(os.path.join(self.chosen_dir, folder_arq).replace("\\", "/")):
                self.folders[i1] = folder_arq
                i1 += 1

    def order_folders(self):
        self.folders = sorted(self.folders, key=lambda x: int(x.split('simulation_')[1]))


    def get_paths_pop_files(self):
        i2 = 0
        for idx, folder in enumerate(self.folders):
            for arq in os.listdir(os.path.join(self.chosen_dir, folder)):
                if arq in self.pop_names:
                    self.paths_arqs_pop_files[idx][i2] = os.path.join(os.path.join(self.chosen_dir, folder), arq).replace('\\', '/')
                    i2 += 1
            i2 = 0


    def get_dataframes_from_pop_files(self):
        print('working on the DataFrames...')

        dict_populations = {}
        dict_time = {} 
        dict_df_time_temporary = {}
        dict_df_populations_temporary = {}
        for idx1, folder in enumerate(self.folders):
            for idx2, pop in enumerate(self.pop_names):
                dict_df_populations_temporary[pop] = pd.read_csv(f'{self.paths_arqs_pop_files[idx1][idx2]}', sep=r'\s+', header=None, dtype=np.float64, engine='python').to_numpy()[:,1]
                dict_df_time_temporary[pop] = pd.read_csv(f'{self.paths_arqs_pop_files[idx1][idx2]}', sep='\s+', header=None, dtype=np.float64, engine='python').to_numpy()[:,0]
            dict_populations[folder] = dict_df_populations_temporary
            dict_time[folder] = dict_df_time_temporary
            dict_df_populations_temporary = {}
            dict_df_time_temporary = {}

        return dict_populations, dict_time

    def create_folders_to_save_graphs(self):
        dirname = f"outputs/power_pumps_{self.pump_power}/population_curves"
        self.path_to_save_graphs = Path(dirname)
        if not os.path.exists(self.path_to_save_graphs):
            os.chdir(os.getcwd())
            os.makedirs(self.path_to_save_graphs)


    def plot_temporal_curves(self):

        dict_populations, dict_time = self.get_dataframes_from_pop_files()
        time_label = 't = 0.005s'
        letter_idx_list = ['a','b','c','d','a','b','c','d']
        for letter_idx, pop_name in zip(letter_idx_list, self.pop_names):
            print(
                f'plotting the curves of: {time_label}, {pop_name}...'
            )
            fig, ax = plt.subplots(figsize=(8.0, 4.8))
            plt.plot(dict_time[self.folders[0]][pop_name], dict_populations[self.folders[0]][pop_name], color='#6495ED', label=f'{pop_name} (k12 = 0.1)', marker='o', ms=2, mec='#6495ED', mfc='#6495ED')
            plt.plot(dict_time[self.folders[1]][pop_name], dict_populations[self.folders[1]][pop_name], color='#191970', label=f'{pop_name} (k12 = 0.2)', marker='o', ms=2, mec='#191970', mfc='#191970')
            plt.plot(dict_time[self.folders[2]][pop_name], dict_populations[self.folders[2]][pop_name], color='#ADD8E6', label=f'{pop_name} (k12 = 0.3)', marker='o', ms=2, mec='#ADD8E6', mfc='#ADD8E6')
            plt.plot(dict_time[self.folders[3]][pop_name], dict_populations[self.folders[3]][pop_name], color='#708090', label=f'{pop_name} (k12 = 0.4)', marker='o', ms=2, mec='#708090', mfc='#708090')
            plt.plot(dict_time[self.folders[4]][pop_name], dict_populations[self.folders[4]][pop_name], color='#7FFFD4', label=f'{pop_name} (k12 = 0.5)', marker='o', ms=2, mec='#7FFFD4', mfc='#7FFFD4')
            plt.plot(dict_time[self.folders[5]][pop_name], dict_populations[self.folders[5]][pop_name], color='#00FA9A', label=f'{pop_name} (k12 = 0.6)', marker='o', ms=2, mec='#00FA9A', mfc='#00FA9A')
            plt.plot(dict_time[self.folders[6]][pop_name], dict_populations[self.folders[6]][pop_name], color='#ADFF2F', label=f'{pop_name} (k12 = 0.7)', marker='o', ms=2, mec='#ADFF2F', mfc='#ADFF2F')
            plt.plot(dict_time[self.folders[7]][pop_name], dict_populations[self.folders[7]][pop_name], color='#A0522D', label=f'{pop_name} (k12 = 0.8)', marker='o', ms=2, mec='#A0522D', mfc='#A0522D')
            plt.plot(dict_time[self.folders[8]][pop_name], dict_populations[self.folders[8]][pop_name], color='#F5DEB3', label=f'{pop_name} (k12 = 0.9)', marker='o', ms=2, mec='#F5DEB3', mfc='#F5DEB3')
            plt.plot(dict_time[self.folders[9]][pop_name], dict_populations[self.folders[9]][pop_name], color='#FF1493', label=f'{pop_name} (k12 = 1.0)', marker='o', ms=2, mec='#FF1493', mfc='#FF1493')
            plt.legend(loc='center right', prop={"size":10, 'family': 'Times New Roman'})
            plt.xlabel('Time (s)', fontsize=11.5, fontname="Times New Roman", weight='semibold')
            plt.ylabel('Population', fontsize=11.5, fontname="Times New Roman", weight='semibold')
            plt.grid(alpha=0.4, ls=':')
            if pop_name in ['pop5', 'pop7','pop8']:
                    ax.yaxis.set_major_formatter(FormatStrFormatter('%.6f'))
            else:
                ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: TicksFormatter(ax).modify_ticks()(x)))
            plt.title(f'({letter_idx})', fontsize=13, fontname="Times New Roman", weight='bold', pad=15)
            plt.savefig(f'{self.path_to_save_graphs}/{pop_name}_k12_{self.pump_power}.png')
            print(f'Graph saved at: {self.path_to_save_graphs}/{pop_name}_k12_{self.pump_power}.png')
            plt.close()
