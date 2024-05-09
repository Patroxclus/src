import maya.cmds as cmds
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide2.QtWidgets import QListWidget, QColorDialog, QMessageBox
from PySide2.QtGui import QColor

class ObjectColorChanger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Object Color Changer")
        self.setObjectName("ObjectColorChanger")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Object Selection Section
        self.object_label = QLabel("Selected Object:")
        self.layout.addWidget(self.object_label)
        self.object_list = QListWidget()
        self.layout.addWidget(self.object_list)
        
        # Color Picker Section
        self.color_label = QLabel("Choose Color:")
        self.layout.addWidget(self.color_label)
        self.color_picker_button = QPushButton("Pick Color")
        self.color_picker_button.clicked.connect(self.open_color_picker)
        self.layout.addWidget(self.color_picker_button)
        
        # Functional Buttons Section
        self.functional_buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.functional_buttons_layout)
        
        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self.select_object)
        self.functional_buttons_layout.addWidget(self.select_button)
        
        self.apply_button = QPushButton("Apply Color")
        self.apply_button.clicked.connect(self.apply_color)
        self.functional_buttons_layout.addWidget(self.apply_button)
        
        self.clear_button = QPushButton("Clear Material")
        self.clear_button.clicked.connect(self.clear_material)
        self.functional_buttons_layout.addWidget(self.clear_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_list)
        self.functional_buttons_layout.addWidget(self.refresh_button)
        
        self.refresh_list()

    def open_color_picker(self):
        color_dialog = QColorDialog()
        new_color = color_dialog.getColor()
        if new_color.isValid():
            self.selected_color = new_color
            
    def select_object(self):
        selected_items = self.object_list.selectedItems()
        if selected_items:
            selected_objects = [item.text() for item in selected_items]
            cmds.select(selected_objects)
            self.object_label.setText(f"Selected Object(s): {', '.join(selected_objects)}")
        else:
            cmds.select(clear=True)
            self.object_label.setText("Selected Object: None")

    def apply_color(self):
        selected_items = self.object_list.selectedItems()
        if selected_items:
            if hasattr(self, 'selected_color'):
                color = [self.selected_color.redF(), self.selected_color.greenF(), self.selected_color.blueF()]
                for item in selected_items:
                    selected_object = item.text()
                    # Create a new material for the object
                    material_name = cmds.shadingNode("lambert", asShader=True, name=f"{selected_object}_mat")
                    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{selected_object}_SG")
                    cmds.connectAttr(f"{material_name}.outColor", f"{shading_group}.surfaceShader", force=True)
                    cmds.sets(selected_object, edit=True, forceElement=shading_group)
                    # Set the color of the material
                    cmds.setAttr(f"{material_name}.color", color[0], color[1], color[2], type="double3")
                cmds.select([item.text() for item in selected_items])

    def clear_material(self):
        selected_items = self.object_list.selectedItems()
        if selected_items:
            for item in selected_items:
                selected_object = item.text()
                # Check if the object has a material
                material_name = cmds.listConnections(selected_object, type="shadingEngine")
                if material_name:
                    # Delete the material
                    cmds.delete(material_name[0])
                else:
                    QMessageBox.warning(self, "Warning", f"No material found for {selected_object}")
                    return

    def refresh_list(self):
        self.object_list.clear()
        selection = cmds.ls(selection=True)
        if selection:
            self.object_list.addItems(selection)

objectcolorchangerWidget = ObjectColorChanger()
objectcolorchangerWidget.show()
