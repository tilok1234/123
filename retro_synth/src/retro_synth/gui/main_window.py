from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QTableWidgetItem
from PySide6.QtCore import Slot
from retro_synth.engine.commands import CommandBus

class MainWindow(QMainWindow):
    def __init__(self, command_bus: CommandBus):
        super().__init__()
        self.command_bus = command_bus
        self.setWindowTitle("Retro Synth Workstation")
        self.resize(1024, 768)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Transport Bar
        transport_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.status_label = QLabel("Ready")

        transport_layout.addWidget(self.play_button)
        transport_layout.addWidget(self.stop_button)
        transport_layout.addWidget(self.status_label)
        transport_layout.addStretch()

        main_layout.addLayout(transport_layout)

        # Main Workspace
        workspace_layout = QHBoxLayout()

        # Orders / Song Map
        orders_layout = QVBoxLayout()
        orders_layout.addWidget(QLabel("Orders"))
        self.orders_list = QTableWidget(16, 1)
        self.orders_list.setHorizontalHeaderLabels(["Pattern"])
        self.orders_list.setFixedWidth(150)
        orders_layout.addWidget(self.orders_list)
        workspace_layout.addLayout(orders_layout)

        # Pattern Editor
        pattern_layout = QVBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern Editor"))
        self.pattern_grid = QTableWidget(64, 8)
        self.pattern_grid.setHorizontalHeaderLabels([f"Ch{i+1}" for i in range(8)])
        pattern_layout.addWidget(self.pattern_grid)
        workspace_layout.addLayout(pattern_layout)

        # Instrument Inspector
        inst_layout = QVBoxLayout()
        inst_layout.addWidget(QLabel("Instrument Inspector"))
        self.inst_props = QTableWidget(10, 2)
        self.inst_props.setHorizontalHeaderLabels(["Property", "Value"])
        self.inst_props.setFixedWidth(250)
        inst_layout.addWidget(self.inst_props)
        workspace_layout.addLayout(inst_layout)

        main_layout.addLayout(workspace_layout)

        # Bottom Bar
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(QLabel("Status: New Project | DSP: Float32 | SR: 48000"))
        main_layout.addLayout(bottom_layout)

        # Connections
        self.play_button.clicked.connect(self.on_play_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)

    @Slot()
    def on_play_clicked(self) -> None:
        self.command_bus.push(("play",))
        self.status_label.setText("Playing")

    @Slot()
    def on_stop_clicked(self) -> None:
        self.command_bus.push(("stop",))
        self.status_label.setText("Stopped")
