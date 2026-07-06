"""
       ██╗███╗   ███╗ ██████╗
       ██║████╗ ████║██╔════╝
       ██║██╔████╔██║██║
  ██   ██║██║╚██╔╝██║██║    
  █████╔╝ ██║ ╚═╝ ██║╚██████╗
  ╚════╝  ╚═╝     ╚═╝ ╚═════╝
"""
import sys
import os
import datetime
import numpy as np

# Interfaz gráfica
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                             QMessageBox, QFrame, QSlider, QColorDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# Motores 3D y BIM
import pyvista as pv
from pyvistaqt import QtInteractor
import ifcopenshell
import ifcopenshell.geom

class VisorIFC(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TERMINAL BIM v3.5 - Jose Manuel Caamaño")
        self.setGeometry(100, 100, 1400, 950)

        # Configuración de estilo Retro Dark (Cyber-BIM)
        self.estilo_consola = """
            QMainWindow { background-color: #000000; }
            QWidget { background-color: #000000; color: #00FF00; font-family: 'Courier New', 'Consolas', monospace; }
            QPushButton { 
                background-color: #050505; 
                color: #00FF00; 
                border: 1px solid #00FF00; 
                padding: 6px 14px; 
                font-size: 10px;
                text-transform: uppercase;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00FF00; color: #000000; }
            QPushButton:checked { background-color: #00FF00; color: #000000; }
            QPushButton:disabled { color: #003300; border-color: #003300; }
            QLabel { color: #00FF00; font-size: 14px; }
            QFrame#separador { background-color: #004400; }
            QSlider::handle:horizontal {
                background: #00FF00;
                width: 12px;
                margin: -5px 0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #004400;
                height: 4px;
                background: #050505;
            }
        """
        self.setStyleSheet(self.estilo_consola)

        # Variables de estado
        self.archivo_ifc = None
        self.mostrar_aristas = True
        self.mostrar_texturas = True
        self.fondo_negro = True
        self.modo_xray = False
        self.color_aristas = "#00FF00"
        self.grosor_aristas = 1
        self.opacidad_global = 1.0
        self.lista_actores = []
        self.actor_seleccionado = None
        
        # Sistema de Rotación
        self.timer_rotacion = QTimer()
        self.timer_rotacion.timeout.connect(self.ejecutar_rotacion)
        self.rotacion_activa = False

        # Contenedor principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout_principal = QVBoxLayout(self.central_widget)

        # --- TOOLBAR ORGANIZADA ---
        self.toolbar_layout = QHBoxLayout()
        
        # [SECCIÓN_IFC]
        self.btn_cargar = QPushButton("📂 LOAD_IFC")
        self.btn_cargar.clicked.connect(self.cargar_ifc)
        self.toolbar_layout.addWidget(self.btn_cargar)

        self.btn_foto = QPushButton("📸 SCREENSHOT")
        self.btn_foto.clicked.connect(self.capturar_pantalla)
        self.toolbar_layout.addWidget(self.btn_foto)
        self.toolbar_layout.addWidget(self.crear_separador())

        # [SECCIÓN_VISTAS]
        vistas = [("TOP", "xy"), ("FRONT", "xz"), ("ISO", "iso")]
        for nombre, modo in vistas:
            btn = QPushButton(nombre)
            if modo == "xy": btn.clicked.connect(lambda: self.plotter.view_xy())
            elif modo == "xz": btn.clicked.connect(lambda: self.plotter.view_xz())
            else: btn.clicked.connect(lambda: self.plotter.view_isometric())
            self.toolbar_layout.addWidget(btn)
        
        self.btn_rotar = QPushButton("🔄 AUTO-ROT")
        self.btn_rotar.setCheckable(True)
        self.btn_rotar.clicked.connect(self.alternar_rotacion)
        self.toolbar_layout.addWidget(self.btn_rotar)
        self.toolbar_layout.addWidget(self.crear_separador())

        # [SECCIÓN_ESTILOS]
        self.btn_aristas = QPushButton("EDGES")
        self.btn_aristas.clicked.connect(self.alternar_aristas)
        self.toolbar_layout.addWidget(self.btn_aristas)

        self.btn_texturas = QPushButton("COLOR/GRIS")
        self.btn_texturas.clicked.connect(self.alternar_texturas)
        self.toolbar_layout.addWidget(self.btn_texturas)

        self.btn_fondo = QPushButton("🌗 FONDO")
        self.btn_fondo.clicked.connect(self.alternar_fondo)
        self.toolbar_layout.addWidget(self.btn_fondo)
        self.toolbar_layout.addWidget(self.crear_separador())

        # [SECCIÓN_EFECTOS]
        self.btn_xray = QPushButton("X-RAY: OFF")
        self.btn_xray.clicked.connect(self.alternar_modo_xray)
        self.toolbar_layout.addWidget(self.btn_xray)
        
        self.slider_opacidad = QSlider(Qt.Horizontal)
        self.slider_opacidad.setRange(5, 95)
        self.slider_opacidad.setValue(30)
        self.slider_opacidad.setFixedWidth(70)
        self.slider_opacidad.valueChanged.connect(self.actualizar_opacidad_xray)
        self.toolbar_layout.addWidget(self.slider_opacidad)

        self.toolbar_layout.addWidget(QLabel("EDGE:"))
        self.btn_color_picker = QPushButton("COLOR")
        self.btn_color_picker.clicked.connect(self.seleccionar_color_aristas)
        self.toolbar_layout.addWidget(self.btn_color_picker)

        self.slider_aristas = QSlider(Qt.Horizontal)
        self.slider_aristas.setRange(1, 8)
        self.slider_aristas.setValue(1)
        self.slider_aristas.setFixedWidth(60)
        self.slider_aristas.valueChanged.connect(self.cambiar_grosor_aristas)
        self.toolbar_layout.addWidget(self.slider_aristas)

        self.toolbar_layout.addStretch()
        self.layout_principal.addLayout(self.toolbar_layout)

        # --- PANEL DE CONSOLA (Doble línea) ---
        self.consola_layout = QVBoxLayout()
        self.label_info = QLabel("> SYSTEM_READY. STANDBY...")
        self.label_info.setStyleSheet("border: 1px solid #004400; padding: 4px; background: #020202; font-size: 13px;")
        
        self.label_meta = QLabel("> PROJECT_DATA: NO_FILE_LOADED")
        self.label_meta.setStyleSheet("border: 1px solid #004400; border-top: none; padding: 4px; background: #020202; font-size: 11px; color: #008800;")
        
        self.consola_layout.addWidget(self.label_info)
        self.consola_layout.addWidget(self.label_meta)
        self.layout_principal.addLayout(self.consola_layout)

        # --- VISOR 3D ---
        self.plotter = QtInteractor(self.central_widget)
        self.layout_principal.addWidget(self.plotter.interactor)
        self.plotter.set_background('black')
        self.plotter.add_camera_orientation_widget()
        
        # Configurar Picking de precisión
        self.plotter.enable_mesh_picking(callback=self.al_seleccionar_elemento, left_clicking=True, show_message=False)

        # --- DATA_HUD (Panel Principal) ---
        self.panel_datos = QLabel(self.plotter.interactor)
        self.panel_datos.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 20, 0, 220);
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 15px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }
        """)
        self.panel_datos.setWordWrap(True)
        self.panel_datos.setFixedWidth(380)
        self.panel_datos.move(20, 20) 
        self.panel_datos.hide()

        # --- PANEL ESTADÍSTICAS FAMILIA (Nuevo debajo) ---
        self.panel_familia = QLabel(self.plotter.interactor)
        self.panel_familia.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 10, 0, 220);
                color: #00CC00;
                border: 1px solid #004400;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        self.panel_familia.setWordWrap(True)
        self.panel_familia.setFixedWidth(380)
        self.panel_familia.hide()

        # --- FOOTER ---
        self.label_creditos = QLabel("IFC_CORE_V3.5 | DEVELOPED BY: JOSE MANUEL CAAMAÑO GONZÁLEZ")
        self.label_creditos.setAlignment(Qt.AlignCenter)
        self.label_creditos.setStyleSheet("color: #005500; font-size: 9px; padding: 8px; border-top: 1px solid #002200;")
        self.layout_principal.addWidget(self.label_creditos)

    def crear_separador(self):
        linea = QFrame(); linea.setFrameShape(QFrame.VLine); linea.setObjectName("separador"); linea.setFixedWidth(2)
        return linea

    def alternar_rotacion(self):
        self.rotacion_activa = not self.rotacion_activa
        if self.rotacion_activa:
            self.timer_rotacion.start(30) # ~33 FPS
            self.label_info.setText("> AUTO_ROTATION_ENABLED. ORBITING...")
        else:
            self.timer_rotacion.stop()
            self.label_info.setText("> AUTO_ROTATION_DISABLED.")

    def ejecutar_rotacion(self):
        # Rotación suave sobre el eje Z (vertical)
        self.plotter.camera.Azimuth(0.5)
        self.plotter.render()

    def alternar_fondo(self):
        self.fondo_negro = not self.fondo_negro
        color = 'black' if self.fondo_negro else '#E0E0E0'
        self.plotter.set_background(color)
        self.plotter.render()

    def capturar_pantalla(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"BIM_CAPTURE_{ts}.png"
        ruta, _ = QFileDialog.getSaveFileName(self, "SAVE_SCREENSHOT", nombre_sugerido, "PNG Files (*.png)")
        if ruta:
            self.plotter.screenshot(ruta)
            self.label_info.setText(f"> SCREENSHOT_SAVED: {os.path.basename(ruta)}")

    def seleccionar_color_aristas(self):
        color = QColorDialog.getColor(QColor(self.color_aristas), self, "SELECT_EDGE_COLOR")
        if color.isValid():
            self.color_aristas = color.name()
            for item in self.lista_actores: item['actor'].prop.edge_color = self.color_aristas
            self.plotter.render()

    def cambiar_grosor_aristas(self, valor):
        self.grosor_aristas = valor
        for item in self.lista_actores: item['actor'].prop.line_width = float(self.grosor_aristas)
        self.plotter.render()

    def alternar_modo_xray(self):
        self.modo_xray = not self.modo_xray
        if self.modo_xray:
            self.btn_xray.setText("X-RAY: ON")
            self.btn_xray.setStyleSheet("background-color: #00FF00; color: #000000;")
            self.opacidad_global = self.slider_opacidad.value() / 100.0
        else:
            self.btn_xray.setText("X-RAY: OFF")
            self.btn_xray.setStyleSheet("")
            self.opacidad_global = 1.0
        
        for item in self.lista_actores:
            item['actor'].prop.opacity = self.opacidad_global
        self.plotter.render()

    def actualizar_opacidad_xray(self, valor):
        if self.modo_xray:
            self.opacidad_global = valor / 100.0
            for item in self.lista_actores:
                if self.actor_seleccionado and item['actor'] != self.actor_seleccionado:
                    item['actor'].prop.opacity = self.opacidad_global * 0.5
                else:
                    item['actor'].prop.opacity = self.opacidad_global
            self.plotter.render()

    def alternar_aristas(self):
        self.mostrar_aristas = not self.mostrar_aristas
        for item in self.lista_actores: item['actor'].prop.show_edges = self.mostrar_aristas
        self.plotter.render()

    def alternar_texturas(self):
        self.mostrar_texturas = not self.mostrar_texturas
        for item in self.lista_actores:
            item['actor'].prop.color = item['color_pastel'] if self.mostrar_texturas else "#444444"
        self.plotter.render()

    def obtener_color_pastel(self, clase):
        colores = {
            "IfcWall": "#A8DADC", "IfcSlab": "#457B9D", "IfcDoor": "#E9C46A", 
            "IfcWindow": "#A2D2FF", "IfcColumn": "#2A9D8F", "IfcBeam": "#8D99AE", 
            "IfcFurnishingElement": "#F4A261", "IfcRoof": "#E76F51", "IfcStair": "#D4A373"
        }
        return colores.get(clase, "#BDBDBD")

    def al_seleccionar_elemento(self, mesh):
        if mesh is None:
            self.panel_datos.hide()
            self.panel_familia.hide()
            self.actor_seleccionado = None
            for item in self.lista_actores: item['actor'].prop.opacity = self.opacidad_global
            self.plotter.render()
            return

        if "ifc_id" in mesh.cell_data:
            id_step = int(mesh.cell_data["ifc_id"][0])
            producto = self.archivo_ifc.by_id(id_step)
            clase_actual = producto.is_a()
            
            # Efecto Ghost
            for item in self.lista_actores:
                if item['id'] == id_step:
                    self.actor_seleccionado = item['actor']
                    item['actor'].prop.opacity = 1.0
                else:
                    item['actor'].prop.opacity = self.opacidad_global * (0.15 if self.modo_xray else 0.5)
            
            # 1. PANEL PRINCIPAL (Propiedades)
            propiedades = {}
            if hasattr(producto, 'IsDefinedBy'):
                for d in producto.IsDefinedBy:
                    if d.is_a('IfcRelDefinesByProperties'):
                        pset = d.RelatingPropertyDefinition
                        if pset.is_a('IfcPropertySet'):
                            for p in pset.HasProperties:
                                if p.is_a('IfcPropertySingleValue') and p.NominalValue:
                                    val = p.NominalValue.wrappedValue
                                    if isinstance(val, (float, int)) and not isinstance(val, bool):
                                        val = round(val, 3)
                                    propiedades[p.Name] = val

            hud_html = f"<div style='color:#00FF00;'>[ SCANNING_OBJECT... ]<br>---<br>"
            hud_html += f"CLASS: <span style='color:white;'>{clase_actual}</span><br>"
            hud_html += f"ID: #{producto.id()}<br>---<br>"
            hud_html += "<table width='100%'>"
            filtros = ['Categoría', 'Familia', 'Tipo', 'Fabricante', 'Nivel', 'Volumen', 'Área', 'Volume', 'Area', 'Width', 'Height', 'Length']
            for f in filtros:
                for p_name, p_val in propiedades.items():
                    if f.lower() in p_name.lower():
                        hud_html += f"<tr><td>{p_name}:</td><td align='right' style='color:white;'>{p_val}</td></tr>"
            hud_html += "</table><br>> DATA_LINK_STABLE.</div>"
            
            self.panel_datos.setText(hud_html)
            self.panel_datos.show()

            # 2. PANEL DE FAMILIA (Estadísticas del mismo tipo de objeto)
            elementos_clase = self.archivo_ifc.by_type(clase_actual)
            total_clase = len(elementos_clase)
            
            # Conteo de tipos específicos dentro de la clase
            desglose_tipos = {}
            for e in elementos_clase:
                tipo = "UNDEFINED"
                # Intentamos sacar el nombre del tipo o familia
                if hasattr(e, 'ObjectType') and e.ObjectType: tipo = e.ObjectType
                elif hasattr(e, 'Name') and e.Name: 
                    # Limpiamos un poco el nombre para agrupar mejor
                    tipo = e.Name.split(':')[0] if ':' in e.Name else e.Name
                
                desglose_tipos[tipo] = desglose_tipos.get(tipo, 0) + 1

            fam_html = f"<div style='color:#00CC00;'>[ FAMILY_REPORT: {clase_actual} ]<br>"
            fam_html += f"TOTAL_COUNT: <span style='color:white;'>{total_clase}</span> elements<br>---<br>"
            
            # Mostrar los top 5 tipos para no saturar el panel
            count = 0
            for t_name, t_qty in sorted(desglose_tipos.items(), key=lambda item: item[1], reverse=True):
                if count < 6:
                    fam_html += f"• {t_name[:25]}: <span style='color:white;'>{t_qty}</span><br>"
                count += 1
            
            if len(desglose_tipos) > 6:
                fam_html += f"... and {len(desglose_tipos)-6} more types."
                
            fam_html += "</div>"
            self.panel_familia.setText(fam_html)
            
            # Posicionar el panel de familia justo debajo del panel de datos
            self.panel_familia.move(20, self.panel_datos.y() + self.panel_datos.height() + 10)
            self.panel_familia.show()
            
            self.plotter.render()

    def cargar_ifc(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "LOAD_IFC_DATA", "", "IFC Files (*.ifc)")
        if not ruta: return
        
        self.label_info.setText(f"> INITIALIZING_BUFFER: {os.path.basename(ruta)}...")
        QApplication.processEvents()
        
        try:
            stats = os.stat(ruta)
            size_mb = round(stats.st_size / (1024 * 1024), 2)
            fecha_mod = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
            
            self.archivo_ifc = ifcopenshell.open(ruta)
            self.plotter.clear()
            self.plotter.add_camera_orientation_widget()
            self.lista_actores.clear()
            
            self.modo_xray = False
            self.btn_xray.setText("X-RAY: OFF")
            self.btn_xray.setStyleSheet("")
            self.opacidad_global = 1.0

            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            
            for p in self.archivo_ifc.by_type("IfcProduct"):
                if p.Representation:
                    try:
                        forma = ifcopenshell.geom.create_shape(settings, p)
                        v = np.array(forma.geometry.verts).reshape((-1, 3))
                        f = np.array(forma.geometry.faces).reshape((-1, 3))
                        malla = pv.PolyData(v, np.hstack([np.full((f.shape[0], 1), 3), f]).flatten())
                        malla.cell_data["ifc_id"] = np.full(malla.n_cells, p.id())
                        
                        color = self.obtener_color_pastel(p.is_a())
                        actor = self.plotter.add_mesh(malla, color=color, show_edges=self.mostrar_aristas,
                                                     edge_color=self.color_aristas, line_width=float(self.grosor_aristas),
                                                     pickable=True, opacity=self.opacidad_global)
                        self.lista_actores.append({'actor': actor, 'color_pastel': color, 'id': p.id()})
                    except: pass
            
            self.plotter.reset_camera()
            self.label_info.setText(f"> SYSTEM_LOADED. READY_FOR_ANALYSIS. ELEMENTS: {len(self.lista_actores)}")
            self.label_meta.setText(f"> PROJECT_DATA | FILE: {os.path.basename(ruta)} | SIZE: {size_mb}MB | MODIFIED: {fecha_mod} | SCHEMA: {self.archivo_ifc.schema}")
            
        except Exception as e:
            self.label_info.setText(f"> BOOT_FAILURE: {str(e)[:40]}")
            QMessageBox.critical(self, "FATAL_ERROR", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    visor = VisorIFC(); visor.show()
    sys.exit(app.exec_())