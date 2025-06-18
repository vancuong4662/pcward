import sys
import psutil
import platform
import GPUtil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QScrollArea
)
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtCore import Qt

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

class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thông số hệ thống máy tính")
        self.setGeometry(100, 100, 500, 400)

        tabs = QTabWidget()
        tabs.addTab(self.create_tab(get_system_info()), "Hệ thống")
        tabs.addTab(self.create_tab(get_cpu_info()), "CPU")
        tabs.addTab(self.create_tab(get_ram_info()), "RAM")
        tabs.addTab(self.create_tab(get_disk_info()), "Ổ đĩa")
        tabs.addTab(self.create_tab(get_gpu_info()), "GPU")

        self.setCentralWidget(tabs)

    def create_tab(self, text):
        widget = QWidget()
        layout = QVBoxLayout()
        # Container cho label
        container = QWidget()
        vbox = QVBoxLayout()
        label = QLabel(text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet("font-size: 13px;")
        label.setWordWrap(True)
        vbox.addWidget(label, alignment=Qt.AlignmentFlag.AlignTop)
        vbox.addStretch(1)
        container.setLayout(vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll)
        widget.setLayout(layout)
        return widget

def setup_custom_font(app, ttf_path="font-default.ttf", font_size=14):
    """
    Nạp font .ttf và đặt làm font mặc định cho app.
    """
    font_id = QFontDatabase.addApplicationFont(ttf_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, font_size))
    else:
        print(f"Không thể nạp font từ {ttf_path}, sẽ dùng font mặc định.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Đặt font tùy chỉnh ở đây. Đổi tên file font nếu cần.
    setup_custom_font(app, ttf_path="font-pro.ttf", font_size=12)
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec())