import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# Ruta al archivo Haar Cascade
HAAR_CASCADE_PATH = "haarcascade_frontalface_default.xml"

# Crear carpeta de almacenamiento de imágenes si no existe
if not os.path.exists("assets"):
    os.makedirs("assets")

# Función para capturar una foto y guardar
def capturar_foto():
    captura = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

    if not captura.isOpened():
        messagebox.showerror("Error", "No se puede acceder a la cámara.")
        return

    def capturar_y_guardar():
        ret, cuadro = captura.read()

        if not ret:
            messagebox.showerror("Error", "Error al capturar el cuadro.")
            return

        gris = cv2.cvtColor(cuadro, cv2.COLOR_BGR2GRAY)
        rostros = face_cascade.detectMultiScale(gris, 1.1, 4)

        if len(rostros) == 0:
            messagebox.showinfo("Info", "No se detectaron rostros.")
            return

        for (x, y, w, h) in rostros:
            cv2.rectangle(cuadro, (x, y), (x + w, y + h), (255, 0, 0), 2)

        nombre_archivo = simpledialog.askstring("Guardar Imagen", "Nombre del archivo:")
        if nombre_archivo:
            ruta_completa = os.path.join("assets", nombre_archivo + ".jpg")
            cv2.imwrite(ruta_completa, cuadro)
            messagebox.showinfo("Guardado", f"Imagen guardada en: {ruta_completa}")

        captura.release()
        cv2.destroyAllWindows()
        ventana_camara.destroy()

    ventana_camara = tk.Toplevel(root)
    ventana_camara.title("Vista de la Cámara")
    
    btn_capturar = tk.Button(ventana_camara, text="Capturar Foto", command=capturar_y_guardar)
    btn_capturar.pack()

    lbl_video = tk.Label(ventana_camara)
    lbl_video.pack()

    def mostrar_video():
        ret, cuadro = captura.read()
        if ret:
            cuadro_rgb = cv2.cvtColor(cuadro, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cuadro_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            lbl_video.imgtk = imgtk
            lbl_video.configure(image=imgtk)
        lbl_video.after(10, mostrar_video)

    mostrar_video()
    ventana_camara.mainloop()

# Función para verificar identidad
def verificar_identidad():
    captura = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

    if not captura.isOpened():
        messagebox.showerror("Error", "No se puede acceder a la cámara.")
        return

    def comparar_fotos(captura_frame):
        gris_captura = cv2.cvtColor(captura_frame, cv2.COLOR_BGR2GRAY)
        rostros = face_cascade.detectMultiScale(gris_captura, 1.1, 4)

        if len(rostros) == 0:
            messagebox.showinfo("Verificación", "No se detectó ningún rostro.")
            return

        for (x, y, w, h) in rostros:
            rostro_capturado = gris_captura[y:y + h, x:x + w]

        for archivo in os.listdir("assets"):
            if archivo.endswith(".jpg"):
                imagen_guardada = cv2.imread(os.path.join("assets", archivo), cv2.IMREAD_GRAYSCALE)
                if imagen_guardada is None:
                    continue

                # Comparar histogramas
                hist1 = cv2.calcHist([rostro_capturado], [0], None, [256], [0, 256])
                hist2 = cv2.calcHist([imagen_guardada], [0], None, [256], [0, 256])
                cv2.normalize(hist1, hist1)
                cv2.normalize(hist2, hist2)
                comparacion = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

                if comparacion > 0.7:  # Umbral de similitud
                    label_info2.config(text=f"Nombre: {archivo[:-4]}")
                    mostrar_imagen(os.path.join("assets", archivo))
                    messagebox.showinfo("Verificación", f"Identidad verificada con: {archivo}")
                    captura.release()
                    cv2.destroyAllWindows()
                    return

        messagebox.showinfo("Verificación", "No se encontró coincidencia.")
        captura.release()
        cv2.destroyAllWindows()

    def verificar_y_mostrar():
        ret, cuadro = captura.read()
        if ret:
            comparar_fotos(cuadro)

    verificar_y_mostrar()

# Mostrar imagen en la interfaz
def mostrar_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    imagen = imagen.resize((260, 350), Image.ANTIALIAS)
    imgtk = ImageTk.PhotoImage(imagen)
    label_image.config(image=imgtk)
    label_image.imgtk = imgtk

# Configuración de la interfaz
colors = {
    "verde": "#58e27b",
    "azul": "#23617e",
    "morado": "#8866e6",
    "morado_oscuro": "#532fb6",
    "medianoche": "#064663",
    "blanco": "#fdfdfd",
    "negro": "#0c0c0c",
}

root = tk.Tk()
root.title("Interfaz con Tkinter")
root.geometry("1200x800")
root.configure(bg=colors["azul"])

container = tk.Frame(root, bg=colors["azul"])
container.pack(fill="both", expand=True, padx=20, pady=20)

container_detection = tk.Frame(container, bg=colors["medianoche"], width=800, height=700)
container_detection.pack(side="left", padx=10, pady=10)
container_detection.pack_propagate(False)

label_camera = tk.Label(container_detection, text="Cámara", fg=colors["blanco"], bg=colors["medianoche"], font=("Poppins", 18))
label_camera.pack(expand=True)

container_menu = tk.Frame(container, bg=colors["azul"], width=300, height=700)
container_menu.pack(side="right", padx=10, pady=10)
container_menu.pack_propagate(False)

container_menu_buttons = tk.Frame(container_menu, bg=colors["azul"])
container_menu_buttons.pack(pady=20)

button1 = tk.Button(container_menu_buttons, text="Registrar Nuevo Rostro", bg=colors["morado"], fg=colors["blanco"],
                    font=("Poppins", 14), relief="flat", bd=0, activebackground=colors["morado_oscuro"], command=capturar_foto)
button1.pack(fill="x", pady=10)

button2 = tk.Button(container_menu_buttons, text="Activar Sistema", bg=colors["morado"], fg=colors["blanco"],
                    font=("Poppins", 14), relief="flat", bd=0, activebackground=colors["morado_oscuro"], command=verificar_identidad)
button2.pack(fill="x", pady=10)

container_menu_info = tk.Frame(container_menu, bg=colors["azul"])
container_menu_info.pack(fill="both", expand=True, pady=20)

label_info1 = tk.Label(container_menu_info, text="Última Persona Detectada", bg=colors["blanco"], fg=colors["negro"],
                       font=("Poppins", 14), relief="solid", bd=1)
label_info1.pack(fill="x", pady=5)

label_info2 = tk.Label(container_menu_info, text="Nombre...", bg=colors["blanco"], fg=colors["negro"],
                       font=("Poppins", 14), relief="solid", bd=1)
label_info2.pack(fill="x", pady=5)

info_image = tk.Frame(container_menu_info, bg=colors["verde"], width=260, height=350)
info_image.pack(pady=20)
info_image.pack_propagate(False)

label_image = tk.Label(info_image, text="Imagen", bg=colors["verde"], fg=colors["negro"], font=("Poppins", 16))
label_image.pack(expand=True)

root.mainloop()
