from enum import StrEnum
import os

class DIR_POWER_PUMPS(StrEnum):

    K12_01_1 = f'{os.getcwd()}/analysis/analysis_power_pumps/power_pumps_k12_01_1'
    K12_1_10 = f'{os.getcwd()}/analysis/analysis_power_pumps/power_pumps_k12_1_10'
    K12_10_100 = f'{os.getcwd()}/analysis/analysis_power_pumps/power_pumps_k12_10_100'
    
class DIR_TO_SAVE_GRAPHS(StrEnum):
    K12_01_1 = f'{os.getcwd()}/outputs/power_pumps_k12_01_1/population_curves'
    K12_1_10 = f'{os.getcwd()}/outputs/power_pumps_k12_01_1/population_curves'
    K12_10_100 = f'{os.getcwd()}/outputs/power_pumps_k12_01_1/population_curves'
    
    