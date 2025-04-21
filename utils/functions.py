import os
from cvat_sdk import Client
from cvat_sdk.api_client import Configuration, ApiClient
from time import sleep
import json
import matplotlib.pyplot as plt
import numpy as np
import cv2
import lensfunpy
import boto3
from botocore.exceptions import NoCredentialsError
import os
import boto3
from botocore.exceptions import NoCredentialsError
import json
import cv2
import pandas as pd
from tkinter import filedialog
import math
from tqdm import tqdm


def read_metadata(file_path):
    with open(file_path, "r") as file:
        metadata = json.load(file)
    return metadata


def connect_to_cvat(host, username, password):
    """Conecta al servidor CVAT y retorna el objeto de cliente."""
    print(f"Conectando a {host}...")
    client = Client(host)
    client.login((username, password))
    print("Conexión exitosa!")
    return client


def find_task(client, task_name):
    """Busca una tarea por nombre y retorna la primera coincidencia."""
    tasks = client.tasks.list()
    for task in tasks:
        if task.name == task_name:
            print(f"Tarea encontrada: {task_name}")
            return task

    if not tasks:
        raise ValueError(f"No se encontró la tarea con el nombre '{task_name}'")
    return None


def get_dataset(task, CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD):
    """Obtiene el nombre del archivo de imagen para un marco específico."""
    configuration = Configuration(
        host=CVAT_HOST,
        username=CVAT_USERNAME,
        password=CVAT_PASSWORD,
    )
    with ApiClient(configuration) as api_client:
        # Export a task as a dataset
        while True:
            (_, response) = api_client.tasks_api.retrieve_dataset(
                id=task.id,
                format="YOLO 1.1",
                _parse_response=False,
            )
            if response.status == 201:
                print("Respuesta del CVAT recibida!")
                break

            print("Esperando la respuesta del servidor CVAT...")
            sleep(5)

        (_, response) = api_client.tasks_api.retrieve_dataset(
            id=task.id,
            format="YOLO 1.1",
            action="download",
            _parse_response=False,
        )

        # Save the resulting file
        total_size = int(
            response.headers.get("Content-Length", 0)
        )  # Obtener tamaño total del archivo
        chunk_size = 1024  # Tamaño de cada fragmento (1 KB)
        downloaded_size = 0

        with open(f"{task.name}.zip", "wb") as output_file:
            print(
                f"Comenzando a descargar {task.name}.zip ({total_size / 1024 / 1024:.2f} MB)..."
            )
            print("Por favor, espere...")
            for chunk in response.stream(chunk_size):
                if chunk:  # Si el fragmento no está vacío
                    output_file.write(chunk)
                    downloaded_size += len(chunk)
                    print(
                        f"Descargado {downloaded_size / 1024 / 1024:.2f} MB de {total_size / 1024 / 1024:.2f} MB",
                        end="\r",
                    )

            print(f"\n{task.name}.zip descargado!")


# Variables globales para almacenar los puntos de clic
clicked_points = []
nBTN = []


def on_click(event):
    global clicked_points
    if event.key == "c":
        x, y = event.x, event.y
        if event.inaxes:
            clicked_point = (event.xdata, event.ydata)
            clicked_points.append(clicked_point)
            plt.gca().add_patch(plt.Circle(clicked_point, radius=10, color="red"))
            plt.draw()


def on_none_key_pressedW(event):
    global clicked_points
    global nBTN
    if event.key == "n":
        nBTN.append("None")


def on_none_key_pressed(event):
    global clicked_points
    if event.key == "n":
        clicked_points.append("None")

def select_especific_ref(imageCenital, tube_distance_cm):
    global nBTN
    nBTN = []
    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona medida de referencia en imagen")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return 0

    # Calcular la distancia en píxeles del tubo
    tube_distance_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )

    # Relación píxeles a cm
    px_to_cm = tube_distance_cm / tube_distance_px

    print(f"Relación píxeles a cm: {px_to_cm:.4f} cm/px")
    return px_to_cm

def select_width(imageCenital, tube_distance_cm):
    global nBTN
    nBTN = []
    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona el ancho de la antena")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return 0

    # Calcular la distancia en píxeles del tubo
    tube_distance_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )

    # Relación píxeles a cm
    px_to_cm = tube_distance_cm / tube_distance_px

    print(f"Relación píxeles a cm: {px_to_cm:.4f} cm/px")
    return px_to_cm


def select_cmRefT(imageCenital, tube_distance_cm):

    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona la parte de abajo y arriba de la torre")
    plt.axis("off")

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics
    while len(clicked_points) < 2:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    # Calcular la distancia en píxeles del tubo
    tube_distance_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )

    # Relación píxeles a cm
    px_to_cm = tube_distance_cm / tube_distance_px

    print(f"Relación píxeles a cm: {px_to_cm:.4f} cm/px")
    return px_to_cm

