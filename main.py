import os
from tkinter import filedialog
from utils.functions import *

import json
from dotenv import load_dotenv
import cv2
from utils.downloadCvat import downloadCvat
import matplotlib
from utils.preProceso import preProceso

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
            "\nSELECCIONE EL PASO A REALIZAR: \n 00. Descargar imágenes de CVAT \n 0. Pre-Proceso \n 1. Calcular Azimuth antenas \n 2. Calcular Ancho antenas \n 3. Calcular Alto antenas \n 4. Calcular Altura en Torre \n 5. Actualizar reporte desde excel \n 6. Subir reporte a S3 \n 7. Subir Imágenes de baja calidad \n 8. Borrar archivos locales \n x. Salir del programa\n"
        )
        step = input("Ingrese el paso a realizar: ")

        try:
            if step == "00":
                downloadCvat(task_name)

            elif step == "0":
                preProceso(task_name)

            # Calcular Azimuth de las antenas
            elif step == "1":
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

                    imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)
                    option = input(
                        "Deseas calcular de una antena en específico? (y/N):"
                    )

                    if option == "y":
                        key = input("Ingrese el ID de la antena a calcular:")
                        filename = report_dict[key]["Filename"]
                        image_path = os.path.join(rootPath, f"{filename}.JPG")
                        label_info = report_dict[key]["Label"]
                        metadata = read_metadata(
                            os.path.join(metadataPath, f"{filename}.txt")
                        )
                        yawDegrees = float(metadata["GimbalYawDegree"])
                        modelo = metadata["Model"]
                        imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                        imageWidth = imageFrontalData.shape[1]
                        imageHeight = imageFrontalData.shape[0]
                        imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                        angle = calculate_angle(
                            imageCenital, imageBBOX, -angle_to_north
                        )
                        if angle != -1212:
                            report_dict[key]["Azimuth"] = angle
                            with open(f"torres/{task_name}/reporte.json", "w") as f:
                                json.dump(report_dict, f, indent=4)

                            report2excelIMG(task_name, cropPath)

                    else:
                        for key in report_dict.keys():
                            filename = report_dict[key]["Filename"]
                            image_path = os.path.join(rootPath, f"{filename}.JPG")
                            label_info = report_dict[key]["Label"]
                            metadata = read_metadata(
                                os.path.join(metadataPath, f"{filename}.txt")
                            )
                            yawDegrees = float(metadata["GimbalYawDegree"])
                            modelo = metadata["Model"]
                            imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                            imageWidth = imageFrontalData.shape[1]
                            imageHeight = imageFrontalData.shape[0]
                            imageBBOX = drawbbox(
                                imageFrontalData, label_info, yawDegrees
                            )
                            angle = calculate_angle(
                                imageCenital, imageBBOX, -angle_to_north
                            )
                            if angle != -1212:
                                report_dict[key]["Azimuth"] = angle
                                with open(f"torres/{task_name}/reporte.json", "w") as f:
                                    json.dump(report_dict, f, indent=4)

                                report2excelIMG(task_name, cropPath)

                    with open(f"torres/{task_name}/reporte.json", "w") as f:
                        json.dump(report_dict, f, indent=4)

                    report2excelIMG(task_name, cropPath)

                    print("Azimuth calculado exitosamente! \n \n")
                except Exception as e:
                    print(f"Error al calcular Azimuth: {e}")

            elif step == "2":
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

                    imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)
                    option = input(
                        "Deseas calcular de una antena en específico? (y/N):"
                    )

                    if option == "y":
                        key = input("Ingrese el ID de la antena a calcular:")
                        filename = report_dict[key]["Filename"]
                        image_path = os.path.join(rootPath, f"{filename}.JPG")
                        label_info = report_dict[key]["Label"]
                        metadata = read_metadata(
                            os.path.join(metadataPath, f"{filename}.txt")
                        )
                        yawDegrees = float(metadata["GimbalYawDegree"])
                        modelo = metadata["Model"]
                        imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                        imageWidth = imageFrontalData.shape[1]
                        imageHeight = imageFrontalData.shape[0]
                        imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                        width = calculate_width(imageCenital, imageBBOX, pix2cm)
                        print(f"Ancho Antena: {width} cm")
                        if width != -1212:
                            report_dict[key]["Ancho"] = width / 100
                            with open(f"torres/{task_name}/reporte.json", "w") as f:
                                json.dump(report_dict, f, indent=4)

                            report2excelIMG(task_name, cropPath)

                    else:

                        for key in report_dict.keys():
                            filename = report_dict[key]["Filename"]
                            image_path = os.path.join(rootPath, f"{filename}.JPG")
                            label_info = report_dict[key]["Label"]
                            metadata = read_metadata(
                                os.path.join(metadataPath, f"{filename}.txt")
                            )
                            yawDegrees = float(metadata["GimbalYawDegree"])
                            modelo = metadata["Model"]
                            imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                            imageWidth = imageFrontalData.shape[1]
                            imageHeight = imageFrontalData.shape[0]
                            imageBBOX = drawbbox(
                                imageFrontalData, label_info, yawDegrees
                            )
                            width = calculate_width(imageCenital, imageBBOX, pix2cm)
                            print(f"Ancho Antena: {width} cm")
                            if width != -1212:
                                report_dict[key]["Ancho"] = width / 100
                                with open(f"torres/{task_name}/reporte.json", "w") as f:
                                    json.dump(report_dict, f, indent=4)

                                report2excelIMG(task_name, cropPath)

                    with open(f"torres/{task_name}/reporte.json", "w") as f:
                        json.dump(report_dict, f, indent=4)

                    report2excelIMG(task_name, cropPath)

                    print("Ancho calculado exitosamente! \n \n")
                except Exception as e:
                    print(f"Error al calcular Ancho: {e}")

            elif step == "3":
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

                    imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)

                    option = input(
                        "Deseas calcular de una antena en específico? (y/N):"
                    )

                    if option == "y":

                        key = input("Ingrese el ID de la antena a calcular:")
                        filename = report_dict[key]["Filename"]
                        image_path = os.path.join(rootPath, f"{filename}.JPG")
                        label_info = report_dict[key]["Label"]
                        metadata = read_metadata(
                            os.path.join(metadataPath, f"{filename}.txt")
                        )
                        yawDegrees = float(metadata["GimbalYawDegree"])
                        modelo = metadata["Model"]
                        imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                        imageWidth = imageFrontalData.shape[1]
                        imageHeight = imageFrontalData.shape[0]
                        imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                        width = report_dict[key]["Ancho"]
                        if width != None:
                            width = width * 100
                            pix2cm = select_width(imageBBOX, width)
                            if pix2cm != None:
                                cmAlto = calculate_high(imageBBOX, pix2cm)
                                if cmAlto != -1212:
                                    print(f"Alto Antena: {cmAlto} cm")
                                    report_dict[key]["Alto"] = cmAlto / 100
                                    with open(
                                        f"torres/{task_name}/reporte.json", "w"
                                    ) as f:
                                        json.dump(report_dict, f, indent=4)

                                    report2excelIMG(task_name, cropPath)

                    else:

                        for key in report_dict.keys():
                            filename = report_dict[key]["Filename"]
                            image_path = os.path.join(rootPath, f"{filename}.JPG")
                            label_info = report_dict[key]["Label"]
                            metadata = read_metadata(
                                os.path.join(metadataPath, f"{filename}.txt")
                            )
                            yawDegrees = float(metadata["GimbalYawDegree"])
                            modelo = metadata["Model"]
                            imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                            imageWidth = imageFrontalData.shape[1]
                            imageHeight = imageFrontalData.shape[0]
                            imageBBOX = drawbbox(
                                imageFrontalData, label_info, yawDegrees
                            )
                            width = report_dict[key]["Ancho"]
                            if width != None:
                                width = width * 100
                                pix2cm = select_width(imageBBOX, width)
                                if pix2cm != None:
                                    cmAlto = calculate_high(imageBBOX, pix2cm)
                                    if cmAlto != -1212:
                                        print(f"Alto Antena: {cmAlto} cm")
                                        report_dict[key]["Alto"] = cmAlto / 100
                            with open(f"torres/{task_name}/reporte.json", "w") as f:
                                json.dump(report_dict, f, indent=4)

                            report2excelIMG(task_name, cropPath)

                    with open(f"torres/{task_name}/reporte.json", "w") as f:
                        json.dump(report_dict, f, indent=4)

                    report2excelIMG(task_name, cropPath)
                except Exception as e:
                    print(f"Error al calcular Alto: {e}")

            elif step == "4":
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
                    imageCenital, angle_to_north, pix2cm = getCenitalInfo(task_name)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)

                    alturaTorre = int(input("Ingrese la altura de referencia en cm: "))

                    option = input(
                        "Deseas calcular de una antena en específico? (y/N): "
                    )
                    if option == "y":
                        print(
                            "\n Desas calcular el alto en la torre con:\n\n 1. Alto de la antena\n 2. Imagen General de la torre"
                        )
                        option2 = input("\nIngresa opción: ")

                        if option2 == "1":

                            key = input("Ingrese el ID de la antena a calcular:")
                            filename = report_dict[key]["Filename"]
                            image_path = os.path.join(rootPath, f"{filename}.JPG")
                            label_info = report_dict[key]["Label"]
                            metadata = read_metadata(
                                os.path.join(metadataPath, f"{filename}.txt")
                            )
                            yawDegrees = float(metadata["GimbalYawDegree"])
                            modelo = metadata["Model"]
                            imageFrontalData = fixDistor(cv2.imread(image_path), modelo)
                            imageWidth = imageFrontalData.shape[1]
                            imageHeight = imageFrontalData.shape[0]
                            imageBBOX = drawbbox(
                                imageFrontalData, label_info, yawDegrees
                            )
                            altoAntena = report_dict[key]["Alto"]
                            if altoAntena != None:
                                altoAntena = altoAntena * 100
                                highPoint = hightPointTower(imageBBOX)
                                if highPoint != -1212:
                                    px2cm, puntoMedio = calculate_hightOnTower(
                                        imageFrontalData, altoAntena
                                    )

                                    if px2cm != -1212 and puntoMedio != -1212:
                                        # Calcular solo la distancia en eje y
                                        dist = abs(puntoMedio[1] - highPoint[1])
                                        distCm = dist * px2cm
                                        # dist = np.linalg.norm(
                                        #     np.array(puntoMedio) - np.array(highPoint)
                                        # )
                                        # distCm = dist * px2cm
                                        if highPoint[1] > puntoMedio[1]:
                                            Hcentro = int(alturaTorre) + int(distCm)
                                            Hinicial = Hcentro - (altoAntena / 2)
                                            Hfinal = Hcentro + (altoAntena / 2)
                                            report_dict[key]["H centro"] = Hcentro / 100
                                            report_dict[key]["H inicial"] = (
                                                Hinicial / 100
                                            )
                                            report_dict[key]["H final"] = Hfinal / 100
                                        else:
                                            Hcentro = int(alturaTorre) - int(distCm)
                                            Hinicial = Hcentro - (altoAntena / 2)
                                            Hfinal = Hcentro + (altoAntena / 2)
                                            report_dict[key]["H centro"] = Hcentro / 100
                                            report_dict[key]["H inicial"] = (
                                                Hinicial / 100
                                            )
                                            report_dict[key]["H final"] = Hfinal / 100
                                        print(f"H centro: {Hcentro} cm")
                                        with open(
                                            f"torres/{task_name}/reporte.json", "w"
                                        ) as f:
                                            json.dump(report_dict, f, indent=4)

                                        report2excelIMG(task_name, cropPath)

                        elif option2 == "2":
                            try:
                                keyAntena = input(
                                    "Ingrese el ID de la antena a calcular:"
                                )
                                if not os.path.exists(
                                    f"torres/{task_name}/general_view.jpg"
                                ):
                                    imageGeneralPath = filedialog.askopenfilename(
                                        title="Seleccione Vista General",
                                        initialdir=f"torres/{task_name}",
                                    )
                                    imageGeneral = cv2.imread(imageGeneralPath)
                                    cv2.imwrite(
                                        f"torres/{task_name}/general_view.jpg",
                                        imageGeneral,
                                    )
                                else:
                                    imageGeneral = cv2.imread(
                                        f"torres/{task_name}/general_view.jpg"
                                    )

                                pix2cm = select_cmRefT(imageGeneral, alturaTorre)
                                Hcentro = calculate_high(imageGeneral, pix2cm)
                                if Hcentro != -1212:
                                    report_dict[keyAntena]["H centro"] = Hcentro / 100
                                    altoAntena = report_dict[keyAntena]["Alto"]
                                    altoAntena = altoAntena * 100
                                    Hinicial = Hcentro - (altoAntena / 2)
                                    Hfinal = Hcentro + (altoAntena / 2)
                                    report_dict[keyAntena]["H inicial"] = Hinicial / 100
                                    report_dict[keyAntena]["H final"] = Hfinal / 100

                                print(f"H centro: {Hcentro} cm")
                                with open(f"torres/{task_name}/reporte.json", "w") as f:
                                    json.dump(report_dict, f, indent=4)

                                report2excelIMG(task_name, cropPath)
                            except Exception as e:
                                print(
                                    f"Error al calcular altura específica de la antena: {e}"
                                )
                    else:
                        try:
                            initialkey = input(
                                "Ingrese el ID de la antena inicial a calcular:"
                            )
                            # report_dict.keys()
                            for key in range(int(initialkey), len(report_dict.keys())):
                                key = str(key)
                                filename = report_dict[key]["Filename"]
                                image_path = os.path.join(rootPath, f"{filename}.JPG")
                                label_info = report_dict[key]["Label"]
                                metadata = read_metadata(
                                    os.path.join(metadataPath, f"{filename}.txt")
                                )
                                yawDegrees = float(metadata["GimbalYawDegree"])
                                modelo = metadata["Model"]
                                imageFrontalData = fixDistor(
                                    cv2.imread(image_path), modelo
                                )
                                imageWidth = imageFrontalData.shape[1]
                                imageHeight = imageFrontalData.shape[0]
                                imageBBOX = drawbbox(
                                    imageFrontalData, label_info, yawDegrees
                                )
                                altoAntena = report_dict[key]["Alto"]
                                if altoAntena != None:
                                    altoAntena = altoAntena * 100
                                    highPoint = hightPointTower(imageBBOX)
                                    if highPoint != None:
                                        px2cm, puntoMedio = calculate_hightOnTower(
                                            imageFrontalData, altoAntena
                                        )

                                        if px2cm != -1212 and puntoMedio != -1212:
                                            dist = abs(puntoMedio[1] - highPoint[1])
                                            distCm = dist * px2cm
                                            if highPoint[1] > puntoMedio[1]:
                                                Hcentro = int(alturaTorre) + int(distCm)
                                                Hinicial = Hcentro - (altoAntena / 2)
                                                Hfinal = Hcentro + (altoAntena / 2)
                                                report_dict[key]["H centro"] = (
                                                    Hcentro / 100
                                                )
                                                report_dict[key]["H inicial"] = (
                                                    Hinicial / 100
                                                )
                                                report_dict[key]["H final"] = (
                                                    Hfinal / 100
                                                )
                                            else:
                                                Hcentro = int(alturaTorre) - int(distCm)
                                                Hinicial = Hcentro - (altoAntena / 2)
                                                Hfinal = Hcentro + (altoAntena / 2)
                                                report_dict[key]["H centro"] = (
                                                    Hcentro / 100
                                                )
                                                report_dict[key]["H inicial"] = (
                                                    Hinicial / 100
                                                )
                                                report_dict[key]["H final"] = (
                                                    Hfinal / 100
                                                )
                                            print(f"H centro: {Hcentro} cm")
                                            with open(
                                                f"torres/{task_name}/reporte.json", "w"
                                            ) as f:
                                                json.dump(report_dict, f, indent=4)

                                            report2excelIMG(task_name, cropPath)
                        except Exception as e:
                            print(
                                f"Error al calcular altura general de las antenas: {e}"
                            )

                    with open(f"torres/{task_name}/reporte.json", "w") as f:
                        json.dump(report_dict, f, indent=4)

                    report2excelIMG(task_name, cropPath)
                except Exception as e:
                    print(f"Error al calcular altura en torre: {e}")

            elif step == "5":
                try:
                    levID, medID, task_name = taskInput(task_name)
                    os.makedirs(f"torres/{task_name}", exist_ok=True)
                    csv_to_json(task_name)
                    print("Reporte actualizado exitosamente!\n \n")
                except Exception as e:
                    print(f"Error al actualizar reporte: {e}")

            elif step == "6":
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
                    option = input("Quieres subir las imágenes de baja calidad? (y/N):")
                    if option == "y":
                        lowImgCvat(
                            AWS_ACCESS_KEY_ID,
                            AWS_SECRET_ACCESS_KEY,
                            AWS_DEFAULT_REGION,
                            AWS_BUCKET,
                            task_name,
                        )

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
                except Exception as e:
                    print(f"Error al subir reporte a S3: {e}")

            elif step == "7":
                try:

                    levID, medID, task_name = taskInput(task_name)

                    if os.path.exists(f"torres/{task_name}/train.txt"):
                        lowImgCvat(
                            AWS_ACCESS_KEY_ID,
                            AWS_SECRET_ACCESS_KEY,
                            AWS_DEFAULT_REGION,
                            AWS_BUCKET,
                            task_name,
                        )
                    else:
                        lowImgS3(
                            AWS_ACCESS_KEY_ID,
                            AWS_SECRET_ACCESS_KEY,
                            AWS_DEFAULT_REGION,
                            AWS_BUCKET,
                            task_name,
                        )
                    print("Imágenes de baja calidad subidas a S3 exitosamente!\n \n")
                except Exception as e:
                    print(f"Error al subir imágenes a S3: {e}")

            elif step == "8":
                print("\nHas seleccionado borrar los archivos locales")
                print(
                    f"Se eliminarán los archivos de la task seleccionada, asegurate de haber terminado el procesamiento antes de continuar"
                )
                option = input(
                    "Estas seguro que deseas borrar los archivos locales? (y/N):"
                )
                if option == "y":
                    try:
                        levID, medID, task_name = taskInput(task_name)
                        if not os.path.exists(f"torres/{task_name}/uploaded.txt"):
                            print("\n")
                            print("¡¡CUIDADO!!")
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
                            print("Estas a punto de eliminar los archivos locales")
                            option3 = input("Estas seguro que deseas continuar? (y/N):")
                            if option3 == "y":
                                os.system(f"rm -r torres/{task_name}")
                                os.system(f"rm torres/{task_name}.zip")
                                print("Archivos locales eliminados!\n \n")
                    except Exception as e:
                        print(f"Error al eliminar archivos locales: {e}")

                else:
                    print("No se ha eliminado ningún archivo\n \n")

            elif step == "x":
                print("Saliendo del programa...")
                break

            else:
                print("Opción no válida\n \n")
                continue

        except Exception as e:
            print(f"Se ha producido un error: {e}")
