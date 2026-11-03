import sys
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QFileDialog, QLabel, QComboBox,
    QProgressBar, QMessageBox
)

class ConvertWorker(QThread):
    progress = Signal(int, str)
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, sources, output_dir, quality):
        super().__init__()
        self.sources = sources
        self.output_dir = Path(output_dir)
        self.quality = quality
        self.cancelled = False

    def run(self):
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        total = len(self.sources)
        for index, source in enumerate(self.sources, 1):
            if self.cancelled:
                self.failed.emit("转换已取消")
                return
            src = Path(source)
            target = self.output_dir / (src.stem + ".mp3")
            if target.exists():
                target = self.output_dir / (src.stem + "_converted.mp3")
            args = [ffmpeg, "-y", "-i", str(src), "-vn", "-codec:a",
                    "libmp3lame", "-q:a", self.quality, str(target)]
            try:
                result = subprocess.run(args, capture_output=True, text=True,
                                        encoding="utf-8", errors="replace")
                if result.returncode != 0:
                    raise RuntimeError(result.stderr[-1500:] or "FFmpeg 转换失败")
                self.progress.emit(int(index * 100 / total), f"已完成 {index}/{total}: {target.name}")
            except Exception as exc:
                self.failed.emit(f"{src.name}\n{exc}")
                return
        self.done.emit(str(self.output_dir))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP4 转 MP3 转换器")
        self.resize(720, 520)
        self.files = []
        self.output_dir = str(Path.home() / "Music")
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel("添加 MP4 视频，提取音轨并保存为 MP3"))
        row = QHBoxLayout()
        add = QPushButton("添加视频")
        add.clicked.connect(self.add_files)
        remove = QPushButton("移除选中")
        remove.clicked.connect(self.remove_selected)
        clear = QPushButton("清空列表")
        clear.clicked.connect(self.clear_files)
        row.addWidget(add); row.addWidget(remove); row.addWidget(clear)
        layout.addLayout(row)
        self.list = QListWidget()
        layout.addWidget(self.list, 1)
        quality_row = QHBoxLayout()
        quality_row.addWidget(QLabel("MP3 音质："))
        self.quality = QComboBox()
        self.quality.addItem("高音质（约 190 kbps）", "2")
        self.quality.addItem("标准（约 130 kbps）", "4")
        self.quality.addItem("较小文件（约 100 kbps）", "6")
        quality_row.addWidget(self.quality)
        layout.addLayout(quality_row)
        out_row = QHBoxLayout()
        self.out_label = QLabel(f"输出文件夹：{self.output_dir}")
        choose = QPushButton("选择输出文件夹")
        choose.clicked.connect(self.choose_output)
        out_row.addWidget(self.out_label, 1); out_row.addWidget(choose)
        layout.addLayout(out_row)
        self.bar = QProgressBar()
        layout.addWidget(self.bar)
        self.status = QLabel("等待添加 MP4 文件")
        layout.addWidget(self.status)
        self.start = QPushButton("开始转换 MP4 → MP3")
        self.start.setMinimumHeight(46)
        self.start.clicked.connect(self.convert)
        layout.addWidget(self.start)

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "选择 MP4 视频", "",
                                                "视频文件 (*.mp4 *.m4v *.mov *.mkv *.avi *.webm)")
        for path in paths:
            if path not in self.files:
                self.files.append(path)
                self.list.addItem(path)

    def remove_selected(self):
        for item in self.list.selectedItems():
            path = item.text()
            if path in self.files:
                self.files.remove(path)
            self.list.takeItem(self.list.row(item))

    def clear_files(self):
        self.files.clear()
        self.list.clear()

    def choose_output(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.output_dir)
        if folder:
            self.output_dir = folder
            self.out_label.setText(f"输出文件夹：{folder}")

    def convert(self):
        if not self.files:
            QMessageBox.information(self, "提示", "请先添加 MP4 文件")
            return
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.start.setEnabled(False)
        self.bar.setValue(0)
        self.worker = ConvertWorker(self.files[:], self.output_dir,
                                    self.quality.currentData())
        self.worker.progress.connect(self.on_progress)
        self.worker.done.connect(self.on_done)
        self.worker.failed.connect(self.on_failed)
        self.worker.start()

    def on_progress(self, value, message):
        self.bar.setValue(value)
        self.status.setText(message)

    def on_done(self, folder):
        self.start.setEnabled(True)
        self.status.setText("全部转换完成")
        QMessageBox.information(self, "完成", f"MP3 已保存到：\n{folder}")

    def on_failed(self, message):
        self.start.setEnabled(True)
        QMessageBox.warning(self, "转换失败", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