def select_center(imageCenital):

    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Seleccionar el centro de la torre")
    plt.axis("off")

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se haga un clic
    while len(clicked_points) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    # Calcular la distancia en píxeles del tubo
    center_px = np.array(clicked_points[0])
    center_px = (int(center_px[0]), int(center_px[1]))



    print(f"Centro de la torre: {center_px}")
    return center_px

def select_cmRef(imageCenital, tube_distance_cm):

    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Seleccionar dos puntos de ref")
    plt.axis("off")

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics
    while len(clicked_points) < 2:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    # Calcular la distancia en píxeles del tubo
    tube_distance_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )

    # Relación píxeles a cm
    px_to_cm = tube_distance_cm / tube_distance_px

    print(f"Relación píxeles a cm: {px_to_cm:.4f} cm/px")
    return px_to_cm


def calculate_high(imageFrontal, pix2cm):
    global clicked_points
    clicked_points = []

    global nBTN
    nBTN = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona la altura de la antena")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return -1212

    distPix = np.linalg.norm(np.array(clicked_points[0]) - np.array(clicked_points[1]))

    # Calcular la distancia en cm
    distCm = distPix * pix2cm

    return distCm

def calculate_width_ref(imageFrontal, pix2cm):
    global clicked_points
    clicked_points = []

    global nBTN
    nBTN = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona la ancho de la antena")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return -1212

    distPix = np.linalg.norm(np.array(clicked_points[0]) - np.array(clicked_points[1]))

    # Calcular la distancia en cm
    distCm = distPix * pix2cm

    return distCm

def calculate_angle_and_width(imageCenital, imageFrontal, yawDegreesCenital, px_to_cm):
    global clicked_points
    clicked_points = []

    # Dibujar en Imagen Cenital en norte SEGUN EL YAW
    cv2.line(
        imageCenital,
        (imageCenital.shape[1] // 2, imageCenital.shape[0] // 2),
        (imageCenital.shape[1] // 2, 0),
        (0, 0, 255),
        2,
    )

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen frontal
    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Frontal")
    plt.axis("off")

    # Mostrar la imagen cenital
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Cenital")
    plt.axis("off")

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    # Calcular el punto medio de los puntos de la antena
    antenna_midpoint = (
        (clicked_points[0][0] + clicked_points[1][0]) / 2,
        (clicked_points[0][1] + clicked_points[1][1]) / 2,
    )

    # Calcular el ancho de la antena en píxeles y convertir a cm
    antenna_width_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )
    antenna_width_cm = antenna_width_px * px_to_cm

    # Centro de la imagen cenital
    h, w, _ = imageCenital.shape
    cx, cy = w / 2, h / 2

    # Coordenadas del punto medio de la antena
    px, py = antenna_midpoint

    # Diferencia en las coordenadas
    dx = px - cx
    dy = (
        cy - py
    )  # Nota: invertimos la coordenada y porque la imagen tiene el origen en la esquina superior izquierda

    # Calcular el ángulo entre el centro y el punto clicado
    alpha = np.arctan2(dy, dx)

    # Ajustar el ángulo según el yaw
    yaw_rad = np.radians(yawDegreesCenital)
    alpha_prime = alpha - yaw_rad

    # Convertir el ángulo ajustado a grados
    alpha_prime_deg = np.degrees(alpha_prime)

    # Normalizar el ángulo para que esté en el rango [0, 360)
    angle = (alpha_prime_deg + 360) % 360

    return round(angle, 1), round(antenna_width_cm, 1)


def calculate_width(imageCenital, imageFrontal, px_to_cm):
    global clicked_points
    clicked_points = []
    global nBTN
    nBTN = []

    # Dibujar en Imagen Cenital en norte SEGUN EL YAW
    cv2.line(
        imageCenital,
        (imageCenital.shape[1] // 2, imageCenital.shape[0] // 2),
        (imageCenital.shape[1] // 2, 0),
        (0, 0, 255),
        2,
    )

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen frontal
    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Frontal")
    plt.axis("off")

    # Mostrar la imagen cenital
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Cenital")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clics (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return -1212

    # Calcular el ancho de la antena en píxeles y convertir a cm
    antenna_width_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )
    antenna_width_cm = antenna_width_px * px_to_cm

    return round(antenna_width_cm, 1)

def calculate_angle(imageCenital, imageFrontal, center, angleTopimg):
    global clicked_points
    clicked_points = []

    # Dibujar en Imagen Cenital en norte SEGUN EL YAW
    cv2.line(
        imageCenital,
        (imageCenital.shape[1] // 2, imageCenital.shape[0] // 2),
        (imageCenital.shape[1] // 2, 0),
        (0, 0, 255),
        2,
    )

    mng = plt.get_current_fig_manager()

    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen frontal
    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Frontal")
    plt.axis("off")

    # Mostrar la imagen cenital
    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(imageCenital, cv2.COLOR_BGR2RGB))
    plt.title("Imagen Cenital")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressed)

    # Conectar el evento de clic a subplot cenital
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se haga un clic o se presione el botón
    while len(clicked_points) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in clicked_points:
        print("El objeto no está visible")
        return -1212, -1212, -1212

    # Calcular el punto medio de los puntos de la antena
    antenna_midpoint = clicked_points[0]

    # Centro de la imagen cenital
    cx, cy = center

    # Coordenadas del punto medio de la antena
    px, py = antenna_midpoint

    antena_angle_img = get_angle(px, py, center, length=1000)
    
    angle = (angleTopimg + antena_angle_img) % 360




    return round(angle, 1), px, py



def get_caras_torre(imageCenitalRaw, imgAngles, center, cantCaras, angleTopimg):
    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageCenitalRaw, cv2.COLOR_BGR2RGB))
    plt.title("Seleccionar Limites de las 4 Caras en Circulo Verde")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressed)

    # Conectar el evento de clic a subplot cenital
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)
    
    # Si se apreta R se termina de seleccioanr puntos
    while len(clicked_points) < int(cantCaras):
        plt.pause(0.1)

 
    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in clicked_points:
        print("El objeto no está visible")
        return -1212

    angleCaras = []

    for point in clicked_points:
  
        # Coordenadas del punto medio de la antena
        px, py = point
 
        antena_angle_img = get_angle(px, py, center, length=1000)
      
      
        
        # print(f"Angulo imagen: {antena_angle_img}")
        
        angle_real = (angleTopimg + antena_angle_img) % 360
        angleCaras.append([antena_angle_img, angle_real])
        

    i = 0
    caras = []
    while i < len(angleCaras):
        if i == len(angleCaras) - 1:

            caras.append([angleCaras[i], angleCaras[0]])
        else:
    
            caras.append([angleCaras[i], angleCaras[i+1]])
        i += 1

    return caras

