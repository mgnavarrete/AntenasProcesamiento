import os
from tkinter import Tk, filedialog


def rename_images_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.startswith("Copia de"):
            new_name = filename.replace("Copia de ", "")
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_name)
            os.rename(old_file, new_file)
            print(f"Renamed: {filename} -> {new_name}")


def select_folder_and_rename():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        rename_images_in_folder(folder_selected)
    else:
        print("No se seleccionó ninguna carpeta.")


if __name__ == "__main__":
    select_folder_and_rename()
