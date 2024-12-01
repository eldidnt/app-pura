import cv2
import os
import numpy as np
import tkinter as tk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import time

# Ruta al archivo Haar Cascade
HAAR_CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Crear carpeta de almacenamiento de imágenes si no existe
if not os.path.exists("assets"):
    os.makedirs("assets")

# Configuración de colores
colors = {
    "verde": "#58e27b",
    "azul": "#23617e",
    "morado": "#8866e6",
    "morado_oscuro": "#532fb6",
    "medianoche": "#064663",
    "blanco": "#fdfdfd",
    "negro": "#0c0c0c",
}

# Configuración del correo
remitente = "tucorreo@gmail.com"
destinatario = "correo_destino@gmail.com"
contraseña = "tu_contraseña_o_contraseña_de_aplicación"
smtp_server = 'smtp.gmail.com'
smtp_port = 587


# Función para enviar correo
def enviar_correo(archivo_imagen):
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = "¡Rostro desconocido detectado!"

    # Cuerpo del mensaje
    cuerpo = "Se ha detectado un rostro desconocido. La imagen se adjunta."
    msg.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar la imagen
    with open(archivo_imagen, 'rb') as file:
        img = MIMEImage(file.read())
        msg.attach(img)

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Iniciar TLS
        server.login(remitente, contraseña)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        print(f"Correo enviado exitosamente con la imagen: {archivo_imagen}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

# Inicializar cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    messagebox.showerror("Error", "No se puede acceder a la cámara.")
    cap = None  # Marca que no hay cámara disponible

# Mostrar la cámara en tiempo real en un widget
def actualizar_camara(label_camera):
    if not cap or not cap.isOpened():
        label_camera.after(1000, actualizar_camara, label_camera)  # Reintentar en 1 segundo
        return

    ret, frame = cap.read()
    if ret:
        # Convertir el fotograma a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convertir a imagen compatible con Tkinter
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        label_camera.imgtk = imgtk
        label_camera.configure(image=imgtk)

    label_camera.after(10, actualizar_camara, label_camera)

# Función para cargar imágenes registradas y sus histogramas
def cargar_imagenes_registradas():
    registros = {}
    for archivo in os.listdir("assets"):
        if archivo.endswith(".jpg"):
            ruta = os.path.join("assets", archivo)
            imagen = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
            if imagen is not None:
                histograma = cv2.calcHist([imagen], [0], None, [256], [0, 256])
                registros[archivo[:-4]] = (ruta, histograma)  # Guardar sin extensión .jpg
    return registros

# Función para comparar histogramas
def comparar_histogramas(hist1, hist2):
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)


