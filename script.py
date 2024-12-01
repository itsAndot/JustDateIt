import os
import platform
import time
from datetime import datetime
import ctypes
from ctypes import wintypes

# Arte
just_date_it_art = '''
     ██╗██╗   ██╗███████╗████████╗██████╗  █████╗ ████████╗███████╗██╗████████╗
     ██║██║   ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║╚══██╔══╝
     ██║██║   ██║███████╗   ██║   ██║  ██║███████║   ██║   █████╗  ██║   ██║   
██   ██║██║   ██║╚════██║   ██║   ██║  ██║██╔══██║   ██║   ██╔══╝  ██║   ██║   
╚█████╔╝╚██████╔╝███████║   ██║   ██████╔╝██║  ██║   ██║   ███████╗██║   ██║   
 ╚════╝  ╚═════╝ ╚══════╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝   ╚═╝   
 
 - Andot
'''

# Función para elegir idioma
def choose_language():
    print("Choose the language:")
    print("1. English")
    print("2. Español")
    choice = input("Enter 1 or 2: ")
    return choice

# Mensajes de cada idioma
messages = {
    'en': {
        'invalid_system': "This script is only compatible with Windows systems.",
        'invalid_directory': "The specified directory is not valid.",
        'file_open_error': "Could not open file: {file_path}",
        'update_error': "Error updating creation date for {file_path}",
        'process_error': "Error processing file {file_path}: {e}",
        'updated': "Updated: {file_path}",
        'failed': "Failed: {file_path}",
        'access_error': "Error accessing file {file_path}: {e}",
        'process_completed': "Process completed. {updated_files}/{total_files} files updated.",
        'enter_directory': "Enter the path to the directory where the files are located:"
    },
    'es': {
        'invalid_system': "Este script solo es compatible con sistemas Windows.",
        'invalid_directory': "El directorio especificado no es válido.",
        'file_open_error': "No se pudo abrir el archivo: {file_path}",
        'update_error': "Error al actualizar la fecha de creación en {file_path}",
        'process_error': "Error al procesar el archivo {file_path}: {e}",
        'updated': "Actualizado: {file_path}",
        'failed': "Falló: {file_path}",
        'access_error': "Error al acceder al archivo {file_path}: {e}",
        'process_completed': "Proceso terminado. {updated_files}/{total_files} archivos actualizados.",
        'enter_directory': "Introduce la ruta del directorio donde están los archivos:"
    }
}

# Función para actualizar las fechas
def update_creation_time_to_modification_time(directory, lang):
    if platform.system() != 'Windows':
        print(messages[lang]['invalid_system'])
        return

    if not os.path.isdir(directory):
        print(messages[lang]['invalid_directory'])
        return

    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value

    def set_file_time(file_path, creation_time):
        try:
            # Abrir archivo
            handle = kernel32.CreateFileW(file_path, 256, 0, None, 3, 0x02000000, None)
            if handle == INVALID_HANDLE_VALUE:
                print(messages[lang]['file_open_error'].format(file_path=file_path))
                return False

            # Convierte timestamp a FILETIME
            creation_time = int(creation_time.timestamp() * 10000000) + 116444736000000000
            ctime = wintypes.FILETIME(creation_time & 0xFFFFFFFF, creation_time >> 32)

            # Coloca la fecha del archivo
            success = kernel32.SetFileTime(handle, ctypes.byref(ctime), None, None)
            if not success:
                print(messages[lang]['update_error'].format(file_path=file_path))
            return success
        except Exception as e:
            print(messages[lang]['process_error'].format(file_path=file_path, e=e))
            return False
        finally:
            if handle != INVALID_HANDLE_VALUE:
                kernel32.CloseHandle(handle)

    # Procesa los archivos en el directorio
    total_files = 0
    updated_files = 0
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            total_files += 1
            file_path = os.path.join(root, file_name)
            try:
                # Obtiene la fecha de modificación
                mod_time = os.path.getmtime(file_path)
                mod_datetime = datetime.fromtimestamp(mod_time)

                # Actualiza la fecha de creación
                if set_file_time(file_path, mod_datetime):
                    print(messages[lang]['updated'].format(file_path=file_path))
                    updated_files += 1
                else:
                    print(messages[lang]['failed'].format(file_path=file_path))
            except OSError as e:
                print(messages[lang]['access_error'].format(file_path=file_path, e=e))
    
    print(messages[lang]['process_completed'].format(updated_files=updated_files, total_files=total_files))

# Ejecuta el script
if __name__ == "__main__":
    # Pantalla de inicio
    print(just_date_it_art)
    
    # Elegir idioma
    lang_choice = choose_language()
    if lang_choice == '1':
        lang = 'en'
    elif lang_choice == '2':
        lang = 'es'
    else:
        print("Invalid choice, defaulting to English.")
        lang = 'en'
    
    # Elegir el directorio
    directory = input(messages[lang]['enter_directory'])
    update_creation_time_to_modification_time(directory, lang)