def identificar_intervalo_invertido(intervalos):
    # Clasificar los intervalos en dos grupos
    mayor = []
    menor = []
    
    for i, (a, b) in enumerate(intervalos):
        if a[1] < b[1]:
            menor.append(i)
        else:
            mayor.append(i)
    
    # Identificar cuál grupo es minoría (el anómalo)
    if len(mayor) == 1:
        return mayor[0]  # Retorna el índice y el intervalo anómalo
    elif len(menor) == 1:
        return menor[0]  # Retorna el índice y el intervalo anómalo
    
    return "Anomalo"

# Función para calcular coordenadas en la imagen según el ángulo
def get_point(yaw_degree, center, length=1000):
    xc = center[0]
    yc = center[1]
    
    # Convertir el ángulo a radianes
    angle_rad = math.radians(yaw_degree)
    
    # Calcular el punto rotado usando las ecuaciones de rotación
    ximg = xc + length * math.sin(angle_rad)  # sin para rotación horaria
    yimg = yc - length * math.cos(angle_rad)  # cos negativo para sistema de coordenadas de imagen
    # print(f"Angulo: {yaw_degree}")
    # print(f"X: {ximg}, Y: {yimg}")
    return int(ximg), int(yimg)

def get_angle(x, y, center, length=1000):
    xTopImg = center[0] 
    yTopImg = center[1] - length
    
    # Calcular vectores a partir de las líneas
    vector1 = [xTopImg - center[0], yTopImg - center[1]]
    vector2 = [x - center[0], y - center[1]]
    
    # Calcular el producto punto y las magnitudes
    dot_product = np.dot(vector1, vector2)
    norm_v1 = np.linalg.norm(vector1)
    norm_v2 = np.linalg.norm(vector2)
    
    # Calcular el ángulo
    cos_theta = dot_product / (norm_v1 * norm_v2)
    theta_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    theta_deg = np.degrees(theta_rad)
    
    # Calcular el producto cruz para determinar la dirección
    # En 2D, el producto cruz es: v1.x * v2.y - v1.y * v2.x
    cross_product = vector1[0] * vector2[1] - vector1[1] * vector2[0]
    
    # Si el producto cruz es negativo, el ángulo es horario
    # Si es positivo, necesitamos restar de 360 para obtener el ángulo horario
    if cross_product < 0:
        theta_deg = - theta_deg
        
    # print(f"Angulo: {theta_deg}")
    return theta_deg

def hightPointTower(imageFrontal):
    global clicked_points
    clicked_points = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Selecciona punto de referencia en la")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressed)

    # Conectar el evento de clic a subplot cenital
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se haga un clic o se presione el botón
    while len(clicked_points) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in clicked_points:
        print("El objeto no está visible")
        return -1212

    altoTorre = clicked_points[0]
    return altoTorre