# Función para capturar una foto
def registrar_nuevo_rostro():
    # Crear una nueva ventana (Toplevel)
    ventana_registro = tk.Toplevel(root)
    ventana_registro.title("Registrar Nuevo Rostro")
    ventana_registro.geometry("800x600")
    ventana_registro.configure(bg=colors["azul"])

    # Contenedor para la cámara
    container_camera = tk.Frame(ventana_registro, bg=colors["medianoche"], width=800, height=400)
    container_camera.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    container_camera.pack_propagate(False)

    label_camera = tk.Label(container_camera, bg=colors["medianoche"])
    label_camera.pack(expand=True, fill="both")

    # Mostrar la cámara en la nueva ventana
    if cap and cap.isOpened():
        actualizar_camara(label_camera)

    # Contenedor para los controles
    container_controls = tk.Frame(ventana_registro, bg=colors["azul"])
    container_controls.pack(side="bottom", fill="x", padx=20, pady=10)

    # Campo de texto para el nombre
    label_nombre = tk.Label(container_controls, text="Nombre:", bg=colors["azul"], fg=colors["blanco"],
                            font=("Poppins", 12))
    label_nombre.pack(side="left", padx=10)

    entry_nombre = tk.Entry(container_controls, font=("Poppins", 12))
    entry_nombre.pack(side="left", fill="x", expand=True, padx=10)

    # Botón para guardar la imagen
    def guardar_rostro():
        if not cap or not cap.isOpened():
            messagebox.showerror("Error", "No se puede acceder a la cámara.")
            return

        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo capturar el fotograma.")
            return

        # Detectar rostros
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = face_cascade.detectMultiScale(gris, 1.1, 4)

        if len(rostros) == 0:
            messagebox.showinfo("Info", "No se detectaron rostros.")
            return

        for (x, y, w, h) in rostros:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Obtener el nombre ingresado
        nombre_archivo = entry_nombre.get().strip()
        if not nombre_archivo:
            messagebox.showwarning("Advertencia", "Por favor, ingresa un nombre antes de guardar.")
            return

        # Guardar la imagen en la carpeta assets
        ruta_completa = os.path.join("assets", nombre_archivo + ".jpg")
        cv2.imwrite(ruta_completa, frame)
        messagebox.showinfo("Guardado", f"Imagen guardada en: {ruta_completa}")
        ventana_registro.destroy()  # Cerrar la ventana después de guardar

    btn_guardar = tk.Button(container_controls, text="Guardar", bg=colors["morado"], fg=colors["blanco"],
                            font=("Poppins", 12), relief="flat", bd=0, activebackground=colors["morado_oscuro"],
                            command=guardar_rostro)
    btn_guardar.pack(side="left", padx=10)


vigilancia_activada = False

# Función para activar el sistema de vigilancia
def activar_sistema():
    # Ocultar el botón de activar sistema
    button2.pack_forget()

    # Crear un nuevo botón para desactivar el sistema
    btnDesactivarSistema = tk.Button(
        container_menu_buttons, 
        text="Desactivar Sistema", 
        bg=colors["morado"], 
        fg=colors["blanco"], 
        font=("Poppins", 14), 
        relief="flat", 
        bd=0, 
        activebackground=colors["morado_oscuro"],
        command=lambda: desactivar_sistema(btnDesactivarSistema)  # Vincular la función para desactivar
    )
    btnDesactivarSistema.pack(fill="x", pady=10)

    # Activar el sistema de verificación de rostros
    global vigilancia_activada
    vigilancia_activada = True  # Cambiar el estado de vigilancia a verdadero

    # Iniciar la captura constante de rostros
    verificar_rostros()

# Función para verificar rostros y enviar correo solo si el rostro es completamente desconocido
def verificar_rostros():
    global vigilancia_activada, rostro_anterior

    if not vigilancia_activada:
        return

    if not cap or not cap.isOpened():
        messagebox.showerror("Error", "No se puede acceder a la cámara.")
        return

    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "No se pudo capturar el fotograma.")
        return

    # Detectar rostros en el fotograma
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rostros = face_cascade.detectMultiScale(gris, 1.1, 4)

    # Si hay rostros, intentar identificarlos
    if len(rostros) > 0:
        encontrado = False  # Variable para verificar si se encontró una coincidencia
        for (x, y, w, h) in rostros:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Convertir la parte de la imagen que corresponde al rostro a escala de grises
        rostro_gris = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
        
        # Cargar las imágenes registradas y comparar los histogramas
        registros = cargar_imagenes_registradas()
        for nombre, (ruta, histograma_registrado) in registros.items():
            histograma_rostro = cv2.calcHist([rostro_gris], [0], None, [256], [0, 256])
            comparacion = comparar_histogramas(histograma_rostro, histograma_registrado)

            if comparacion > 0.7:  # Umbral de similitud para considerar que es el mismo rostro
                # Si hay coincidencia, actualizar el nombre en la interfaz
                label_info2.config(text=nombre)  # Actualiza el nombre en la interfaz
                encontrado = True
                break

        if not encontrado:  # Si no se encontró ninguna coincidencia
            label_info2.config(text="¡DESCONOCIDO!")  # Mostrar "¡DESCONOCIDO!" en la interfaz

            # Verificar si el rostro desconocido ha sido reportado recientemente
            if rostro_anterior != "¡DESCONOCIDO!":  # Evitar múltiples correos para el mismo rostro desconocido
                rostro_anterior = "¡DESCONOCIDO!"  # Marcar como desconocido
                # Enviar un correo notificando sobre el rostro desconocido
                archivo_imagen = "assets/rostro_desconocido.jpg"  # Puedes guardar la imagen o usar la capturada
                cv2.imwrite(archivo_imagen, frame)  # Guardar la imagen capturada
                enviar_correo(archivo_imagen)

        else:
            rostro_anterior = nombre  # Actualizar al nombre del rostro registrado

    # Llamar a la función cada 1 segundo para seguir verificando rostros
    root.after(1000, verificar_rostros)

