from utils.functions import *
import os
from tkinter import filedialog


def preProceso(task_name):

    try:
        levID, medID, task_name = taskInput(task_name)
        (
            rootPath,
            imagesPath,
            labelsPath,
            detectionsPath,
            s3_labels,
            s3_detections,
            s3_reporte,
            filenames,
            cropPath,
            metadataPath,
        ) = getDirectories(task_name)

        imageCenitalPath = filedialog.askopenfilename(
            title="Seleccione Vista Cenital",
            initialdir=f"torres/{task_name}",
        )

        filenameCenital = os.path.basename(imageCenitalPath)
        metadataPathCenital = os.path.join(
            metadataPath, filenameCenital.replace(".JPG", ".txt")
        )
        imageCenital = cv2.imread(imageCenitalPath)
        metadataCenital = read_metadata(metadataPathCenital)
        yawDegreesCenital = float(metadataCenital["GimbalYawDegree"])
        modelo = metadataCenital["Model"]
        print(f"Modelo: {modelo}")
        imageCenital = fixDistor(imageCenital, modelo)
        angle_to_north = -yawDegreesCenital
        pix2cm = 0
        print("Calculando relación pixeles a cm...")
        cmRef = int(
            input("Ingrese la distancia en cm entre los puntos de referencia: ")
        )
        pix2cm = select_cmRef(imageCenital, cmRef)

        # Guardar imagen cenital y metadata en carpeta task_name con nombre cental_view.jpg y cenital_view.txt
        cv2.imwrite(f"torres/{task_name}/cenital_view.jpg", imageCenital)

        # Guardar angle_to_north y pix2cm en un dict
        infoCenital = {"angle_to_north": angle_to_north, "pix2cm": pix2cm}
        with open(f"torres/{task_name}/cenital_view.json", "w") as f:
            json.dump(infoCenital, f)

        report_dict = {}
        IDAnte = -1
        IDantena = -1

        for filename in tqdm(filenames, desc="Procesando Detecciones"):
            if not filename.endswith(".txt"):
                image_path = os.path.join(rootPath, filename)
                label_path = filename.split(".")[0] + ".txt"
                IDantena = detectImg(
                    image_path,
                    os.path.join(labelsPath, label_path),
                    cropPath,
                    IDantena,
                )
                IDAnte, report_dict = get_JustReport(
                    os.path.join(labelsPath, label_path),
                    report_dict,
                    IDAnte,
                )

        # Guardar el reporte en un archivo json
        with open(f"torres/{task_name}/reporte.json", "w") as f:
            json.dump(report_dict, f, indent=4)

        report2excelIMG(task_name, cropPath)

        print("Pre-Proceso completado exitosamente! \n \n")
    except Exception as e:
        print(f"Error en el pre-proceso: {e}")
