import os

class ListDirs:
    
    def __init__(self):
        self.name_input_file = 'ucnum8.f'
        self.name_output_file = 'ucnum8.exe'
        self.roots_input_file = []
        self.roots_output_file = []
            
    def list_dirs_pop_files(self, chosen_path):
        directories_to_process = []
        paths_pop_files = []
        pop_file_names = ['pop1', 'pop2', 'pop3', 'pop4', 'pop5', 'pop6', 'pop7', 'pop8']
        
        path = os.path.join(os.getcwd(), chosen_path).replace('\\', '/')
        for root, dirs, files in os.walk(path):
            # Check for required files in the current directory
            input_file_found = False
            output_file_found = False
            
            if self.name_input_file in files:
                input_file_found = True
                path_input_file = os.path.join(root, self.name_input_file).replace('\\', '/')
                self.roots_input_file.append(path_input_file)
            
            if self.name_output_file in files:
                output_file_found = True
                path_output_file = os.path.join(root, self.name_output_file).replace('\\', '/')
                self.roots_output_file.append(path_output_file)
            
            # If both files are found in the same directory, run Fortran
            if input_file_found and output_file_found:
                directories_to_process.append(root.replace('\\', '/'))
        
        for root, dirs, files in os.walk(chosen_path):
            for pop_file_name in pop_file_names:
                if pop_file_name in files:
                    paths_pop_files.append(os.path.join(root, pop_file_name).replace('\\', '/'))

        return directories_to_process, paths_pop_files

    def order_dirs(self, paths: list, dir_type = 'pop'):
        if dir_type == 'pop':
            return sorted(paths, key=lambda x: int((x.split('simulation_')[1]).split('/')[0]))
        elif dir_type == 'simulation':
            return sorted(paths, key=lambda x: int(x.split('simulation_')[1]))
        else:
            print('Invalid directory type. Please choose "pop" or "simulation".')
            return None
        
    def list_dirs_thermometric_parameter(self, chosen_path, target):
        directories = []
        
        path = os.path.join(os.getcwd(), chosen_path).replace('\\', '/')
        for root, dirs, files in os.walk(path):
            # Check for required files in the current directory
            if target in dirs:
                directories.append(os.path.join(root, target).replace('\\', '/'))
        
        return directories