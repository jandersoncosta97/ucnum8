from statistics import mean
from math import exp
import matplotlib.pyplot as plt
from pathlib import Path


class DetermineNonRadRateConstants:
    def __init__(self):
        self.temperatures = list(range(290, 361, 10))
        self.deltaE76 = 695
        self.energy_levels = {
            '1': mean([0, 218, 248, 485]),
            '2': mean([10293, 10416, 10554]),
            '3': mean([8, 11, 11, 50, 250, 285, 317, 336]),
            '4': mean([10216, 10231, 10284, 10305, 10310, 10322]),
            '5': mean([15335, 15359, 15375, 15447, 15502]),
            '6': mean([18437, 18496]),
            '7': mean([19165, 19188, 19232, 19307, 19313, 19327]),
            '8': mean([20542, 20544, 20638, 20647])
        }
        self._kb = 0.6950348004

    def get_energy_levels(self):
        Energy43 = self.energy_levels['4'] - self.energy_levels['3']
        Energy54 = self.energy_levels['5'] - self.energy_levels['4']
        Energy65 = self.energy_levels['6'] - self.energy_levels['5']
        Energy76 = self.deltaE76
        Energy87 = self.energy_levels['8'] - self.energy_levels['7']
        return Energy43, Energy54, Energy65, Energy76, Energy87

    def non_rad_rates(self, deltaE, temperature):
        Constant = 3.5*10**7
        alfa = 3.8*10**(-3)
        ni_effective = 400
        return Constant*(exp(-alfa*deltaE))/((1-exp(-ni_effective/(self._kb*temperature)))**(deltaE/ni_effective))

    def calculate_rates_for_temperatures(self):
        energy43, energy54, energy65, energy76, energy87 = self.get_energy_levels()
        k76_rates = {}
        k43_rates = {}
        k54_rates = {}
        k65_rates = {}
        k76_rates = {}
        k87_rates = {}
        for temp in self.temperatures:
            k76_rates[temp] = self.non_rad_rates(energy76, temp)
            k43_rates[temp] = self.non_rad_rates(energy43, temp)
            k54_rates[temp] = self.non_rad_rates(energy54, temp)
            k65_rates[temp] = self.non_rad_rates(energy65, temp)
            k87_rates[temp] = self.non_rad_rates(energy87, temp)
        return k76_rates, k43_rates, k54_rates, k65_rates, k87_rates

    def get_k67_rates(self):
        k76_rates = self.calculate_rates_for_temperatures()[0]
        k67_rates = {}
        for temp in self.temperatures:
            k67_rates[temp] = k76_rates[temp]*exp(-self.deltaE76/(self._kb*temp))
        return k67_rates

    def plot_k76_rates(self):
        save_path = f'{Path.cwd()}/outputs/non_rad_rates_constants' 
        k76_rates = self.calculate_rates_for_temperatures()[0]
        plt.plot(self.temperatures, list(k76_rates.values()), marker='o', color='blue')
        plt.xlabel('Temperature (K)')
        plt.ylabel('Nonradiative rate, k76')
        plt.grid()
        plt.savefig(f'{save_path}/k76_rates.png')
        print(f'Graph saved at: {save_path}/k76_rates.png')
