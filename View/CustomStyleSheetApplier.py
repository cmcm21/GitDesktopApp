##Author Sumanth shenoy
##licenced to soleil studios
from PySide6 import QtGui
from PySide6 import QtCore, QtGui, QtWidgets


class CustomStyleSheetApplier:
    COLOR_STYLES = {
        'Blue': {
            'label_color': "#EAEAEA",
            'gradient_start': "#1E90FF",  # Darker shade for gradient start
            'gradient_stop': "#004080",  # Light blue shade with increased gradient distance
            'hover_start': "#004080",  # Darker shade for hover start
            'hover_stop': "#000A17",  # Even darker shade for hover stop
            'pressed_bg': "#000A17",  # Same as hover stop for pressed background
            'border_color': "black",
            'background_color': "#222222",  # Darker background color
            'focus_color': "#999999",
            'hover_color': "#999999"
        },

        'White': {
            'label_color': "#000000",
            'gradient_start': "#CCCCCC",
            'gradient_stop': "#999999",
            'hover_start': "#999999",
            'hover_stop': "#666666",
            'pressed_bg': "#666666",
            'border_color': "black",
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        },
        'Red': {
            'label_color': "#FFFFFF",
            'gradient_start': "#8B0000",
            'gradient_stop': "#B22222",
            'hover_start': "#B22222",
            'hover_stop': "#FF0000",
            'pressed_bg': "#FF0000",
            'border_color': "#B22222",
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        },
        'Green': {
            'label_color': "#FFFFFF",
            'gradient_start': "#006400",
            'gradient_stop': "#008000",
            'hover_start': "#008000",
            'hover_stop': "#00FF00",
            'pressed_bg': "#00FF00",
            'border_color': "#008000",
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        },
        'Yellow': {
            'label_color': "#000000",  # Set to black
            'gradient_start': "#B5A642",  # Brass color
            'gradient_stop': "#FFD700",  # Bright gold
            'hover_start': "#FFD700",  # Bright gold on hover
            'hover_stop': "#B5A642",  # Brass color on hover
            'pressed_bg': "#B5A642",  # Brass color on press
            'border_color': "#B5A642",  # Brass color for border
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        },
        'Brown': {
            'label_color': "#FFFFFF",
            'gradient_start': "#8B4513",
            'gradient_stop': "#A52A2A",
            'hover_start': "#A52A2A",
            'hover_stop': "#CD5C5C",
            'pressed_bg': "#CD5C5C",
            'border_color': "#8B4513",
            'background_color': "#A52A2A",  # Adjusted background color for QLineEdit
            'focus_color': "#CD5C5C",  # Adjusted focus color for QLineEdit
            'hover_color': "#CD5C5C"  # Adjusted hover color for QLineEdit
        },
        'Black': {
            'label_color': "#FFFFFF",
            'gradient_start': "#000000",  # Set to black
            'gradient_stop': "#333333",  # Dark gray
            'hover_start': "#333333",  # Dark gray
            'hover_stop': "#666666",  # Light gray
            'pressed_bg': "#666666",  # Light gray
            'border_color': "#000000",  # Black
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        },

        'mayaDefault': {
            'label_color': "#FFFFFF",
            'gradient_start': f"rgb({48}, {48}, {48})",
            'gradient_stop': f"rgb({48}, {48}, {48})",
            'hover_start': "#333333",
            'hover_stop': "#666666",
            'pressed_bg': "#666666",
            'border_color': "#000000",
            'background_color': "#CCCCCC",
            'focus_color': "#999999",
            'hover_color': "#999999"
        }

    }

    @classmethod
    def set_buttons_style_and_colour(cls, widgetId='btnName', colour='White', postion='Center'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])
        widgetId.setStyleSheet(f"""
            QPushButton {{
                color: {style_data['label_color']};
                font-size: 11px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border-radius: 5px;
                padding: 5px;
                text-align: {postion};
                border: 2px solid black; /* Black outline */
            }}

            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['hover_start']},
                                             stop: 1 {style_data['hover_stop']});
            }}

            QPushButton:pressed {{
                background-color: {style_data['pressed_bg']};
                border: 2px solid {style_data['pressed_bg']};
            }}
        """)
        widgetId.setFont(QtGui.QFont("Courier New", 10))  # Monospaced font for alignment

    @classmethod
    def set_q_push_button_style_and_colour(cls, widgetId, colour='White', textColour='White'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        textColour = textColour if textColour else style_data['label_color']

        widgetId.setStyleSheet(f"""

            QRadioButton {{
                color: {textColour};
                font-size: 11px;
                padding: 5px;
            }}

            QRadioButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['hover_start']},
                                             stop: 1 {style_data['hover_stop']});
            }}

            QRadioButton:checked {{
                background-color: {style_data['pressed_bg']};
                border: 2px solid {style_data['pressed_bg']};
            }}
        """)
        widgetId.setFont(QtGui.QFont("Courier New", 10))  # Monospaced font for alignment

    @classmethod
    def set_line_edit_style_and_colour(cls, widgetId='btnName', colour='White'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])
        widgetId.setStyleSheet(f"""
            QLineEdit {{
                color: {style_data['label_color']};
                font-size: 12px;
                border-radius: 5px;
                padding: 5px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black outline */
            }}

            QLineEdit:focus {{
                border: 2px solid {style_data['focus_color']}; /* Darker color border on focus */
            }}

            QLineEdit:hover {{
                border: 2px solid {style_data['hover_color']}; /* Darker color border on hover */
            }}
        """
                               )

    @classmethod
    def set_check_box_style_and_colour(cls, widgetId='checkBoxName', defaultColor='White', checkedColor='Green'):
        widgetId.setStyleSheet(f'''
            QCheckBox {{
                color: #f0f0f0; /* Dark white color for text */
                font-size: 12px;
            }}

            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                background-color: {defaultColor}; /* Unchecked background color */

                border: 2px solid black; /* Black border */
                border-radius: 5px;
            }}

            QCheckBox::indicator:checked {{
                background-color: {checkedColor}; /* Checked background color */
                border: 2px solid black; /* Black border for checked state */
            }}

            QCheckBox::indicator:checked:disabled {{
                background-color: {defaultColor}; /* Checked background color for disabled state */
                border: 2px solid {defaultColor}; /* Border color for disabled state */
            }}

            QCheckBox::indicator:unchecked:disabled {{
                background-color: {defaultColor}; /* Unchecked background color for disabled state */
                border: 2px solid {defaultColor}; /* Border color for disabled state */
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {checkedColor}; /* Hovered background color for checked state */
            }}

            QCheckBox::indicator:unchecked:hover {{
                background-color: {defaultColor}; /* Hovered background color for unchecked state */
            }}

            QCheckBox::indicator:checked:disabled:hover {{
                background-color: {defaultColor}; /* Hovered background color for checked state in disabled state */
            }}

            QCheckBox::indicator:unchecked:disabled:hover {{
                background-color: {defaultColor}; /* Hovered background color for unchecked state in disabled state */
            }}
        '''
                               )
        widgetId.setToolTip("Red:OFF Green:ON")

    @classmethod
    def set_combo_box_style_and_colour(cls, widgetId='comboBoxName', colour='White'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QComboBox {{
                color: {style_data['label_color']};
                font-size: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black border */
                border-radius: 5px;
                padding: 5px;
            }}

            QComboBox:hover {{
                border: 2px solid {style_data['hover_color']}; /* Darker color border on hover */
            }}

            QComboBox:focus {{
                border: 2px solid {style_data['focus_color']}; /* Darker color border on focus */
            }}


            }}
        """
                               )
        widgetId.setFont(QtGui.QFont("Courier New", 10))  # Monospaced font for alignment

    @classmethod
    def set_qlist_widget_style_and_colour(cls, widgetId='QlistWidgetID', colour='White', textColour='black'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QListView {{
                font-size: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black border */
                border-radius: 5px;
                padding: 5px;
            }}

            QListView::item {{
                border: 2px solid {style_data['border_color']};
                color: {textColour}; /* Set the text color to black */
            }}

            QListView::item:hover {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                   stop: 0 {style_data['hover_start']},
                                                   stop: 1 {style_data['hover_stop']});
            }}

            QListView::item:selected {{
                background-color: {style_data['pressed_bg']};
            }}

            QListView::item:selected:active {{
                background-color: {style_data['pressed_bg']};
            }}
            QToolTip{{
                background-color: {style_data['background_color']};
                border: 2px solid {style_data['border_color']};
                color: {textColour};
            }}
        """)
        widgetId.setFont(QtGui.QFont("Courier New", 10))  # Monospaced font for alignment

    @classmethod
    def set_q_text_edit_style_and_colour(cls, widgetId='QTextEditID', colour='White', textColour='Black'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QTextEdit {{
                font-size: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black border */
                border-radius: 5px;
                padding: 5px;
                margin: 0px;
                color: {textColour}; /* Set the text color to black */
            }}

            QTextEdit:hover {{
                border: 2px solid {style_data['hover_color']}; /* Darker color border on hover */
            }}

            QTextEdit:focus {{
                border: 2px solid {style_data['focus_color']}; /* Darker color border on focus */
            }}
        """)
        widgetId.setFont(QtGui.QFont("Courier New", 10))  # Monospaced font for alignment

    @classmethod
    def set_q_spin_box_style_and_colour(cls, widgetId='QSpinBoxID', colour='White'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QSpinBox {{
                font-size: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black border */
                border-radius: 5px;
                padding: 5px;
                color: black; /* Set the text color to black */
            }}

            QSpinBox:hover {{
                border: 2px solid {style_data['hover_color']}; /* Darker color border on hover */
            }}

            QSpinBox:focus {{
                border: 2px solid {style_data['focus_color']}; /* Darker color border on focus */
            }}
        """)

    @classmethod
    def set_q_double_spin_box_style_and_colour(self, widgetId='widgetIdName', colour='White'):
        style_data = self.COLOR_STYLES.get(colour, self.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QDoubleSpinBox {{
                font-size: 12px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 2px solid black; /* Black border */
                border-radius: 5px;
                padding: 5px;
                color: black; /* Set the text color to black */
            }}

            QDoubleSpinBox:hover {{
                border: 2px solid {style_data['hover_color']}; /* Darker color border on hover */
            }}

            QDoubleSpinBox:focus {{
                border: 2px solid {style_data['focus_color']}; /* Darker color border on focus */
            }}
        """)

    @classmethod
    def set_q_slider_style_and_colour(cls, widgetId='QSpinBoxID', colour='White', ButtonAndLoadColour='Black'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        widgetId.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border: 1px solid #606060;
                height: 8px;
                border-radius: 4px;
            }}

            QSlider::handle:horizontal {{
                background: {ButtonAndLoadColour}; 

                border: 1px solid #2C3E50;
                width: 16px;
                margin: -8px 0px;
                border-radius: 8px;
            }}

            QSlider::sub-page:horizontal {{
                background: {ButtonAndLoadColour};
                border: 1px solid #2C3E50;
                border-radius: 4px;
            }}

            QSlider::add-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                             stop: 0 {style_data['gradient_start']},
                                             stop: 1 {style_data['gradient_stop']});
                border-radius: 4px;
            }}

            QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #FFFFFF);
            border: 1px solid #2C3E50;
        }}
        """)

    @classmethod
    def set_qtableview_style_and_colour(cls, tableView, colour='White'):
        style_data = cls.COLOR_STYLES.get(colour, cls.COLOR_STYLES['White'])

        tableView.setStyleSheet(f"""
            QTableView {{
                color: {style_data['label_color']};
                background: {style_data['background_color']};
                gridline-color: {style_data['border_color']};
                font-size: 12px;
                selection-background-color: {style_data['pressed_bg']};
                selection-color: {style_data['label_color']};
                border: 1px solid {style_data['border_color']};
            }}

            QTableView::item:hover {{
                background-color: {style_data['hover_color']};
                color: {style_data['label_color']};
            }}

            QHeaderView::section {{
                background-color: {style_data['gradient_start']};
                color: {style_data['label_color']};
                padding: 4px;
                border: 1px solid {style_data['border_color']};
            }}
        """)
        tableView.setFont(QtGui.QFont("Courier New", 10))  # Optional: Set a custom font