def calculate_hightOnTower(imageFrontal, cmAltoAntena):
    global clicked_points
    clicked_points = []

    global nBTN
    nBTN = []

    mng = plt.get_current_fig_manager()
    # Poner en pantalla completa de forma automática
    mng.full_screen_toggle()

    # Mostrar la imagen cenital
    plt.imshow(cv2.cvtColor(imageFrontal, cv2.COLOR_BGR2RGB))
    plt.title("Seleccionar altura antena")
    plt.axis("off")

    # Conectar el evento de tecla
    cid_key = plt.gcf().canvas.mpl_connect("key_press_event", on_none_key_pressedW)

    # Conectar el evento de clic
    cid = plt.gcf().canvas.mpl_connect("key_press_event", on_click)

    # Esperar hasta que se hagan dos clicks (para la antena)
    while len(clicked_points) < 2 and len(nBTN) < 1:
        plt.pause(0.1)

    # Desconectar el evento de clic
    plt.gcf().canvas.mpl_disconnect(cid_key)
    plt.gcf().canvas.mpl_disconnect(cid)
    plt.close()

    if "None" in nBTN:
        print("El objeto no está visible")
        return -1212, -1212

    # Calcular la distancia en píxeles
    distance_px = np.linalg.norm(
        np.array(clicked_points[0]) - np.array(clicked_points[1])
    )

    # Relación píxeles a cm
    px_to_cm = cmAltoAntena / distance_px

    punto_medio = (
        (clicked_points[0][0] + clicked_points[1][0]) / 2,
        (clicked_points[0][1] + clicked_points[1][1]) / 2,
    )
    return px_to_cm, punto_medio

def drawbbox(
    imageFrontal, label_info, yaw_degree
):  # dibujar el bounding box in imageFrontal
    x_center = float(label_info[1]) * imageFrontal.shape[1]
    y_center = float(label_info[2]) * imageFrontal.shape[0]
    box_width = float(label_info[3]) * imageFrontal.shape[1]
    box_height = float(label_info[4]) * imageFrontal.shape[0]
    x_min = int(x_center - box_width / 2)
    x_max = int(x_center + box_width / 2)
    y_min = int(y_center - box_height / 2)
    y_max = int(y_center + box_height / 2)
    cv2.rectangle(imageFrontal, (x_min, y_min), (x_max, y_max), (255, 0, 0), 10)

    return imageFrontal


def get_JustReport(label_path, report_dict, IDAntena):
    if os.path.exists(label_path):
        with open(label_path, "r") as file:
            labels = file.readlines()
        if len(labels) == 0:
            return IDAntena, report_dict
        else:
            for label in labels:
                IDAntena += 1
                # Formato YOLO: <class_id> <x_center> <y_center> <width> <height>
                label_info = label.split()
                modeloTipo = {0: "RF", 1: "RRU", 2: "Micro Wave"}

                report_dict[IDAntena] = {
                    "Label": label_info,
                    "Modelo": None,
                    "Tipo": modeloTipo[int(label_info[0])],
                    "Alto": None,
                    "Ancho": None,
                    "H centro": None,
                    "H inicial": None,
                    "H final": None,
                    "Azimuth": None,
                    "Cara": None,
                    "Pointx": 0,
                    "Pointy": 0,
                    "Filename": label_path.split("/")[-1].split(".")[0],
                }

            return IDAntena, report_dict


def detectImg(imgPath, labelPath, cropPath, IDantena):
    # Read the first image
    if os.stat(labelPath).st_size == 0:
        return IDantena
    imgOR = cv2.imread(imgPath)
    imgC = cv2.cvtColor(cv2.imread(imgPath), cv2.COLOR_BGR2RGB)
    img1 = cv2.cvtColor(imgC, cv2.COLOR_RGB2GRAY)

    img_height, img_width = img1.shape
    bbox = []

    # Read the corresponding label file
    with open(labelPath, "r") as file:

        for line in file:
            line = line.split()
            _, xc, yc, bw, bh = map(float, line)

            # Calculate bounding box coordinates
            x = int((xc - bw / 2) * img_width)
            y = int((yc - bh / 2) * img_height)
            x2 = int((xc + bw / 2) * img_width)
            y2 = int((yc + bh / 2) * img_height)

            # Ensure the bounding box is within image bounds
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            x2 = max(0, min(x2, img_width - 1))
            y2 = max(0, min(y2, img_height - 1))

            bbox.append([x, y, x2, y2])

    margen = 25
    for x, y, x2, y2 in bbox:
        IDantena += 1
        if x < x2 and y < y2:  # Check for valid bounding box
            x_margen = max(x - margen, 0)
            y_margen = max(y - margen, 0)
            x2_margen = min(x2 + margen, img1.shape[1])
            y2_margen = min(y2 + margen, img1.shape[0])

            # Realizar el corte con el margen añadido
            detection = imgOR[y_margen:y2_margen, x_margen:x2_margen]

            if detection.size > 0:
                cv2.imwrite(f"{cropPath}/{IDantena}.JPG", detection)

    return IDantena


def fixDistor(image, model):

    if model == "MAVIC2-ENTERPRISE-ADVANCEDt":
        fix_image = undistort_m2ea_th(image)
    elif model == "XT2":
        fix_image = undistort_xt2(image)
    elif model == "ZH20T":
        fix_image = undistort_zh20t(image)
    elif model == "M3T":
        fix_image = undistort_m3e_th(image)
    else:
        # print("CÁMARA NO DEFINIDA")
        return image

    return fix_image


def undistort_zh20t(im):
    st = """
    <lensdatabase version="1">

        <mount>
            <name>Pentax K</name>
            <compat>M42</compat>
        </mount>

        <lens>
            <maker>Pentax</maker>
            <model>SMC Pentax M 13.5mm f/1.0</model>
            <mount>Pentax K</mount>
            <cropfactor>1.0</cropfactor>
            <focal value="13.5" />
            <aperture min="1.0" max="1.0" />
            <type>rectilinear</type>
            <calibration>
                <!-- WARNING: this calibration data is completely bogus :) -->
                <distortion model="ptlens" focal="13.5" a="0.01865" b="-0.06932" c="0.05956" />
            </calibration>
        </lens>

        <camera>
            <maker>Pentax</maker>
            <model>Pentax K10D</model>
            <mount>Pentax KAF2</mount>
            <cropfactor>1.0</cropfactor>
        </camera>

    </lensdatabase>"""

    cam_maker = "Pentax"
    cam_model = "Pentax K10D"
    lens_maker = "Pentax"
    lens_model = "SMC Pentax M 13.5mm f/1.0"

    db = lensfunpy.Database(xml=st)
    cam = db.find_cameras(cam_maker, cam_model)[0]
    lens = db.find_lenses(cam, lens_maker, lens_model)[0]
    focal_length = 13.5
    aperture = 1
    distance = 5

    height, width = im.shape[0], im.shape[1]

    mod = lensfunpy.Modifier(lens, cam.crop_factor, width, height)
    mod.initialize(focal_length, aperture, distance)

    undist_coords = mod.apply_geometry_distortion()
    im_undistorted = cv2.remap(im, undist_coords, None, cv2.INTER_LANCZOS4)
    return im_undistorted


def undistort_m2ea_th(im):
    st = """
    <lensdatabase version="1">

        <mount>
            <name>Pentax K</name>
            <compat>M42</compat>
        </mount>

        <lens>
            <maker>Pentax</maker>
            <model>SMC Pentax M 13.5mm f/1.0</model>
            <mount>Pentax K</mount>
            <cropfactor>1.0</cropfactor>
            <focal value="13.5" />
            <aperture min="1.0" max="1.0" />
            <type>rectilinear</type>
            <calibration>
                <!-- WARNING: this calibration data is completely bogus :) -->
                <distortion model="ptlens" focal="9" a="0.02356" b="-0.13063" c="0.13631" />
            </calibration>
        </lens>

        <camera>
            <maker>Pentax</maker>
            <model>Pentax K10D</model>
            <mount>Pentax KAF2</mount>
            <cropfactor>1.0</cropfactor>
        </camera>

    </lensdatabase>"""

    cam_maker = "Pentax"
    cam_model = "Pentax K10D"
    lens_maker = "Pentax"
    lens_model = "SMC Pentax M 13.5mm f/1.0"

    db = lensfunpy.Database(xml=st)
    cam = db.find_cameras(cam_maker, cam_model)[0]
    lens = db.find_lenses(cam, lens_maker, lens_model)[0]
    focal_length = 9
    aperture = 1
    distance = 5

    height, width = im.shape[0], im.shape[1]

    mod = lensfunpy.Modifier(lens, cam.crop_factor, width, height)
    mod.initialize(focal_length, aperture, distance)

    undist_coords = mod.apply_geometry_distortion()
    im_undistorted = cv2.remap(im, undist_coords, None, cv2.INTER_LANCZOS4)
    return im_undistorted