# Variable global para evitar falsos reportes
rostro_anterior = None
  
# Función para desactivar el sistema
def desactivar_sistema(btn):
    # Ocultar el botón de desactivar sistema
    btn.pack_forget()

    # Volver a mostrar el botón de activar sistema
    button2.pack(fill="x", pady=10)

# Crear la ventana principal
def crearVentanaPrincipal():
    global button2, container_menu_buttons

    container = tk.Frame(root, bg=colors["azul"])
    container.pack(fill="both", expand=True, padx=20, pady=20)

    container_detection = tk.Frame(container, bg=colors["medianoche"], width=800, height=700)
    container_detection.pack(side="left", padx=10, pady=10)
    container_detection.pack_propagate(False)

    label_camera = tk.Label(container_detection, bg=colors["medianoche"])
    label_camera.pack(expand=True, fill="both")
    if cap and cap.isOpened():
        actualizar_camara(label_camera)

    container_menu = tk.Frame(container, bg=colors["azul"], width=300, height=700)
    container_menu.pack(side="right", padx=10, pady=10)
    container_menu.pack_propagate(False)

    container_menu_buttons = tk.Frame(container_menu, bg=colors["azul"])
    container_menu_buttons.pack(pady=20)

    button1 = tk.Button(container_menu_buttons, text="Registrar Nuevo Rostro", bg=colors["morado"], fg=colors["blanco"],
                    font=("Poppins", 14), relief="flat", bd=0, activebackground=colors["morado_oscuro"],
                    command=registrar_nuevo_rostro)
    button1.pack(fill="x", pady=10)

    # Botón para activar el sistema
    global button2
    button2 = tk.Button(container_menu_buttons, text="Activar Sistema", bg=colors["morado"], fg=colors["blanco"],
                        font=("Poppins", 14), relief="flat", bd=0, activebackground=colors["morado_oscuro"], command=activar_sistema)
    button2.pack(fill="x", pady=10)

    container_menu_info = tk.Frame(container_menu, bg=colors["azul"])
    container_menu_info.pack(fill="both", expand=True, pady=20)

    label_info1 = tk.Label(container_menu_info, text="Última Persona Detectada", bg=colors["blanco"], fg=colors["negro"],
                           font=("Poppins", 14), relief="solid", bd=1)
    label_info1.pack(fill="x", pady=5)

    global label_info2
    label_info2 = tk.Label(container_menu_info, text="---", bg=colors["blanco"], fg=colors["negro"],
                           font=("Poppins", 14), relief="solid", bd=1)
    label_info2.pack(fill="x", pady=5)


# Configuración de la ventana principal
root = tk.Tk()
root.title("Sistema de Seguridad")
root.geometry("1200x400")
root.configure(bg=colors["azul"])

crearVentanaPrincipal()

# Liberar la cámara al cerrar la aplicación
def cerrar():
    if cap and cap.isOpened():
        cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", cerrar)
root.mainloop()

crearVentanaPrincipal()