import sys
import psutil
import platform
import GPUtil
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_system_info():
    uname = platform.uname()
    info = [
        f"Hệ điều hành: {uname.system}",
        f"Tên máy: {uname.node}",
        f"Phiên bản: {uname.version}",
        f"Kiểu máy: {uname.machine}",
        f"Bộ xử lý: {uname.processor}"
    ]
    return "\n".join(info)

def get_cpu_info():
    lines = []
    lines.append(f"Số lõi vật lý: {psutil.cpu_count(logical=False)}")
    lines.append(f"Tổng số lõi (logic): {psutil.cpu_count(logical=True)}")
    cpufreq = psutil.cpu_freq()
    lines.append(f"Xung nhịp tối đa: {cpufreq.max:.2f} MHz")
    lines.append(f"Xung nhịp tối thiểu: {cpufreq.min:.2f} MHz")
    lines.append(f"Xung nhịp hiện tại: {cpufreq.current:.2f} MHz")
    lines.append("Mức sử dụng từng lõi:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        lines.append(f"  Lõi {i}: {percentage}%")
    lines.append(f"Tổng mức sử dụng CPU: {psutil.cpu_percent()}%")
    return "\n".join(lines)

def get_ram_info():
    svmem = psutil.virtual_memory()
    lines = [
        f"Tổng dung lượng: {get_size(svmem.total)}",
        f"Còn trống: {get_size(svmem.available)}",
        f"Đang sử dụng: {get_size(svmem.used)}",
        f"Phần trăm sử dụng: {svmem.percent}%"
    ]
    return "\n".join(lines)

def get_disk_info():
    lines = []
    partitions = psutil.disk_partitions()
    for partition in partitions:
        lines.append(f"Ổ đĩa: {partition.device}")
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        lines.append(f"  Dung lượng tổng: {get_size(usage.total)}")
        lines.append(f"  Đã dùng: {get_size(usage.used)}")
        lines.append(f"  Còn lại: {get_size(usage.free)}")
        lines.append(f"  Phần trăm sử dụng: {usage.percent}%")
        lines.append("")
    return "\n".join(lines)

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    if not gpus:
        return "Không phát hiện GPU hoặc thư viện không hỗ trợ GPU này."
    lines = []
    for i, gpu in enumerate(gpus):
        lines.append(f"GPU {i}: {gpu.name}")
        lines.append(f"  ID: {gpu.id}")
        lines.append(f"  Driver: {gpu.driver}")
        lines.append(f"  VRAM: {gpu.memoryTotal} MB")
        lines.append(f"  VRAM còn trống: {gpu.memoryFree} MB")
        lines.append(f"  VRAM đã dùng: {gpu.memoryUsed} MB")
        lines.append(f"  Mức tải: {gpu.load*100:.1f}%")
        lines.append(f"  Nhiệt độ: {gpu.temperature} °C")
        lines.append("")
    return "\n".join(lines)

class TaskListTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Filter box
        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Lọc theo tên tiến trình hoặc PID...")
        self.filter_edit.textChanged.connect(self.refresh_table)
        filter_layout.addWidget(self.filter_edit)
        main_layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Task Name", "PID", "SES/CON", "Memory (MB)"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Co giãn cột: 40-10-20-30
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        # Tỉ lệ stretch
        header.setStretchLastSection(False)
        header.resizeSection(0, 400)
        header.resizeSection(1, 100)
        header.resizeSection(2, 200)
        header.resizeSection(3, 300)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.set_column_widths()

        main_layout.addWidget(self.table)

        # End Task button
        btn_layout = QHBoxLayout()
        self.end_task_btn = QPushButton("End Task")
        self.end_task_btn.clicked.connect(self.end_task)
        btn_layout.addStretch()
        btn_layout.addWidget(self.end_task_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.refresh_table()

    def set_column_widths(self):
        # Set width by % of total width
        total = 40 + 10 + 20 + 30
        self.table.setColumnWidth(0, int(self.table.width() * 40 / 100))
        self.table.setColumnWidth(1, int(self.table.width() * 10 / 100))
        self.table.setColumnWidth(2, int(self.table.width() * 20 / 100))
        self.table.setColumnWidth(3, int(self.table.width() * 30 / 100))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_column_widths()

    def get_processes(self):
        processes = []
        is_windows = os.name == "nt"
        for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
            try:
                info = proc.info
                # Windows: Dùng session_id, các HĐH khác: luôn SES
                if is_windows:
                    try:
                        sesid = proc.session_id()
                        session = "CON" if sesid == 1 else "SES"
                    except Exception:
                        session = "SES"
                else:
                    session = "SES"
                mem = info['memory_info'].rss / (1024 * 1024)  # MB
                processes.append([
                    info['name'],
                    str(info['pid']),
                    session,
                    f"{mem:.1f}"
                ])
            except Exception:
                continue
        return processes

    def refresh_table(self):
        filter_text = self.filter_edit.text().lower().strip()
        processes = self.get_processes()
        filtered = []
        for row in processes:
            if filter_text == '':
                filtered.append(row)
            else:
                # Lọc theo tên hoặc PID
                if filter_text in row[0].lower() or filter_text in row[1]:
                    filtered.append(row)
        self.table.setRowCount(len(filtered))
        for i, row_data in enumerate(filtered):
            for j, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, j, item)

    def end_task(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Chưa chọn tiến trình", "Vui lòng chọn một tiến trình trước khi tắt.")
            return
        pid_item = self.table.item(selected, 1)
        name_item = self.table.item(selected, 0)
        pid = int(pid_item.text())
        name = name_item.text()
        reply = QMessageBox.question(
            self, "Xác nhận", f"Bạn có chắc muốn tắt tiến trình '{name}' (PID: {pid}) không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                p = psutil.Process(pid)
                p.terminate()
                p.wait(timeout=3)
                QMessageBox.information(self, "Thành công", f"Đã tắt tiến trình '{name}' (PID: {pid})")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tắt tiến trình: {e}")
            self.refresh_table()

class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load custom font
        font_path = os.path.join(os.path.dirname(__file__), "font-pro.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                family = QFontDatabase.applicationFontFamilies(font_id)[0]
                QApplication.setFont(QFont(family))

        self.setWindowTitle("Thông số hệ thống máy tính")
        self.setGeometry(100, 100, 700, 500)

        tabs = QTabWidget()
        tabs.addTab(self.create_tab(get_system_info()), "Hệ thống")
        tabs.addTab(self.create_tab(get_cpu_info()), "CPU")
        tabs.addTab(self.create_tab(get_ram_info()), "RAM")
        tabs.addTab(self.create_tab(get_disk_info()), "Ổ đĩa")
        tabs.addTab(self.create_tab(get_gpu_info()), "GPU")
        tabs.addTab(TaskListTab(), "Task List")

        self.setCentralWidget(tabs)

    def create_tab(self, text):
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet("font-size: 13px; padding-left: 6px;")  # Thêm padding trái
        label.setWordWrap(True)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(label)
        layout.addWidget(scroll)
        layout.addStretch(1)
        widget.setLayout(layout)
        return widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec())