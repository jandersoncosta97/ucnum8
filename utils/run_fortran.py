import os
import subprocess
import sys

class RunFortran:

    def __init__(self):
        self.rel_initial_path = 'analysis'

    def list_folders(self):
        dict_folders = {}
        cwd = os.getcwd()
        abs_initial_path = os.path.join(cwd, self.rel_initial_path).replace('\\', '/')
        for idx, folder_arq in enumerate(os.listdir(abs_initial_path)):
            dict_folders[idx+1] = folder_arq
        print(dict_folders)
        return dict_folders

    def select_folder(self):

        list_of_folders = self.list_folders()
        folder_key = input('KEY: ')
        while folder_key not in ['1', '2', '3', '4']:
            print('NOT A VALID KEY')
            folder_key = input('KEY: ')
        return list_of_folders[int(folder_key)]

    def select_subfolders(self):

        target_folder = self.select_folder()
        print(f'TARGET_FOLDER: "{target_folder}"\n')
        sub_folders = os.listdir(os.path.join(os.getcwd(), self.rel_initial_path, target_folder).replace('\\', '/'))
        sub_folders = sorted(sub_folders, key=lambda x: int(x.split('_')[1]))
        print(f'SUBFOLDERS:\n\n{sub_folders}')
        return target_folder, sub_folders

    def get_path(self, *args):

        path_continuation = "/".join(map(str, args))
        print(path_continuation)
        return os.path.join(os.getcwd(), self.rel_initial_path, path_continuation).replace('\\', '/')
        

    def run_fortran(self, path_dir_files):

        name_input_file = 'ucnum8.f'
        name_output_file = 'ucnum8.exe'
        conda_env = 'dissertacao'
        input_file_path = os.path.join(path_dir_files, name_input_file)
        output_file_path = os.path.join(path_dir_files, name_output_file.removesuffix(".exe"))

        set_codepage_command = 'chcp 65001'
        try:
            subprocess.run(set_codepage_command, shell=True, check=True, cwd=path_dir_files)
        except subprocess.CalledProcessError as e:
            print(f"Failed to set code page: {e}")
            sys.exit(1)


        # Normalize paths to UTF-8
        input_file_path = os.fsdecode(input_file_path.encode('utf-8').decode('utf-8').replace('\\', '/'))
        output_file_path = os.fsdecode(output_file_path.encode('utf-8').decode('utf-8').replace('\\', '/'))

        input_file_path = os.path.abspath(input_file_path).replace('\\', '/')
        output_file_path = os.path.abspath(output_file_path).replace('\\', '/')

        compile_command = f'conda run -n {conda_env} gfortran "{input_file_path}" -o "{output_file_path}"'
        try:
            subprocess.run(compile_command, shell=True, check=True, cwd=path_dir_files)
            print(f"Compiled {name_input_file} successfully to {name_output_file}.")
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e}")
            exit(1)

        execute_command = f'"{output_file_path}"'
        try:
            subprocess.run(execute_command, shell=True, check=True, cwd=path_dir_files)
            print(f"Executed {name_output_file} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Execution failed: {e}")


    def run(self):

        folders_tuple = self.select_subfolders()
        target_folder  = folders_tuple[0]
        subfolders = folders_tuple[1]
        for subfolder in subfolders:
            self.run_fortran(f'{self.get_path(target_folder, subfolder)}')
