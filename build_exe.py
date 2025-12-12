import PyInstaller.__main__
import os
import shutil

# Definir rutas
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, 'src')
main_script = os.path.join(src_dir, 'main.py')
tmvs_exe = os.path.join(src_dir, 'bin', 'tmvs-cli.exe')
media_dir = os.path.join(src_dir, 'media')

# Verificar que el ejecutable de TM existe
if not os.path.exists(tmvs_exe):
    print(f"Error: No se encontró {tmvs_exe}")
    print("Por favor asegúrate de haber compilado y copiado tmvs-cli.exe a src/bin/")
    exit(1)

# Argumentos para PyInstaller
args = [
    main_script,
    '--name=CompiladorIDE',
    '--onefile',  # Un solo archivo ejecutable
    '--windowed', # No mostrar consola (GUI app)
    '--clean',
    # Incluir el ejecutable de TM en la carpeta bin dentro del paquete
    f'--add-data={tmvs_exe}{os.pathsep}bin',
    # Incluir la carpeta media
    f'--add-data={media_dir}{os.pathsep}media',
    # Rutas de búsqueda
    f'--paths={src_dir}',
]

print("Iniciando construcción con PyInstaller...")
print(f"Argumentos: {args}")
PyInstaller.__main__.run(args)
print("Construcción finalizada. El ejecutable está en la carpeta 'dist'.")
