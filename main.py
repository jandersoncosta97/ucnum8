from pathlib import Path
from scripts.analysis_for_different_temperatures.thermometric_parameter.thermometric_parameter_v2 import AnalysisThermometricParameter
from scripts.analysis_k65.analysis_k65 import AnalysisK65
from scripts.analysis_power_pumps.simulations_pump_power import ProcessTemporalCurves
from scripts.analysis_for_different_temperatures.temperature_range.pump_power_temp_range import ProcessTemporalCurvesTemperatureRange
from scripts.analysis_for_different_temperatures.temperature_range.pump_power_temp_range import ProcessTemporalCurvesTemperatureRange
from scripts.analysis_concentration_effects.analysis_concentration_effects import ProcessTemporalCurvesConcentrationEffects
from scripts.analysis_emission_intensities.emission_intensities_versus_n1_k12 import EmissionIntensities
from scripts.analysis_power_pumps.power_law import PowerLawAnalysis
from scripts.analysis_for_different_temperatures.rate_effects_in_ratio_n6_n7.rate_effects_in_ratio import RatioRateConstants
from scripts.analysis_for_different_temperatures.get_rate_constants_with_temperature import DetermineNonRadRateConstants
from scripts.analysis_k87.analysis_k87 import AnalysisK87
from scripts.analysis_power_pumps.stationary_state_power_pumps import StationaryStatePowerPumps
from scripts.analysis_for_different_temperatures.temperature_shifts_v2 import TemperatureShifts
from utils.concatanation_images_concentration_effects import ConcatenationImagesConcEffects
from scripts.analysis_concentration_effects.stationary_state_pop_with_concentration_Yb import StationaryStatePopWithConcentrationYb


def menu():

    print("==================================================")
    print("================LIST OF ANALYSIS==================")
    print("1 - rate effects in ratio n6/n7 - analysis_for_different_temperatures")
    print("2 - power law - analysis_for_different_temperatures")
    print("3 - pump power - analysis_for_different_temperatures")
    print("4 - thermometric parameter - analysis_for_different_temperatures")
    print("5 - analysis power pumps")
    print("6 - analysis emission intensities")
    print("7 - analysis concentration effects")
    print("8 - stationary state - concentration effects")
    print('9 - k65 effects')
    print('10 - k87 effects')
    print("11 - Determine non-radiative rate constants with temperature")
    print("12 - shifts in the predicted temperature")
    print("13 - stationary state - power pumps\n")
    
    choice = input("Choose an option (1-13): ")
    if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']:
        choice = int(choice)
    else:
        print("Invalid choice. Please try again.")
        menu()
    return choice


def select_to_run():

    choice = menu()
    if choice == 1:
        print("running: 1 - rate effects in ratio n6/n7 - analysis_for_different_temperatures")
        run_ratio_effects_for_different_temperatures()
    if choice == 2:
        print("running: 2 - power law - analysis_for_different_temperatures")
        run_power_law()
    if choice == 3:
        print("running: 3 - pump power - analysis_for_different_temperatures")
        run_analysis_power_pumps_analysis_for_different_temperatures()
    if choice == 4:
        print("running: 4 - thermometric parameter - analysis_for_different_temperatures")
        run_thermometric_parameter()
    if choice == 5:
        print("running: 5 - analysis power pumps")
        run_analysis_power_pumps()
    if choice == 6:
        print("running: 6 - analysis emission intensities")
        run_analysis_emission_intensities()
    if choice == 7:
        print("running: 7 - analysis concentration effects")
        run_analysis_concentration_effects()
    if choice == 8:
        print("running: 8 - stationary state - concentration effects")
        run_stationary_state_concentration_effects()
    if choice == 9:
        print("Running: 9 - k65 effects")
        run_k65_effects()
    if choice == 10:
        print("Running: 10 - k87 effects")
        run_k87_effects()
    if choice == 11:
        print("Running: 11 - Determine non-radiative rate constants with temperature")
        run_determine_non_rad_rates_with_temperature()
    if choice == 12:
        print("Running: 12 - shifts in the predicted temperature")
        run_shifts_in_predicted_temperature()
    if choice == 13:
        print("Running: 13 - stationary state - power pumps")
        run_stationary_state_power_pumps()



