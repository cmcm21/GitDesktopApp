from PySide6.QtWidgets import QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal
from Utils.ConfigFileManager import ConfigFileManager
from Utils import FileManager
from View.BaseWindow import BaseWindow
from View.WindowID import WindowID
from View.CustomStyleSheetApplier import CustomStyleSheetApplier
from View.UILogger import LoggerWidget

Maya_Versions = {
    "Maya2018": "C://Program Files/Autodesk/Maya2018/bin/maya.exe",
    "Maya2019": "C://Program Files/Autodesk/Maya2019/bin/maya.exe",
    "Maya2020": "C://Program Files/Autodesk/Maya2020/bin/maya.exe",
    "Maya2021": "C://Program Files/Autodesk/Maya2021/bin/maya.exe",
    "Maya2022": "C://Program Files/Autodesk/Maya2022/bin/maya.exe",
    "Maya2024": "C://Program Files/Autodesk/Maya2024/bin/maya.exe",
    "Maya2025": "C://Program Files/Autodesk/Maya2025/bin/maya.exe"
}
config_section = "general"
selected_maya_key = "selected_maya_bat"
selected_bat_key = "selected_bat"

class SettingWindows(BaseWindow):
    def __init__(self, window_id: WindowID, logger: LoggerWidget):
        super().__init__("Settings Window", window_id, 500, 250)
        self.tempura_bat_files = []
        self.onigiri_bat_files = []
        self.config_manager = ConfigFileManager()
        self.logger_widget = logger
        self.main_layout = QVBoxLayout(self)

        self.maya_layout = QHBoxLayout(self)
        self.maya_label = QLabel("Select Maya Version")
        self.maya_combo_box = QComboBox(self)
        self.maya_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.bat_dir_layout = QHBoxLayout(self)
        self.bat_dir_label =  QLabel("Select Bat Version")
        self.bat_dir_combo_box = QComboBox(self)
        self.bat_dir_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.raw_working_directory = self.config_manager.get_config()["general"]["working_path"]
        self.save_button = BaseWindow.create_button(self,"save.png", "Save")
        self.save_button.clicked.connect(self.on_save_pressed)

        self._build()
        self.apply_styles()

    def _build(self):
        self.build_maya_elements()
        self.build_bat_dir_elements()
        self.set_store_values()

        self.main_layout.addLayout(self.bat_dir_layout)
        self.main_layout.addLayout(self.maya_layout)
        self.main_layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

    def build_bat_dir_elements(self):
        self.bat_dir_layout.addWidget(self.bat_dir_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.bat_dir_layout.addWidget(self.bat_dir_combo_box)
        self.build_bat_dir_combo_box()

    def build_maya_elements(self):
        self.maya_layout.addWidget(self.maya_label, alignment=Qt.AlignmentFlag.AlignJustify)
        self.maya_layout.addWidget(self.maya_combo_box)

    def build_bat_dir_combo_box(self):
        self.bat_dir_combo_box.clear()
        onigiri_bat_dirs = FileManager.find_directories("Onigiri", self.raw_working_directory)
        if len(onigiri_bat_dirs) > 0:
            self.onigiri_bat_files = FileManager.find_files("AdminMaya", "bat", onigiri_bat_dirs[0])
            for bat_dir in onigiri_bat_dirs:
                self.bat_dir_combo_box.addItem(f"Onigiri ({bat_dir})", userData=bat_dir)

        tempura_bat_dirs = FileManager.find_directories("Tempura", self.raw_working_directory)
        if len(tempura_bat_dirs) > 0:
            self.tempura_bat_files = FileManager.find_files("AdminMaya", "bat", tempura_bat_dirs[0])
            for bat_dir in tempura_bat_dirs:
                self.bat_dir_combo_box.addItem(f"Tempura ({bat_dir})", userData=bat_dir)

        if self.bat_dir_combo_box.count() > 0:
            self.on_bat_dir_change(self.bat_dir_combo_box.currentIndex())
        else:
            self.bat_dir_combo_box.addItem("Maya bat files not found")

        self.bat_dir_combo_box.currentIndexChanged.connect(self.on_bat_dir_change)

    def set_store_values(self):
        store_bat_conf = self.config_manager.get_value(config_section, selected_bat_key)
        store_maya_conf = self.config_manager.get_value(config_section, selected_maya_key)
        selected_bat_index = -1
        selected_maya_index = -1

        for i in range(self.bat_dir_combo_box.count()):
            data_dir = self.bat_dir_combo_box.itemData(i,Qt.ItemDataRole.UserRole)
            if data_dir is not None and data_dir == store_bat_conf:
                selected_bat_index = i
                break

        for i in range(self.maya_combo_box.count()):
            data_dir = self.maya_combo_box.itemData(i, Qt.ItemDataRole.UserRole)
            if data_dir is not None and data_dir == store_maya_conf:
                selected_maya_index = i
                break

        if selected_maya_index != -1:
            self.maya_combo_box.setCurrentIndex(selected_maya_index)

        if selected_bat_index != -1:
            self.bat_dir_combo_box.setCurrentIndex(selected_bat_index)

    def on_bat_dir_change(self, index):
        bat_data: str = self.bat_dir_combo_box.itemData(index, Qt.ItemDataRole.UserRole)
        if bat_data.endswith("Onigiri"):
            self.build_maya_combo_box(self.onigiri_bat_files)
        elif bat_data.endswith("Tempura"):
            self.build_maya_combo_box(self.tempura_bat_files)

    def build_maya_combo_box(self, maya_files):
        self.maya_combo_box.clear()
        for maya_version in maya_files:
            self.maya_combo_box.addItem(maya_version, userData=maya_version)

    def on_save_pressed(self):
        maya_bat = self.maya_combo_box.currentData(Qt.ItemDataRole.UserRole)
        selected_bat = self.bat_dir_combo_box.currentData(Qt.ItemDataRole.UserRole)

        if maya_bat:
            self.config_manager.add_value("general","selected_maya_bat", maya_bat)
            self.config_manager.add_value("general", "selected_bat", selected_bat)
            self.logger_widget.logger.debug(f"Maya version selected: {maya_bat}")
        else:
            self.logger_widget.logger.error(f"Error trying to select bat file, bat path: {maya_bat}")

        self.automatic_close = True
        self.close()

    def apply_styles(self):
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.maya_combo_box)
        CustomStyleSheetApplier.set_combo_box_style_and_colour(self.bat_dir_combo_box)
        CustomStyleSheetApplier.set_buttons_style_and_colour(self.save_button, "Blue")

