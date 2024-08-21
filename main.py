import os
from tkinter import filedialog
from utils.functions import *
from tqdm import tqdm
import json
from dotenv import load_dotenv
import shutil
import cv2
from utils.metadata import get_metadata
import matplotlib


if __name__ == "__main__":
    matplotlib.use("TkAgg")

    os.makedirs("torres", exist_ok=True)

    # Carga las variables del archivo .env
    load_dotenv()
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    AWS_BUCKET = os.getenv("AWS_BUCKET")

    # Parámetros de conexión
    CVAT_HOST = os.getenv("CVAT_HOST")
    CVAT_USERNAME = os.getenv("CVAT_USERNAME")
    CVAT_PASSWORD = os.getenv("CVAT_PASSWORD")
    task_name = ""

    while True:
        print(
            "\nSELECCIONE EL PASO A REALIZAR: \n 00. Descargar imágenes de CVAT \n 0. Pre-Proceso \n 1. Calcular Azimuth antenas \n 2. Calcular Ancho antenas \n 3. Calcular Alto antenas \n 4. Calcular Altura en Torre \n 5. Actualizar reporte desde excel \n 6. Subir reporte a S3 \n 7. Borrar archivos locales \n x. Salir del programa\n"
        )
        step = input("Ingrese el paso a realizar: ")

        # Descargar imágenes de CVAT
        if step == "00":

            # Conectar a CVAT
            client = connect_to_cvat(CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD)
            levID, medID, task_name = taskInput(task_name)
            downloadZip(client, task_name, CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD)
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

            os.makedirs(cropPath, exist_ok=True)

            os.makedirs(labelsPath, exist_ok=True)
            images = os.listdir(imagesPath)
            for file in images:
                if file.endswith(".txt"):
                    # Mover el archivo a la carpeta labels shutil
                    shutil.move(
                        os.path.join(imagesPath, file), os.path.join(labelsPath, file)
                    )
            get_metadata([f"torres/{task_name}/obj_train_data/{levID}/{medID}"])
            print("Imágenes descargadas exitosamente!")

        elif step == "0":
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
                title="Seleccione Vista Cenital", initialdir=f"torres/{task_name}"
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
                        os.path.join(labelsPath, label_path), report_dict, IDAnte
                    )

            # Guardar el reporte en un archivo json
            with open(f"torres/{task_name}/reporte.json", "w") as f:
                json.dump(report_dict, f, indent=4)

            report2excelIMG(task_name, cropPath)

            print("Pre-Proceso completado exitosamente! \n \n")

        # Calcular Azimuth de las antenas
        elif step == "1":
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

            imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
            with open(f"torres/{task_name}/reporte.json", "r") as f:
                report_dict = json.load(f)

            for key in report_dict.keys():
                filename = report_dict[key]["Filename"]
                image_path = os.path.join(rootPath, f"{filename}.JPG")
                label_info = report_dict[key]["Label"]
                metadata = read_metadata(os.path.join(metadataPath, f"{filename}.txt"))
                yawDegrees = float(metadata["GimbalYawDegree"])
                modelo = metadata["Model"]
                imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                imageWidth = imageFrontalData.shape[1]
                imageHeight = imageFrontalData.shape[0]
                imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                angle = calculate_angle(imageCenital, imageBBOX, -angle_to_north)
                report_dict[key]["Azimuth"] = angle

            with open(f"torres/{task_name}/reporte.json", "w") as f:
                json.dump(report_dict, f, indent=4)

            report2excelIMG(task_name, cropPath)

            print("Azimuth calculado exitosamente! \n \n")

        elif step == "2":
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

            imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
            with open(f"torres/{task_name}/reporte.json", "r") as f:
                report_dict = json.load(f)

            for key in report_dict.keys():
                filename = report_dict[key]["Filename"]
                image_path = os.path.join(rootPath, f"{filename}.JPG")
                label_info = report_dict[key]["Label"]
                metadata = read_metadata(os.path.join(metadataPath, f"{filename}.txt"))
                yawDegrees = float(metadata["GimbalYawDegree"])
                modelo = metadata["Model"]
                imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                imageWidth = imageFrontalData.shape[1]
                imageHeight = imageFrontalData.shape[0]
                imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                width = calculate_width(imageCenital, imageBBOX, pix2cm)
                report_dict[key]["Ancho"] = width

            with open(f"torres/{task_name}/reporte.json", "w") as f:
                json.dump(report_dict, f, indent=4)

            report2excelIMG(task_name, cropPath)

            print("Ancho calculado exitosamente! \n \n")

        elif step == "3":
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

            imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
            with open(f"torres/{task_name}/reporte.json", "r") as f:
                report_dict = json.load(f)

            for key in report_dict.keys():
                filename = report_dict[key]["Filename"]
                image_path = os.path.join(rootPath, f"{filename}.JPG")
                label_info = report_dict[key]["Label"]
                metadata = read_metadata(os.path.join(metadataPath, f"{filename}.txt"))
                yawDegrees = float(metadata["GimbalYawDegree"])
                modelo = metadata["Model"]
                imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                imageWidth = imageFrontalData.shape[1]
                imageHeight = imageFrontalData.shape[0]
                imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                width = report_dict[key]["Ancho"]
                if width != None:
                    pix2cm = select_width(imageBBOX, width)
                    if pix2cm != None:
                        cmAlto = calculate_high(imageBBOX, pix2cm)
                        print(f"Alto Antena: {cmAlto} cm")
                        report_dict[key]["Alto"] = cmAlto

            with open(f"torres/{task_name}/reporte.json", "w") as f:
                json.dump(report_dict, f, indent=4)

            report2excelIMG(task_name, cropPath)

        elif step == "4":
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
            imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
            with open(f"torres/{task_name}/reporte.json", "r") as f:
                report_dict = json.load(f)

            alturaTorre = input("Ingrese la altura de la torre en cm:")

            for key in report_dict.keys():
                filename = report_dict[key]["Filename"]
                image_path = os.path.join(rootPath, f"{filename}.JPG")
                label_info = report_dict[key]["Label"]
                metadata = read_metadata(os.path.join(metadataPath, f"{filename}.txt"))
                yawDegrees = float(metadata["GimbalYawDegree"])
                modelo = metadata["Model"]
                imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                imageWidth = imageFrontalData.shape[1]
                imageHeight = imageFrontalData.shape[0]
                imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                altoAntena = report_dict[key]["Alto"]
                if altoAntena != None:
                    highPoint = hightPointTower(imageBBOX)
                    if highPoint != None:
                        px2cm, puntoMedio = calculate_hightOnTower(
                            imageFrontalData, altoAntena
                        )
                        if px2cm != None and puntoMedio != None:
                            dist = np.linalg.norm(
                                np.array(puntoMedio) - np.array(highPoint)
                            )
                            distCm = dist * px2cm
                            Hcentro = int(alturaTorre) - int(distCm)
                            Hinicial = Hcentro - (altoAntena / 2)
                            Hfinal = Hcentro + (altoAntena / 2)
                            report_dict[key]["H centro"] = Hcentro
                            report_dict[key]["H inicial"] = Hinicial
                            report_dict[key]["H final"] = Hfinal

            with open(f"torres/{task_name}/reporte.json", "w") as f:
                json.dump(report_dict, f, indent=4)

            report2excelIMG(task_name, cropPath)

        elif step == "5":
            levID, medID, task_name = taskInput(task_name)
            os.makedirs(f"torres/{task_name}", exist_ok=True)
            csv_to_json(task_name)
            print("Reporte actualizado exitosamente!\n \n")

        elif step == "6":
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

            subirReporte(
                AWS_ACCESS_KEY_ID,
                AWS_SECRET_ACCESS_KEY,
                AWS_DEFAULT_REGION,
                AWS_BUCKET,
                task_name,
                s3_reporte,
            )
            print("Reporte subido a S3 exitosamente!\n \n")
            # Archivo de control para saber si se ha subido el reporte
            open(f"torres/{task_name}/uploaded.txt", "w").close()

        elif step == "7":
            print("\nHas seleccionado borrar los archivos locales")
            print(
                f"Se eliminarán los archivos de la task seleccionada, asegurate de haber terminado el procesamiento antes de continuar"
            )
            option = input(
                "Estas seguro que deseas borrar los archivos locales? (y/N):"
            )
            if option == "y":
                levID, medID, task_name = taskInput(task_name)
                if not os.path.exists(f"torres/{task_name}/uploaded.txt"):
                    print("\n")
                    print("IMPORTANTE")
                    print(
                        f"Se ha detectado que el reporte de {task_name} no ha sido subido a S3"
                    )
                    option2 = input("Estas seguro que deseas continuar? (y/N):")
                    if option2 == "y":
                        # Eliminar el archivo zip y la carpeta descomprimida
                        os.system(f"rm -r torres/{task_name}")
                        os.system(f"rm torres/{task_name}.zip")
                        print("Archivos locales eliminados!\n \n")
                elif os.path.exists(f"torres/{task_name}/uploaded.txt"):
                    # Eliminar el archivo zip y la carpeta descomprimida
                    os.system(f"rm -r torres/{task_name}")
                    os.system(f"rm torres/{task_name}.zip")
                    print("Archivos locales eliminados!\n \n")

            else:
                print("No se ha eliminado ningún archivo\n \n")

        elif step == "x":
            print("Saliendo del programa...")
            break

        else:
            print("Opción no válida\n \n")
            continue