def run_ratio_effects_for_different_temperatures():
    for i in list(range(1, 11)):
        process = RatioRateConstants(i)
        ratios_1 = process.calculate_ratios()
        arrays = process.get_arrays()
        n6 = process.get_values_at_stationary_state('pop6', arrays)
        n7 = process.get_values_at_stationary_state('pop7', arrays)
        ratios_2 = process.get_ratios_n6_n7(n6, n7)
        process.plot(ratios_1, ratios_2)



def run_power_law():
    path = Path.cwd().as_posix() + "/analysis/analysis_power_pumps/power_pumps_k12_01_1"
    process = PowerLawAnalysis(path)
    process.edit_power_pumps()
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process.select_ucnum8_to_run()
    process.run_converter()
    process.plot()


def run_analysis_power_pumps_analysis_for_different_temperatures():
    process_temporal_curves_temp_range = ProcessTemporalCurvesTemperatureRange()
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process_temporal_curves_temp_range.select_folders()
        process_temporal_curves_temp_range.order_folders()
        process_temporal_curves_temp_range.edit_et_files()
        process_temporal_curves_temp_range.run_fortran()
        process_temporal_curves_temp_range.get_paths_pop_files()
        process_temporal_curves_temp_range.convert_format_pop_files()
        process_temporal_curves_temp_range.plot_temporal_curves()
    elif choice == 'N':
        process_temporal_curves_temp_range.select_folders()
        process_temporal_curves_temp_range.order_folders()
        process_temporal_curves_temp_range.get_paths_pop_files()
        process_temporal_curves_temp_range.convert_format_pop_files()
        process_temporal_curves_temp_range.plot_temporal_curves()
    

def run_thermometric_parameter():
    process = AnalysisThermometricParameter()
    process.get_paths()
    process.edit_et_files()
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process.select_ucnum8_to_run()
    choice = input('CONVERT FORMAT OF POP FILES? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! CONVERT FORMAT OF POP FILES? (Y/N): ').upper()
    if choice == 'Y':
        process.run_converter()
        
    dataframes = process.get_dataframes()
    pop6 = process.get_values_at_stationary_state('pop6', dataframes)
    pop7 = process.get_values_at_stationary_state('pop7', dataframes)
    for simulation in [f'simulation_{n}' for n in range(1, 11)]:
        process.apply_model_linear_regression(pop6, pop7, simulation=simulation)
        process.plot_curves_thermometric_parameter()




def run_analysis_power_pumps():
    process_temporal_curves = ProcessTemporalCurves()
    process_temporal_curves.select_folders()
    process_temporal_curves.order_folders()
    process_temporal_curves.get_paths_pop_files()
    process_temporal_curves.create_folders_to_save_graphs()
    process_temporal_curves.plot_temporal_curves()



def run_analysis_emission_intensities():
    choice = input("K12: 1, 5, 30 or 50?: ")
    while choice not in ['1', '5', '30', '50']:
        choice = input("Invalid choice. K12: 1, 5, 30 or 50?: ")
    directory = f'{Path.cwd().as_posix()}/analysis/analysis_emission_intensities/emission_intensities_versus_n1_k12_{choice}'
    emission_intensities = EmissionIntensities(directory)
    folders = emission_intensities.create_folders()
    emission_intensities.copy_et_inp_files(folders)
    emission_intensities.edit_radiative_rates()
    emission_intensities.edit_initial_concentration()
    choice_run = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice_run not in ['Y', 'N']:
        choice_run = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice_run == 'Y':
        emission_intensities.select_ucnum8_to_run() 
    emission_intensities.run_converter()
    dataframes = emission_intensities.get_dataframes()

    stationary_values_pop5 = emission_intensities.get_intensity_values_at_stationary_state('pop5', 
                                                                        dataframes)
    stationary_values_pop6 = emission_intensities.get_intensity_values_at_stationary_state('pop6', 
                                                                        dataframes)
    stationary_values_pop7 = emission_intensities.get_intensity_values_at_stationary_state('pop7', 
                                                                        dataframes)

    emission_intensities.plot(stationary_values_pop5, stationary_values_pop6,
                              stationary_values_pop7)




