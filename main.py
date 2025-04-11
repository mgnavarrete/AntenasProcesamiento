import os
from tkinter import filedialog
from utils.functions import *
import shutil
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
            "\nSELECCIONE EL PASO A REALIZAR: \n 00. Descargar imágenes de CVAT \n 0. Pre-Proceso \n 1. Calcular Azimuth antenas \n 2. Calcular Ancho antenas \n 3. Calcular Alto antenas \n 4. Calcular Altura en Torre \n 5. Actualizar reporte desde excel \n 6. Subir reporte a S3 \n 7. Subir Imágenes de baja calidad \n 8. Calcular Caras Torre \n 9. Borrar archivos locales \n x. Salir del programa\n"
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

                    imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg = getCenitalInfo(task_name)
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
                        angle, px, py = calculate_angle(
                            imageCenital, imageBBOX, center, angleTopimg
                        )
                        print(f"Punto: {px}, {py}")
                        print(f"Ángulo {key}: {angle:.1f}°")
                        if angle != -1212:
                            report_dict[key]["Azimuth"] = angle
                            
                            report_dict[key]["Pointx"] = int(px)
                            report_dict[key]["Pointy"] = int(py)
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
                            imageBBOX = drawbbox(imageFrontalData, label_info, yawDegrees)
                            angle, px, py = calculate_angle(
                            imageCenital, imageBBOX, center, angleTopimg
                        )
                            print(f"Punto: {px}, {py}")
                            print(f"Ángulo {key}: {angle:.1f}°")
                            if angle != -1212:
                                report_dict[key]["Azimuth"] = angle
                                
                                report_dict[key]["Pointx"] = int(px)
                                report_dict[key]["Pointy"] = int(py)
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

                    imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg = getCenitalInfo(task_name)
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

                    imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg = getCenitalInfo(task_name)
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
                    imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg = getCenitalInfo(task_name)
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
                print("\nHas seleccionado calcular Caras Torre")
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
                     
                    cantCaras = input("Ingrese la cantidad de caras a calcular: ")

                    imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg = getCenitalInfo(task_name)                                   
                    imageCenitalRaw = cv2.imread(f"torres/{task_name}/cenital_view_raw.jpg")  
          
                    # Dubijar circulo verde en el centro de la imagen                  
                    cv2.circle(imageCenitalRaw, center, 1000, (0, 255, 0), 15)
           
                    caras = get_caras_torre(imageCenitalRaw, imgAngles, center, cantCaras, angleTopimg)
                    print(f"Caras Torre: {caras}")
                    nameCaras = ["A", "B", "C", "D"]
                    camaraJSON = {}
                    for i, cara in enumerate(caras):
                        point1 = get_point(cara[0][0], center)
                        point2 = get_point(cara[1][0], center)
                        puntoMediox = (point1[0] + point2[0]) / 2
                        puntoMedioy = (point1[1] + point2[1]) / 2
                        
                        # Dibujar líneas en la imagen para cada punto cardinal
                        cv2.line(imageCenitalRaw, center, point1, (0, 0, 255), 15)  
                        cv2.line(imageCenitalRaw, center, point2, (0, 0, 255), 15)  
                        
                        # Dibujar angulo en la imagen
                        cv2.putText(imageCenitalRaw, nameCaras[i], (int(puntoMediox), int(puntoMedioy)), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 15)
                        cv2.putText(imageCenitalRaw, "({:.1f})".format(cara[0][1]), point1, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
                        cv2.putText(imageCenitalRaw, "({:.1f})".format(cara[1][1]), point2, cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
                        camaraJSON[nameCaras[i]] = {"name": nameCaras[i], "angle_img": cara[0], "angle_real": cara[1]}
                  
                    cv2.imwrite(f"torres/{task_name}/cenital_view_caras.jpg", imageCenitalRaw)
                    
                    with open(f"torres/{task_name}/caras.json", "w") as f:
                        json.dump(camaraJSON, f, indent=4)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)

                    for key in tqdm(report_dict.keys(), desc="Calculando Caras"):
                        
                        if report_dict[key]["Tipo"] == "RF" or report_dict[key]["Tipo"] == "Micro Wave":
                          
                            filename = report_dict[key]["Filename"]
                            image_path = os.path.join(rootPath, f"{filename}.JPG")
                            label_info = report_dict[key]["Label"]
                            metadata = read_metadata(
                                os.path.join(metadataPath, f"{filename}.txt")
                            )
                            yawDegrees = float(metadata["GimbalYawDegree"])
                            # print("Antena: ", key)
                            # print(f"Yaw Degrees: {yawDegrees}")
                            if yawDegrees >= 0:
                                yaw_opuesto = yawDegrees + 180
                            else:
                                yaw_opuesto = yawDegrees + 180
                                if yaw_opuesto > 180:
                                    yaw_opuesto -= 360
                                
                            
                            # print(f"Angulo antena: {yaw_opuesto}")
                            
                            angle_antena = yaw_opuesto
                            report_dict[key]["Azimuth"] = angle_antena
                            intervalo_invertido = identificar_intervalo_invertido(caras)
                            # print(f"Intervalo invertido: {intervalo_invertido}")
                            
                            for i, cara in enumerate(caras): 
                                if intervalo_invertido != i:
                                    if cara[0][1] > cara[1][1]:
                                        if angle_antena <= cara[0][1] and angle_antena >= cara[1][1]:
                                            report_dict[key]["Cara"] = nameCaras[i]
                                            break
                                    else:
                                        if angle_antena <= cara[0][1] and angle_antena >= cara[1][1]:
                                            report_dict[key]["Cara"] = nameCaras[i]
                                            break
                                else:
                                    if cara[0][1] > cara[1][1]:
                                        if angle_antena >= cara[0][1] or angle_antena <= cara[1][1]:
                                            report_dict[key]["Cara"] = nameCaras[i]
                                            break
                                    else:
                                        if angle_antena <= cara[0][1] or angle_antena >= cara[1][1]:
                                            report_dict[key]["Cara"] = nameCaras[i]
                                            break
                            
                        # else:
                        #     intervalo_invertido = identificar_intervalo_invertido(caras)
                        #     angle_antena = report_dict[key]["Azimuth"]
                        #     for i, cara in enumerate(caras): 
                        #         if intervalo_invertido != i:
                        #             if cara[0][1] > cara[1][1]:
                        #                 if angle_antena <= cara[0][1] and angle_antena >= cara[1][1]:
                        #                     report_dict[key]["Cara"] = nameCaras[i]
                        #                     break
                        #             else:
                        #                 if angle_antena <= cara[0][1] and angle_antena >= cara[1][1]:
                        #                     report_dict[key]["Cara"] = nameCaras[i]
                        #                     break
                        #         else:
                        #             if cara[0][1] > cara[1][1]:
                        #                 if angle_antena >= cara[0][1] or angle_antena <= cara[1][1]:
                        #                     report_dict[key]["Cara"] = nameCaras[i]
                        #                     break
                        #             else:
                        #                 if angle_antena <= cara[0][1] or angle_antena >= cara[1][1]:
                        #                     report_dict[key]["Cara"] = nameCaras[i]
                        #                     break

                        with open(f"torres/{task_name}/reporte.json", "w") as f:
                            json.dump(report_dict, f, indent=4)
                        
                        report2excelIMG(task_name, cropPath)
                    
                    report_dict = {}
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)

                except Exception as e:
                    print(f"Error al calcular Caras Torre: {e}")


            elif step == "9":
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
            
            elif step == "g":
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
                     
                    nameCaras = ["A", "B", "C", "D"]
                    for cara in nameCaras:
                        os.makedirs(f"torres/{task_name}/{cara}", exist_ok=True)
                    with open(f"torres/{task_name}/reporte.json", "r") as f:
                        report_dict = json.load(f)
                    for key in tqdm(report_dict.keys(), desc="Copiando imágenes:"):
                        filename = report_dict[key]["Filename"]
                        image_path = os.path.join(rootPath, f"{filename}.JPG")
                        cara = report_dict[key]["Cara"]
                        label_info = report_dict[key]["Label"]
                        metadata = read_metadata(
                            os.path.join(metadataPath, f"{filename}.txt")
                        )
                        yawDegrees = float(metadata["GimbalYawDegree"])
                        cx = float(label_info[1])
                        cy = float(label_info[2])
                        w = float(label_info[3])
                        h = float(label_info[4])
                        data_img = cv2.imread(image_path)
                        imageBBOX = drawbbox(
                                    data_img, label_info, yawDegrees
                                )
                        cv2.putText(imageBBOX, key, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 15)
                    
                        cv2.imwrite(f"torres/{task_name}/{cara}/{filename}_{key}.JPG", imageBBOX)
        
                
                except Exception as e:
                    print(f"Error al calcular Caras Torre: {e}")
                    

            elif step == "x":
                print("Saliendo del programa...")
                break

            else:
                print("Opción no válida\n \n")
                continue

        except Exception as e:
            print(f"Se ha producido un error: {e}")
