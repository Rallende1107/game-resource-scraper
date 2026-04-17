# 🎮 Game Resource Scraper

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PySide6](https://img.shields.io/badge/UI-PySide6-green)
![Status](https://img.shields.io/badge/status-en%20desarrollo-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Herramienta para extraer recursos (imágenes, audio, fuentes y video) desde juegos
desarrollados en motores como **Ren'Py** y otros.

---
## 🚀 Características

- 📂 Extracción de imágenes, audio y video
- 🧩 Compatible con proyectos Ren'Py
- 🎨 Interfaz gráfica construida con PySide6
- ⚡ Procesamiento rápido y automatizado
- 📁 Organización de archivos extraídos
- 📁 descompilar **RPA** Y **RPYC** de juegos **Ren'Py**

---

## 📸 Capturas (opcional)

<img width="804" height="686" alt="image" src="https://github.com/user-attachments/assets/b89c5bf1-0421-4f51-9274-3f582867d742" />


---

## 📦 Instalación

### 1. Clonar repositorio
```bash
    git clone https://github.com/Rallende1107/game-resource-scraper.git
    cd game-resource-scraper
```

### 2. Crear entorno virtual
```bash
    python -m venv .venv
```

### 3. Activar entorno

#### Windows
```bash
    .venv\Scripts\activate
```

#### Linux / macOS
```bash
    source .venv/bin/activate
```

### 4. Instalar dependencias
```bash
    pip install -r requirements.txt
```
---

## ▶️ Uso
```bash
    python main.py
```
---

## 🎨 Interfaz gráfica (PySide6)
El diseño de la interfaz se realiza con archivos `.ui` usando Qt Designer.


### 🛠️ Abrir el editor
```bash
    pyside6-designer
```
Abrir archivo:
<img width="1486" height="903" alt="image" src="https://github.com/user-attachments/assets/6497f66d-8e85-4186-9fcc-d12b4ec5ad4f" />

```bash
    ui/main.ui
```

<img width="799" height="502" alt="image" src="https://github.com/user-attachments/assets/dee919db-fb89-429b-a191-b66cfa3eafec" />

### 🔄 Convertir .ui a Python

```bash
    pyside6-uic ui/main.ui -o ui/main_view.py
```
---

## ⚠️ Notas importantes
- Cada vez que modifiques el `.ui`, debes regenerar el archivo `.py`
- No edites manualmente los archivos generados (`main_view.py`)
- Usa rutas relativas para mantener compatibilidad entre sistemas
---


## 📁 Estructura del proyecto

```html
game-resource-scraper/
│
├── funciones/        # Lógica del programa
├── ui/               # Archivos de interfaz (.ui y convertidos)
├── main.py           # Punto de entrada
├── requirements.txt  # Dependencias
└── README.md
```
---
## 🧠 Tecnologías utilizadas
- Python
- PySide6 (Qt)
- pathlib / os

---

## ⚖️ Aviso legal
Este proyecto está destinado únicamente a fines educativos.
No se incluyen ni distribuyen recursos de terceros.

---

## 👤 Autor

- [@Rallende](https://github.com/Rallende1107)

---

## ⭐ Contribuciones
Las contribuciones, ideas y mejoras son bienvenidas.
Puedes abrir un issue o enviar un pull request.

---

## 📌 Estado del proyecto
🚧 En desarrollo — nuevas funcionalidades en camino.

---
