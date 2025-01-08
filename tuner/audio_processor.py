import numpy as np
import pyaudio
from multiprocessing import Process, Queue
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

class AudioProcessor:
    def __init__(self, sample_rate=12000, buffer_size=4096, channels=1):
        self.ui = None
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.stream = None
        self.pyaudio = pyaudio.PyAudio()
        self.worker = None
        self.worker_interval = round(self.sample_rate / self.buffer_size)
        self.queue = Queue()

    def start(self, ui):
        self.ui = ui
        self.worker = AudioWorker(self.queue, self.ui, self.sample_rate, self.buffer_size, channels=self.channels)

    def start_audio_worker(self):
        """Start the audio worker thread."""
        self.worker.start()
        # Use a QTimer to periodically check for new results from the queue
        self.check_worker()

    def check_worker(self):
        # Check if the queue has any new data from the worker process
        if not self.queue.empty():
            result = self.queue.get()  # Get data from the queue
            self.ui.update_display_fft_data(result)

        # Re-run this method to check the queue every 100ms
        QTimer.singleShot(round(self.sample_rate / self.buffer_size), self.check_worker)

    def pause_audio_worker(self):
        self.worker.pause_stream()

    def unpause_audio_worker(self):
        self.worker.unpause_stream()
    
    def stop_audio_worker(self):
        self.worker.terminate_stream()

# TODO: rewrite audio worker
# Worker class that processes audio data and calculates FFT
class AudioWorker(QThread):
    result = (np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, queue, ui, sample_rate=48000, buffer_size=1024, channels=1):
        super().__init__()
        self.queue = queue
        self.ui = ui
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.buffer_size)
        self.max_fft_peaks = 10
        self.running = True  # Flag to control the worker's run loop
    
    def increase_buffer_size(self):
        self.close_stream()
        self.buffer_size *= 2
        self.create_stream()

    def decrease_buffer_size(self):
        self.close_stream()
        self.buffer_size //= 2
        self.create_stream()
        
    def create_stream(self):
        if self.p is None:
            self.p = pyaudio.PyAudio()

        if self.running:
            print(f"warning: stream already created, not starting another.")
            return

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.buffer_size)
        self.max_fft_peaks = 10
        self.running = True  # Flag to control the worker's run loop
        self.start()

    def run(self):
        while self.running:
            try:
                # Capture audio data
                audio_data = np.frombuffer(self.stream.read(self.buffer_size), dtype=np.int16)

                # Perform FFT
                fft_data = np.fft.fft(audio_data)
                frequencies = np.fft.fftfreq(len(fft_data), 1 / self.sample_rate)
                magnitudes = np.abs(fft_data)

                # Get positive frequencies and corresponding magnitudes
                positive_frequencies = frequencies[:len(frequencies) // 2]
                positive_magnitudes = magnitudes[:len(magnitudes) // 2]

                # positive_magnitudes[0] = 0

                # Identify the peaks
                peaks_idx = np.argsort(positive_magnitudes)[-self.max_fft_peaks:]  # Get top 5 peaks
                peak_frequencies = positive_frequencies[peaks_idx]
                peak_magnitudes = positive_magnitudes[peaks_idx]

                # Emit the frequency and magnitude data to the UI thread
                # self.fft_data_signal.emit(positive_frequencies, positive_magnitudes, peaks_idx, peak_frequencies, peak_magnitudes)  # Emit signal
                result = (positive_frequencies, positive_magnitudes, peaks_idx, peak_frequencies, peak_magnitudes)
                self.queue.put(result)

            except Exception as e:
                print(f"error while processing audio data: {e}")
                break

    def pause_stream(self):
        """Gracefully stop the worker thread."""
        self.running = False
        self.wait()  # Wait for the thread to finish
    
    def unpause_stream(self):
        self.running = True
        self.start()
    
    def close_stream(self):
        # Stop the audio stream and terminate PyAudio
        self.pause_stream()
        self.stream.stop_stream()
        self.stream.close()
    
    def terminate_stream(self):
        self.close_stream()
        self.p.terminate()