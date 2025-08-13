import json
import sys
from os.path import exists

import numpy as np
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QSpinBox,
    QSpacerItem,
    QStatusBar,
    QTextEdit,
    QWidget,
)

from utils import GLOBAL_PATHS, FeedFile, set_style, write_json


class Ui_LuaConverter(object):
    """
    Refactored UI class that builds a dynamic PyQt6 interface from a JSON
    configuration file.
    """

    # Maps string names from the config to actual PyQt6 widget classes
    PYQT_CLASSES = {
        "label": QLabel,
        "edit": QLineEdit,
        "intedit": QSpinBox,
        "floatedit": QDoubleSpinBox,
        "textbox": QTextEdit,
        "dropdown": QComboBox,
        "checkbox": QCheckBox,
        "color": QPushButton,
        "coloralpha": QPushButton,
        "alpha": QLineEdit,
        "Pyegi_button": QPushButton,
    }

    def setupUi(self, LuaConverter, script_id, window_name="main_window"):
        LuaConverter.setObjectName("LuaConverter")
        set_style(LuaConverter)

        self.centralwidget = QWidget(LuaConverter)
        self.centralwidget.setObjectName("centralwidget")

        self.window_layout = QGridLayout(self.centralwidget)
        self.widgets_layout = QGridLayout()
        self.widgets_layout.setContentsMargins(20, 20, 20, 0)
        self.widgets_layout.setVerticalSpacing(10)

        # Load script and settings
        self.script = FeedFile().get_script(script_id)
        script_settings_file_path = (
            sys.argv[3]
            if len(sys.argv) > 3 and exists(sys.argv[3])
            else self.script.folder + GLOBAL_PATHS.settings_filename
        )

        with open(script_settings_file_path) as f:
            self.script_settings = json.load(f)

        # Find the configuration for the current window
        widgets_config = next(
            (w for w in self.script_settings["Windows"] if w["name"] == window_name), None
        )
        if not widgets_config:
            raise ValueError(f"Window configuration '{window_name}' not found.")
        
        window_index = self.script_settings["Windows"].index(widgets_config)

        # Create and place widgets dynamically
        self._create_widgets(widgets_config["Controls"], LuaConverter, window_index)

        self.window_layout.addLayout(self.widgets_layout, 0, 0)
        LuaConverter.setCentralWidget(self.centralwidget)
        
        # Setup menubar and statusbar
        self.menubar = QMenuBar(LuaConverter)
        LuaConverter.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(LuaConverter)
        LuaConverter.setStatusBar(self.statusbar)

        self.retranslateUi(LuaConverter, widgets_config)
        QtCore.QMetaObject.connectSlotsByName(LuaConverter)

    def _create_widgets(self, controls, LuaConverter, window_index):
        "Creates and lays out widgets based on the controls configuration."
        for widget_data in controls:
            name = widget_data["name"]
            class_name = widget_data["class"]

            # Get the widget class, defaulting to QLabel if not found
            widget_class = self.PYQT_CLASSES.get(class_name, QLabel)
            widget_instance = widget_class(self.centralwidget)
            
            # Use setattr to dynamically create widget attributes (e.g., self.my_button)
            setattr(self, name, widget_instance)

            # Add widget to the layout
            x, y = widget_data["x"], widget_data["y"]
            width, height = widget_data["width"], widget_data["height"]
            self.widgets_layout.addWidget(widget_instance, y, x, height, width)
            widget_instance.setObjectName(name)
            
            # Connect signals using a safe, direct approach
            self._connect_signals(widget_instance, widget_data, LuaConverter, window_index)

    def _connect_signals(self, instance, data, LuaConverter, window_index):
        "Connects signals for interactive widgets."
        class_name = data["class"]
        name = data["name"]

        # Use a lambda with a default argument to correctly capture the loop variable
        if class_name == "color":
            instance.clicked.connect(lambda checked=False, n=name: self.set_color(n))
        elif class_name == "coloralpha":
            instance.clicked.connect(lambda checked=False, n=name: self.set_coloralpha(n))
        elif class_name == "Pyegi_button":
            instance.clicked.connect(
                lambda checked=False, d=data: self.button_clicked(
                    d, LuaConverter, window_index
                )
            )

    def retranslateUi(self, LuaConverter, widgets_config):
        "Sets the text, values, and tooltips for the widgets."
        _translate = QtCore.QCoreApplication.translate
        LuaConverter.setWindowTitle(_translate("LuaConverter", self.script.name))

        for widget_data in widgets_config["Controls"]:
            name = widget_data["name"]
            class_name = widget_data["class"]
            
            # Use getattr to safely access the widget attribute by its string name
            widget_instance = getattr(self, name)

            # Set tooltips if hint is present
            if "hint" in widget_data:
                widget_instance.setToolTip(_translate("LuaConverter", widget_data["hint"]))

            # Configure widget based on its class
            if class_name == "label":
                widget_instance.setText(_translate("LuaConverter", widget_data["label"]))
            elif class_name in ["edit", "Pyegi_button"]:
                widget_instance.setText(widget_data.get("text", ""))
            elif class_name in ["floatedit", "intedit"]:
                self._setup_spinbox(widget_instance, widget_data)
            elif class_name == "textbox":
                widget_instance.setPlainText(widget_data.get("text", ""))
            elif class_name == "dropdown":
                items = widget_data.get("items", [])
                widget_instance.addItems(items)
                widget_instance.setCurrentText(str(widget_data.get("value", "")))
            elif class_name == "checkbox":
                widget_instance.setText(_translate("LuaConverter", widget_data["label"]))
                # Ensure the value is a boolean
                is_checked = str(widget_data.get("value", "False")).lower() == "true"
                widget_instance.setChecked(is_checked)
            elif class_name == "color":
                widget_instance.setStyleSheet(f"background-color: {widget_data['value']}")
            elif class_name == "coloralpha":
                rgba = self._hex_to_rgba_stylesheet(widget_data["value"])
                widget_instance.setStyleSheet(rgba)
            elif class_name == "alpha":
                widget_instance.setText(str(widget_data.get("value", "")))
                widget_instance.setInputMask("#HH")

    def _setup_spinbox(self, instance, data):
        "Configures QSpinBox or QDoubleSpinBox with min, max, step, and value."
        # Check for 'min' value
        min_val = data.get("min")
        if min_val is not None and str(min_val).lower() != 'nil':
            instance.setMinimum(int(min_val))

        # Check for 'max' value
        max_val = data.get("max")
        if max_val is not None and str(max_val).lower() != 'nil':
            instance.setMaximum(int(max_val))

        # Check for 'step' value for QDoubleSpinBox
        if isinstance(instance, QDoubleSpinBox):
            step_val = data.get("step")
            if step_val is not None and str(step_val).lower() != 'nil':
                instance.setSingleStep(float(step_val))

        # Check for 'value'
        value = data.get("value")
        if value is not None and str(value).lower() != 'nil':
            if isinstance(instance, QDoubleSpinBox):
                instance.setValue(float(value))
            else:
                instance.setValue(int(value))
    
    def _hex_to_rgba_stylesheet(self, hex_color):
        "Converts a hex color string (e.g., #RRGGBBAA) to a CSS rgba() string."
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = 255 - int(hex_color[6:8], 16) if len(hex_color) == 8 else 255
        return f"background-color: rgba({r}, {g}, {b}, {a});"


    def button_clicked(self, button_data, LuaConverter, window_index):
        "Handles button clicks to save settings or transition windows."
        if button_data.get("action", "").lower() == "cancel":
            LuaConverter.close()
            return

        # Update settings from all widgets in the current window
        current_window_config = self.script_settings["Windows"][window_index]
        for widget_data in current_window_config["Controls"]:
            self._update_setting_from_widget(widget_data)

        # Sync values of global widgets (those starting with 'G_') across all windows
        for widget_data in current_window_config["Controls"]:
            if widget_data["name"].startswith("G_"):
                self._sync_global_widget(widget_data)
        
        # Save the updated settings to the JSON file
        py_parameters_file_path = sys.argv[3]
        write_json(self.script_settings, py_parameters_file_path)

        if button_data.get("action", "").lower() == "apply":
            self.script.run(sys.argv[1:])
            sys.exit()
        elif "transition to" in button_data:
            # Re-initialize the UI for the new window
            self.setupUi(LuaConverter, self.script.id, button_data["transition to"])
            
    def _update_setting_from_widget(self, widget_data):
        "Updates a single setting dictionary from its corresponding widget's value."
        name = widget_data["name"]
        class_name = widget_data["class"]
        widget_instance = getattr(self, name, None)
        if not widget_instance:
            return

        if class_name in ["edit", "textbox"]:
            widget_data["text"] = widget_instance.text() if class_name == "edit" else widget_instance.toPlainText()
        elif class_name == "intedit":
            widget_data["value"] = widget_instance.value()
        elif class_name == "floatedit":
            widget_data["value"] = widget_instance.value()
        elif class_name == "dropdown":
            widget_data["value"] = widget_instance.currentText()
        elif class_name == "checkbox":
            widget_data["value"] = str(widget_instance.isChecked())
        elif class_name == "color":
            widget_data["value"] = widget_instance.palette().button().color().name().upper()
        elif class_name == "coloralpha":
            color = widget_instance.palette().button().color()
            alpha_hex = f"{(255 - color.alpha()):02x}".upper()
            widget_data["value"] = f"{color.name().upper()}{alpha_hex}"
        elif class_name == "alpha":
            widget_data["value"] = widget_instance.text()

    def _sync_global_widget(self, source_widget_data):
        "Finds and updates all instances of a global widget in other windows."
        source_name = source_widget_data["name"]
        for window_config in self.script_settings["Windows"]:
            for target_widget_data in window_config["Controls"]:
                if target_widget_data["name"] == source_name:
                    # Copy the value from the source widget
                    if "text" in source_widget_data:
                        target_widget_data["text"] = source_widget_data["text"]
                    if "value" in source_widget_data:
                        target_widget_data["value"] = source_widget_data["value"]


    def set_color(self, name):
        "Opens a QColorDialog to choose a color for a button."
        button = getattr(self, name)
        initial_color = button.palette().button().color()
        
        color = QColorDialog.getColor(initial=initial_color)
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()}")

    def set_coloralpha(self, name):
        "Opens a QColorDialog with alpha to choose a color for a button."
        button = getattr(self, name)
        
        # Get the current color and "un-invert" the alpha for the dialog
        initial_color = button.palette().button().color()
        initial_color.setAlpha(255 - initial_color.alpha())
        
        color = QColorDialog.getColor(
            initial=initial_color,
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            # Invert the alpha again for the stylesheet to match original logic
            rgba_stylesheet = f"background-color: rgba({color.red()}, {color.green()}, {color.blue()}, {255 - color.alpha()})"
            button.setStyleSheet(rgba_stylesheet)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_LuaConverter()
    script_id_from_args = sys.argv[1] if len(sys.argv) > 1 else "default_script"
    ui.setupUi(MainWindow, script_id_from_args)
    MainWindow.show()
    sys.exit(app.exec())
