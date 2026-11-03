import os

class ModifyCharacters:

    def __init__(self):
        self.path_values = 'outputs/non_rad_rates_constants'
        self.gap_values = []
        self.rates_constants_temp_dependent = ['k65', 'k67', 'k76', 'k87']
        
    def modify_first_character_pop_file(self, path, set_value):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        modified_content = ''
        i1 = 0
        for line in content:
            if i1 == 0:
                new_line = line.replace(line.split()[0], set_value)
                modified_content += new_line
                i1 += 1
            else:
                modified_content += line
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
    def convert_format_scientific_notation(self, path, character, new_character):
        with open(path, 'r', encoding = 'utf_8') as f:
            content = f.read()
        modified_content = content.replace(character, new_character)
        with open(path, 'w', encoding = 'utf_8') as f:
            f.write(modified_content)
        print('Converted format from', character, 'to', new_character, 'in', path)
        
    def gap_rate_constants(self, temp: str):
        gap_rates = {}
        dict_decay_rates = {
            '290': 0,
            '300': 1,
            '310': 2,
            '320': 3,
            '330': 4,
            '340': 5,
            '350': 6,
            '360': 7
        }
            
        file_path = os.listdir(self.path_values)[dict_decay_rates[temp]]
        with open(f'{file_path}', 'r', encoding='utf_8') as f:
            lines = f.readlines()
            for line_id, line in enumerate(lines):
                if 'LiYF4' in line:
                    lines = lines[line_id:len(lines)]
            for line in lines:
                for rates in self.rates_constants_temp_dependent:
                    if rates in line:
                        get_line = line
                        gap_value = get_line.split(': ')[1]
                        gap_value = gap_value.replace('e', 'E').replace('+', '').replace(' \n', '')
                        gap_rates[rates] = gap_value
        return gap_rates
            
    def modify_rates_constants(self, path, temp: str):
        gap_rates = self.gap_rate_constants(temp)
        with open(f'{path}/ET.INP', 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        modified_content = ''
        for line in content:
            for rates in self.rates_constants_temp_dependent:
                if rates in line:
                    new_line = line.replace(line.split()[0], gap_rates[rates])
                    modified_content += new_line
                else:
                    modified_content += line
            
        with open(f'{path}/ET.INP', 'w', encoding='utf-8') as f:
            f.write(modified_content)

    def modify_power_pump(self, path, power_pump):
        with open(f'{path}/ET.INP', 'r', encoding='utf-8') as f: # TODO cpmtinue from here
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

    def modify_non_decay_rates_parameters_in_ET_INP(self, path, substitute_character, new_character, pos=0):
        with open(f'{path}/ET.INP', 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        modified_content = ''
        found_character = False
        for line in content:    
            if substitute_character in line and not found_character:
                new_line = line.replace(line.split()[pos], new_character)
                modified_content += new_line
                found_character = True
            else:
                modified_content += line
        
        with open(f'{path}/ET.INP', 'w', encoding='utf-8') as f:
            f.write(modified_content)
