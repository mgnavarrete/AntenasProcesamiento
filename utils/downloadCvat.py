from utils.functions import *
from dotenv import load_dotenv
import shutil
from utils.metadata import get_metadata


def downloadCvat(task_name):

    load_dotenv()
    # Parámetros de conexión
    CVAT_HOST = os.getenv("CVAT_HOST")
    CVAT_USERNAME = os.getenv("CVAT_USERNAME")
    CVAT_PASSWORD = os.getenv("CVAT_PASSWORD")

    try:
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
                    os.path.join(imagesPath, file),
                    os.path.join(labelsPath, file),
                )
        get_metadata([f"torres/{task_name}/obj_train_data/{levID}/{medID}"])
        print("Imágenes descargadas exitosamente!")
    except Exception as e:
        print(f"Error al descargar imágenes: {e}")
