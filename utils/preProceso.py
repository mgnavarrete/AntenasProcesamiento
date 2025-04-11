from utils.functions import *
import os
from utils.saveGeoMatriz import *
from tkinter import filedialog
import cv2
import numpy as np
import math


def calculate_direction_angles(image_angle):
   
    directions = {
        "Norte": 0,
        "Sur": 180,
        "Este": 90,
        "Oeste": 270
    }
    
    angles_in_image = {}
    
    for direction, real_angle in directions.items():
        # Restar la orientación de la imagen para obtener el ángulo relativo
        relative_angle = (real_angle - image_angle) % 360
        angles_in_image[direction] = relative_angle
    
    return angles_in_image

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
        imageCenitalRaw = imageCenital.copy()
        metadataCenital = read_metadata(metadataPathCenital)
 

        yawDegreesCenital = float(metadataCenital["GimbalYawDegree"])
        modelo = metadataCenital["Model"]
        print(f"Modelo: {modelo}")
        # imageCenital = fixDistor(imageCenital, modelo)
        angle_to_north = -yawDegreesCenital
        
        center = select_center(imageCenital)
       

       # Ajustar el ángulo para que 0° sea el Norte real
        angleTopimg = (yawDegreesCenital + 360) % 360
        print(f"Angle top img: {angleTopimg}")
        
        angles_in_image = calculate_direction_angles(angleTopimg)
        print(f"Angulos en la imagen: {angles_in_image}")


        # Calcular posiciones de los puntos cardinales
        north_pos = get_point(angles_in_image["Norte"], center)
        south_pos = get_point(angles_in_image["Sur"], center)
        east_pos = get_point(angles_in_image["Este"], center)
        west_pos = get_point(angles_in_image["Oeste"], center)
        
        north_angle_real = 0
        south_angle_real = 180
        east_angle_real = 90
        west_angle_real = 270

        # Dibujar líneas en la imagen para cada punto cardinal

        cv2.line(imageCenital, center, north_pos, (0, 0, 255), 15)  # Norte (rojo)
        cv2.line(imageCenital, center, south_pos, (0, 255, 255), 15)  # Sur (amarillo)
        cv2.line(imageCenital, center, east_pos, (255, 0, 0), 15)  # Este (azul)
        cv2.line(imageCenital, center, west_pos, (0, 255, 0), 15)  # Oeste (verde)

        # Etiquetas de los puntos cardinales con los ángulos corregidos
        cv2.putText(imageCenital, "N ({:.1f}), ({:.1f})".format(north_angle_real, angles_in_image["Norte"]), north_pos, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
        cv2.putText(imageCenital, "S ({:.1f}), ({:.1f})".format(south_angle_real, angles_in_image["Sur"]), south_pos, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 255), 15)
        cv2.putText(imageCenital, "E ({:.1f}), ({:.1f})".format(east_angle_real, angles_in_image["Este"]), east_pos, cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 15)
        cv2.putText(imageCenital, "O ({:.1f}), ({:.1f})".format(west_angle_real, angles_in_image["Oeste"]), west_pos, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 15)

        
        pix2cm = 0
        print("Calculando relación pixeles a cm...")
        cmRef = int(
            input("Ingrese la distancia en cm entre los puntos de referencia: ")
        )
        pix2cm = select_cmRef(imageCenital, cmRef)

        # Guardar imagen cenital y metadata en carpeta task_name con nombre cental_view.jpg y cenital_view.txt
        cv2.imwrite(f"torres/{task_name}/cenital_view.jpg", imageCenital)
        cv2.imwrite(f"torres/{task_name}/cenital_view_raw.jpg", imageCenitalRaw)

        # Guardar angle_to_north y pix2cm en un dict
        infoCenital = {"angle_to_north": angle_to_north, 
                       "pix2cm": pix2cm, 
                       "center": center,
                       "angleTopimg": angleTopimg,
                       'imgAngles': [angles_in_image["Norte"], angles_in_image["Sur"], angles_in_image["Este"], angles_in_image["Oeste"]],
                       "realAngles": [north_angle_real, south_angle_real, east_angle_real, west_angle_real],
                       "allPos": [north_pos, south_pos, east_pos, west_pos]}
        
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