def run_analysis_concentration_effects():

    process = ProcessTemporalCurvesConcentrationEffects('analysis/analysis_concentration_effects')
    folders_ordered = process.order_folders()
    paths = process.get_paths_pop_files(folders_ordered)
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process.select_ucnum8_to_run()
    process.run_converter(paths)
    process.create_folders_to_save_graphs()
    arrays = process.get_dataframes(paths)
    process.plot_temporal_curves(arrays)
    
    process = ConcatenationImagesConcEffects(path_conc="outputs/analysis_concentration_effects/population_curves")
    get_imgs = process.get_images()
    h_imgs = process.perform_hconcat(get_imgs)
    v_imgs = process.perform_vconcat(h_imgs)
    process.save_img(v_imgs)




def run_stationary_state_concentration_effects():
    process = StationaryStatePopWithConcentrationYb('analysis/analysis_stationary_states_pop_with_conc_yb')
    paths = process.population_file_paths()
    process.edit_radiative_rates()
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process.select_ucnum8_to_run()
    process.run_converter()
    arrays = process.get_arrays(paths)
    stationary_state = process.get_values_stationary_state(arrays)
    ratios = process.get_ratio(stationary_state)
    ratios = process.transpose_dict(ratios)
    path = process.create_path()
    process.plot(ratios, path)



def run_k87_effects():
    process = AnalysisK87('analysis/k65-k87/simulation_t_290/k87')
    paths = process.select_folders()
    process.run_converter(paths)
    choice = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while choice not in ['Y', 'N']:
        choice = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if choice == 'Y':
        process.select_ucnum8_to_run()
    stationary_populations = process.get_stationary_populations(paths)
    ratios = process.get_ratios(stationary_populations)
    process.plot(ratios)

    

def run_k65_effects():
    process = AnalysisK65('analysis/k65-k87/simulation_t_290')
    population_file_paths = process.select_folders()
    process.run_converter(population_file_paths)
    stationary_populations = process.get_stationary_populations(population_file_paths)
    ratios = process.get_ratios(stationary_populations)
    process.plot(ratios)


def run_determine_non_rad_rates_with_temperature():    
    determine_non_rad_rates_instance = DetermineNonRadRateConstants()
    determine_non_rad_rates_instance.calculate_rates_for_temperatures()
    determine_non_rad_rates_instance.get_k67_rates()
    determine_non_rad_rates_instance.plot_k76_rates()



def run_shifts_in_predicted_temperature():
    temperature_shifts = TemperatureShifts()
    temperature_shifts.get_paths()
    CHOICE = input('EXECUTE FORTRAN? (Y/N): ').upper()
    while CHOICE not in ['Y', 'N']:
        CHOICE = input('INVALID OPTION! EXECUTE FORTRAN? (Y/N): ').upper()
    if CHOICE == 'Y':
        temperature_shifts.edit_et_files()
        temperature_shifts.select_ucnum8_to_run()
        temperature_shifts.run_converter()
    stationary_values = temperature_shifts.get_stationary_populations()
    new_stationary_values = temperature_shifts.sort_dict_by_temperature_and_simulation(stationary_values)
    ratios = temperature_shifts.get_ratios_pop6_pop7(new_stationary_values)
    predicted_temperatures = temperature_shifts.get_predicted_temperature(ratios)
    temperature_shifts.plot(predicted_temperatures)



def run_stationary_state_power_pumps():
    cwd = Path.cwd().as_posix()
    paths = [cwd+f'/analysis/analysis_power_pumps/power_pumps_k12_{i}' for i in
             ['10_100', '1_10', '01_1']]
    for path in paths:
        process = StationaryStatePowerPumps(path=path)
        array_k12 = process.get_arrays_pop_k12()
        stationary_pop_k12 = process.get_values_at_stationary_state(array_k12)
        ordered_values = process.order_values(stationary_pop_k12)
        ratios = process.get_ratio(ordered_values)
        process.plot_curves(ratios)


def main():
    select_to_run()


if __name__ == "__main__":
    main()