def undistort_m3e_th(im):
    st = """
    <lensdatabase version="1">

        <mount>
            <name>Pentax K</name>
            <compat>M42</compat>
        </mount>

        <lens>
            <maker>Pentax</maker>
            <model>SMC Pentax M 13.5mm f/1.0</model>
            <mount>Pentax K</mount>
            <cropfactor>1.0</cropfactor>
            <focal value="13.5" />
            <aperture min="1.0" max="1.0" />
            <type>rectilinear</type>
            <calibration>
                <!-- WARNING: this calibration data is completely bogus :) -->
                <distortion model="ptlens" focal="9" a="0.02356" b="-0.13063" c="0.13631" />
            </calibration>
        </lens>

        <camera>
            <maker>Pentax</maker>
            <model>Pentax K10D</model>
            <mount>Pentax KAF2</mount>
            <cropfactor>1.0</cropfactor>
        </camera>

    </lensdatabase>"""

    cam_maker = "Pentax"
    cam_model = "Pentax K10D"
    lens_maker = "Pentax"
    lens_model = "SMC Pentax M 13.5mm f/1.0"

    db = lensfunpy.Database(xml=st)
    cam = db.find_cameras(cam_maker, cam_model)[0]
    lens = db.find_lenses(cam, lens_maker, lens_model)[0]
    focal_length = 9
    aperture = 1
    distance = 5

    height, width = im.shape[0], im.shape[1]

    mod = lensfunpy.Modifier(lens, cam.crop_factor, width, height)
    mod.initialize(focal_length, aperture, distance)

    undist_coords = mod.apply_geometry_distortion()
    im_undistorted = cv2.remap(im, undist_coords, None, cv2.INTER_LANCZOS4)
    return im_undistorted


