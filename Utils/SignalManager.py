from PySide6.QtCore import QMetaMethod
from PySide6.QtCore import QObject, Signal, Slot, SignalInstance


class SignalManager(QObject):
    _connected_signals = {}

    @staticmethod
    def connect_signal(signal_object: QObject, signal: SignalInstance, method: Slot):
        signal_meta_method = QMetaMethod.fromSignal(signal)
        if (not signal_object.isSignalConnected(signal_meta_method) or
                not SignalManager.is_method_connected(signal, method)):

            signal.connect(method)
            SignalManager._register_connection(signal, method)

    @staticmethod
    def disconnect_signal(signal_object: QObject, signal: SignalInstance, method: Slot):
        signal_meta_method = QMetaMethod.fromSignal(signal)
        if signal_object.isSignalConnected(signal_meta_method) or SignalManager.is_method_connected(signal, method):
            signal.disconnect(method)
            SignalManager._unregister_connection(signal, method)

    @staticmethod
    def is_method_connected(signal: SignalInstance, method: Slot) -> bool:
        connected_methods = SignalManager._connected_signals.get(signal, [])
        return method in connected_methods

    @staticmethod
    def _register_connection(signal: SignalInstance, method: Slot):
        if signal not in SignalManager._connected_signals:
            SignalManager._connected_signals[signal] = []
        SignalManager._connected_signals[signal].append(method)

    @staticmethod
    def _unregister_connection(signal: SignalInstance, method: Slot):
        if signal in SignalManager._connected_signals:
            SignalManager._connected_signals[signal].remove(method)
