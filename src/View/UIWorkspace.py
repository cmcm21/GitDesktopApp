from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt


class WorkspaceWidget(QtWidgets.QWidget):
    """ Workspace widget to show working files """

    def __init__(self, *args, **kwargs):
        super(WorkspaceWidget, self).__init__(*args, **kwargs)
