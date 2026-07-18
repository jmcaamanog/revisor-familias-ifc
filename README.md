# IFC BY JMC - Cyber-BIM Terminal v3.5 🏢🕶️

![Profesión](https://img.shields.io/badge/Profesi%C3%B3n-Arquitectos%20T%C3%A9cnicos-2e7d32?logo=micro%3Abit&logoColor=white&style=flat-square)
![Role](https://img.shields.io/badge/Role-BIM%20%26%20ConTech-007ACC?logo=bim360&style=flat-square)
![Location](https://img.shields.io/badge/Location-A%20Coru%C3%B1a%20%F0%9F%8C%8A-005B94?logo=lighthouse&logoColor=white&style=flat-square)
![Sector](https://img.shields.io/badge/Sector-ConTech%20%7C%20AECO-E65100?logo=construct3&style=flat-square)
![BIM](https://img.shields.io/badge/BIM-IFC%20%2F%20openBIM-009688?style=flat-square)
![Maker](https://img.shields.io/badge/Maker-Software-red?logo=makerbot&style=flat-square)
![Hardware](https://img.shields.io/badge/Hardware---grey?style=flat-square)
![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&style=flat-square)
![Language](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white&style=flat-square)
![Stars](https://img.shields.io/github/stars/jmcaamanog/revisor-familias-ifc?style=flat-square&color=yellow&logo=github)
![License](https://img.shields.io/github/license/jmcaamanog/revisor-familias-ifc?style=flat-square&color=green)

(Arquitecto Técnico_JMC) Visor 3D de modelos BIM ultraligero y de alto rendimiento. Presenta una interfaz de terminal inmersiva (estilo retro/ciberpunk) enfocada en la fluidez, permitiendo diseccionar modelos espaciales complejos y extraer datos paramétricos en tiempo real sin el lastre de los visores comerciales tradicionales.

## 🚀 La Filosofía de la Herramienta (Fricción Cero)

Cuando necesitas auditar la geometría de un modelo o verificar la información de un activo, abrir plataformas pesadas (como Navisworks o Revit) te hace perder un tiempo muy valioso. Esta herramienta nace para ser tu visor táctico: un entorno oscuro, acelerado por hardware, donde puedes cargar un IFC en segundos, hacerle rayos X, y obtener un escaneo instantáneo de las propiedades de cualquier elemento con un solo clic.

## 🧠 Características del Software (v3.5)

* **Motor 3D Táctico:** Construido sobre PyVista, renderiza mallas complejas con colores pastel según la clase de entidad (Muros, Losas, Puertas, etc.) o en modo escala de grises.
* **DATA_HUD (Escáner Paramétrico):** Al hacer clic sobre cualquier elemento, un panel lateral transparente ("Uplink") te muestra al instante su Clase IFC, ID, y todos los parámetros clave (Categoría, Volumen, Área, Fabricante) que encuentre en los Property Sets.
* **Panel de Estadísticas de Familia:** Trabaja en conjunto con el escáner para contarte, en vivo, cuántos elementos de esa misma familia o tipo hay en todo el modelo.
* **Modo X-RAY Inteligente:** Aplica una opacidad global regulable mediante un slider. Al seleccionar un objeto, este se ilumina (efecto Ghost) mientras el resto del edificio se vuelve traslúcido para facilitar su ubicación.
* **Herramientas de Visualización:** Control total del grosor y color de las aristas (edges), rotación automática (Auto-Rot) para presentaciones o análisis visual, y módulo de captura de pantalla integrado.

## 📂 Estructura del Repositorio

* 📁 **`CODIGO/`**: Contiene el código fuente principal de la interfaz y el motor 3D (`visor_ifc.py`).
* 📁 **`PROGRAMA/`**: Contenedor del programa ya compilado (`.exe`) junto con sus librerías de soporte. Lamentablemente el archivo queda muy grande para alojarlo en GITHUB, por lo que os toca hacerlo por vuestra cuenta... XD

## ⚙️ Requisitos para el Código Fuente

Si prefieres ejecutar o modificar el software desde el código fuente, necesitarás:

1. Clonar el repositorio y navegar a la carpeta.
2. Instalar las dependencias del motor gráfico y de datos:
   ```bash
   pip install pyqt5 pyvista pyvistaqt ifcopenshell numpy
3. Ejecutar el programa
   ```bash
   python CODIGO\visor_ifc.py
## 🛠️ ¿Cómo compilar tu propio .exe?

1. Si modificas el código y quieres generar tu propio ejecutable aislando las librerías 3D pesadas en una carpeta y ocultando la consola, usa este comando con PyInstaller:
   ```bash
    pyinstaller --noconfirm --onedir --windowed --name "CyberBIM_Terminal" CODIGO\visor_ifc.py
## 👨‍💻 Autor

Jose Manuel Caamaño González | Arquitecto Técnico & BIM Manager.
Digital Product Lead | ConTech & Digital Twin SaaS | BIM, Energy Modeling & Sustainability | Data Analytics (SQL, Power BI)

Hecho con código y café desde A Coruña. ☕

Jose Manuel Caamaño González | [LinkedIn](https://www.linkedin.com/in/jmcaamanog/)
