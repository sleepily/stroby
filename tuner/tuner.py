import sys
from PyQt6.QtWidgets import QApplication
from tuner.audio_processor import AudioProcessor
from tuner.ui import TunerWindow

class Tuner:
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.app = None
        self.ui = None
        self.is_running = False
    
    def start(self):
        self.app = QApplication(sys.argv)

        self.ui = TunerWindow(self)
        self.ui.show()

        self.toggle_tuning_input(first_run=True) # start tuning

        sys.exit(self.app.exec())

    def toggle_tuning_input(self, first_run=False):
        if first_run:
            self.is_running = True
            # print(f"start tuning logic")
            self.audio_processor.start(self.ui)
            self.audio_processor.start_audio_worker()
            self.ui.strobe_container.reset_strobe_wheels()
            return
        else:
            self.is_running = not self.is_running
            # print(f"toggle tuning logic: {self.is_running}")

        # Toggle logic for starting/stopping tuning
        if self.is_running:
            self.audio_processor.unpause_audio_worker()
            self.ui.tuning_button.setText("Pause Tuning")
        else:
            self.audio_processor.pause_audio_worker()
            self.ui.tuning_button.setText("Resume Tuning")

    def buffer_increase(self):
        self.audio_processor.worker.increase_buffer_size()

    def buffer_decrease(self):
        self.audio_processor.worker.decrease_buffer_size()