def undistort_xt2(img):
    w = 640
    h = 512
    # camera matrix parameters
    fx = 1124.53
    fy = 1124.53

    cx = 318.79
    cy = 255.76

    # distorsion parameters
    k1 = 0.310014
    k2 = 0.268621
    k3 = 2.68808

    p1 = 0.0000835738
    p2 = -0.000796806

    # convert for opencv
    mtx = np.matrix([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype="float32")

    dist = np.array([k1, k2, p1, p2, k3], dtype="float32")

    im_undistorted = cv2.undistort(img, mtx, dist)

    return im_undistorted


def getDirectories(task_name):
    levID = task_name.split("-")[0]
    medID = task_name.split("-")[1]

    rootPath = f"torres/{task_name}/obj_train_data/{levID}/{medID}/images"
    imagesPath = f"torres/{task_name}/obj_train_data/{levID}/{medID}/images"
    labelsPath = f"torres/{task_name}/obj_train_data/{levID}/{medID}/labels"
    detectionsPath = f"torres/{task_name}/obj_train_data/{levID}/{medID}/detections"
    s3_labels = f"{levID}/{medID}/labels"
    s3_detections = f"{levID}/{medID}/detections"
    s3_reporte = f"{levID}/{medID}"
    filenames = os.listdir(rootPath)
    cropPath = os.path.join(
        f"torres/{task_name}/obj_train_data/{levID}/{medID}", "crop"
    )
    metadataPath = os.path.join(
        f"torres/{task_name}/obj_train_data/{levID}/{medID}", "metadata"
    )

    return (
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
    )


def downloadZip(
    client, task_name, CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD
):  # Buscar la tarea
    task = find_task(client, task_name)

    if task is None:
        client.logout()
        raise ValueError(f"No se encontró la tarea {task_name}")
    else:
        # Obtener el dataset con lables e imagenes
        get_dataset(task, CVAT_HOST, CVAT_USERNAME, CVAT_PASSWORD)

        # Mover archivo zip a carpeta torres
        os.system(f"mv {task_name}.zip torres/")

        # Cerrar cliente cvat
        client.logout()

        # Correr unzip para descomprimir el archivo y que no haga print de lo que hace
        print(f"Descomprimiendo el archivo {task_name}.zip...")
        os.system(f"unzip torres/{task_name}.zip -d torres/{task_name}")


def taskInput(task_name):
    levID = input("Ingrese el ID del levantamiento: ")
    medID = input("Ingrese el ID de la medición: ")
    task_name = f"{levID}-{medID}"

    return levID, medID, task_name


def getCenitalInfo(task_name):

    imageCenital = cv2.imread(f"torres/{task_name}/cenital_view.jpg")

    with open(f"torres/{task_name}/cenital_view.json", "r") as f:
        infoCenital = json.load(f)
        angle_to_north = infoCenital["angle_to_north"]
        pix2cm = infoCenital["pix2cm"]
        center = infoCenital["center"]
        imgAngles = infoCenital["imgAngles"]
        realAngles = infoCenital["realAngles"]
        allPos = infoCenital["allPos"]
        angleTopimg = infoCenital["angleTopimg"]
    return imageCenital, center, angle_to_north, pix2cm, allPos, imgAngles, realAngles, angleTopimg


def report2excelIMG(task_name, cropPath):
    # Verificar si existe el archivo uploaded.txt
    if os.path.exists(f"torres/{task_name}/uploaded.txt"):
        os.remove(f"torres/{task_name}/uploaded.txt")

    inputReport = f"torres/{task_name}/reporte.json"

    # Cargar los datos JSON
    with open(inputReport) as f:
        data = json.load(f)

    # Convertir los datos JSON a un DataFrame
    df = pd.DataFrame.from_dict(data, orient="index")

    # Función para manejar los valores float y None
    def clean_value(value):
        if value is None:
            return ""
        try:
            return float(value)
        except ValueError:
            return value

    # Aplicar la función a las columnas específicas
    for col in ["Alto", "Ancho", "H centro", "H inicial", "H final", "Azimuth", "Cara", "Pointx", "Pointy"]:
        if col in df.columns:
            df[col] = df[col].apply(clean_value)

    # Agregar columna ID como la primera columna
    df.insert(0, "ID", df.index)

    # Asignar ID del 0 al n
    df["ID"] = range(len(df))

    # Crear una nueva columna 'bboxAntena' vacía
    df["bboxAntena"] = ""

    # Guardar el DataFrame a un archivo Excel utilizando XlsxWriter
    excel_path = f"torres/{task_name}/medidas.xlsx"
    writer = pd.ExcelWriter(excel_path, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]

    # Determinar la columna 'bboxAntena'
    img_col = df.columns.get_loc("bboxAntena")
    file_col = df.columns.get_loc("Filename")
    worksheet.set_column(file_col, file_col, 30)

    # Agregar las imágenes en la columna 'bboxAntena'
    for row in range(
        1, len(df) + 1
    ):  # Comienza en la fila 1 porque la 0 es el encabezado
        img_id = df.iloc[row - 1]["ID"]  # El ID está en la primera columna
        img_path = f"{cropPath}/{img_id}.jpg"

        # Verificar si la imagen existe y agregarla si es así
        try:
            from PIL import Image

            img = Image.open(img_path)
            orig_width, orig_height = img.size
            y_scale = 250 / orig_height
            x_scale = y_scale  # Mantener la relación de aspecto

            worksheet.set_column(img_col, img_col, 35)
            worksheet.set_row(row, 200)
            # Insertar la imagen en la celda específica con escalado
            worksheet.insert_image(
                row, img_col, img_path, {"x_scale": x_scale, "y_scale": y_scale}
            )
        except FileNotFoundError:
            print(f"Imagen no encontrada: {img_path}")
            worksheet.write(row, img_col, "Imagen no encontrada")

    # Guardar los cambios en el archivo Excel
    writer._save()


def csv_to_json(task_name):
    # Load the CSV file
    csvPath = filedialog.askopenfilename(
        title="Selecciona el archivo CSV", initialdir=f"torres/{task_name}"
    )

    # Load the Excel file
    data = pd.read_excel(csvPath, usecols=lambda column: column != "L")

    # Replace NaN with None for the entire dataframe
    data = data.where(pd.notnull(data), None)

    # Ensure the "Modelo" column replaces NaN with "-"
    data["Modelo"] = data["Modelo"].where(pd.notnull(data["Modelo"]), "-")

    report = {}

    def clean_value(value):
        if isinstance(value, str):
            # Replace comma with dot for floats and strip spaces
            value = value.replace(",", ".").strip()
            try:
                return float(value)
            except ValueError:
                return None
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return None

    # Create the report as a dictionary
    for index, row in data.iterrows():
        # Clean and convert the specific columns
        alto = clean_value(row["Alto"])
        ancho = clean_value(row["Ancho"])
        h_centro = clean_value(row["H centro"])
        h_inicial = clean_value(row["H inicial"])
        h_final = clean_value(row["H final"])
        azimuth = clean_value(row["Azimuth"])
        cara = clean_value(row["Cara"])
        pointx = clean_value(row["Pointx"])
        pointy = clean_value(row["Pointy"])
        if pointx == None:
            pointx = 0
        if pointy == None:
            pointy = 0
        label_string = row["Label"]

        report[row["ID"]] = {
            "Label": json.loads(label_string.replace("'", '"')),
            "Modelo": row["Modelo"],
            "Tipo": row["Tipo"],
            "Alto": alto,
            "Ancho": ancho,
            "H centro": h_centro,
            "H inicial": h_inicial,
            "H final": h_final,
            "Azimuth": azimuth,
            "Filename": row["Filename"],
            "Cara": row["Cara"],
            "Pointx": pointx,
            "Pointy": pointy,
        }

    # Convert the dictionary to a JSON formatted string and save it to a file
    with open(f"torres/{task_name}/reporte.json", "w") as file:
        json.dump(report, file, indent=4)

    levID = task_name.split("-")[0]
    medID = task_name.split("-")[1]
    report2excelIMG(
        task_name,
        os.path.join(f"torres/{task_name}/obj_train_data/{levID}/{medID}", "crop"),
    )


def subirReporte(
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_DEFAULT_REGION,
    AWS_BUCKET,
    task_name,
    s3_reporte,
):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )
    try:
        s3.upload_file(
            f"torres/{task_name}/reporte.json", AWS_BUCKET, f"{s3_reporte}/reporte.json"
        )
    except NoCredentialsError:
        print("No se encontraron las credenciales para AWS.")
    except Exception as e:
        print(f"Error al subir el reporte: {str(e)}")


def lowImgCvat(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, AWS_BUCKET, task_name
):

    levID = task_name.split("-")[0]
    medID = task_name.split("-")[1]

    imagesPath = f"torres/{task_name}/obj_train_data/{levID}/{medID}/images"
    lowImg = f"torres/{task_name}/obj_train_data/{levID}/{medID}/comprimida"

    s3_lowImg = f"{levID}/{medID}/comprimida"

    os.makedirs(lowImg, exist_ok=True)
    images = os.listdir(imagesPath)

    for filename in tqdm(images, desc="Bajando calidad IMG"):
        if filename.endswith(".JPG"):

            image_path = os.path.join(imagesPath, filename)
            imgData = cv2.imread(image_path)
            imgResized = cv2.resize(imgData, (870, 650))

            cv2.imwrite(os.path.join(lowImg, filename), imgResized)

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )

    # Recorrer todos los archivos en la carpeta local
    for root, dirs, files in os.walk(lowImg):
        for file in tqdm(files, desc="Subiendo archivos a S3"):
            # Ruta completa al archivo
            local_path = os.path.join(root, file)

            # Generar la clave para el S3
            s3_key = os.path.relpath(
                local_path, lowImg
            )  # Obtener la ruta relativa desde la carpeta local
            s3_full_key = os.path.join(s3_lowImg, s3_key)

            # Subir el archivo al bucket S3
            try:
                s3.upload_file(local_path, AWS_BUCKET, s3_full_key)

            except NoCredentialsError:
                print("No se encontraron las credenciales para AWS.")
            except Exception as e:
                print(f"Error al subir el archivo {file}: {str(e)}")


def lowImgS3(
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, AWS_BUCKET, task_name
):

    rootPath = f"torres/{task_name}"
    os.makedirs(rootPath, exist_ok=True)

    levID = task_name.split("-")[0]
    medID = task_name.split("-")[1]

    imagesPath = f"torres/{task_name}/images"
    os.makedirs(imagesPath, exist_ok=True)
    lowImg = f"torres/{task_name}/comprimida"
    os.makedirs(lowImg, exist_ok=True)

    s3_original = f"{levID}/{medID}/images"

    s3_lowImg = f"{levID}/{medID}/comprimida"

    os.makedirs(lowImg, exist_ok=True)

    # Descargar las imágenes de la carpeta S3_original
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )

    # Listar los objetos en la carpeta
    objects = s3.list_objects_v2(Bucket=AWS_BUCKET, Prefix=s3_original)

    if "Contents" in objects:
        for obj in tqdm(objects["Contents"], desc="Descargando imágenes de S3"):
            # Obtener la ruta del objeto en S3
            s3_key = obj["Key"]

            # Determinar la ruta de destino local
            local_path = os.path.join(
                imagesPath, s3_key[len(s3_original) + 1 :]
            )  # +1 para eliminar el "/" inicial si es necesario

            # Crear directorios locales si no existen
            if not os.path.exists(os.path.dirname(local_path)):
                os.makedirs(os.path.dirname(local_path))

            # Descargar el archivo
            s3.download_file(AWS_BUCKET, s3_key, local_path)

    else:
        print(f"No files found in {s3_original}.")

    images = os.listdir(imagesPath)

    for filename in tqdm(images, desc="Bajando calidad IMG"):
        if filename.endswith(".JPG"):

            image_path = os.path.join(imagesPath, filename)
            imgData = cv2.imread(image_path)
            imgResized = cv2.resize(imgData, (870, 650))

            cv2.imwrite(os.path.join(lowImg, filename), imgResized)

    # Recorrer todos los archivos en la carpeta local
    for root, dirs, files in os.walk(lowImg):
        for file in tqdm(files, desc="Subiendo archivos a S3"):
            # Ruta completa al archivo
            local_path = os.path.join(root, file)

            # Generar la clave para el S3
            s3_key = os.path.relpath(
                local_path, lowImg
            )  # Obtener la ruta relativa desde la carpeta local
            s3_full_key = os.path.join(s3_lowImg, s3_key)

            # Subir el archivo al bucket S3
            try:
                s3.upload_file(local_path, AWS_BUCKET, s3_full_key)

            except NoCredentialsError:
                print("No se encontraron las credenciales para AWS.")
            except Exception as e:
                print(f"Error al subir el archivo {file}: {str(e)}")

if __name__ == "__main__":
    pass
    
    
    
    
    
    
    
    
    
    
    
    
