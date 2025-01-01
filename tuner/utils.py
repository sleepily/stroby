import numpy as np

A4_FREQUENCY = 440.0

def frequency_to_midi(frequency):
    """Convert frequency to the closest MIDI note."""
    if frequency <= 0:
        return -128
    midi_number = 69 + 12 * np.log2(frequency / A4_FREQUENCY)
    return round(midi_number)

def frequency_to_midi_with_cents(frequency):
    """Convert frequency to the closest MIDI note."""
    if frequency <= 0:
        return -128
    midi_number = 69 + 12 * np.log2(frequency / A4_FREQUENCY)
    return midi_number

def frequency_to_cents(f1, f2):
    """Convert the frequency difference between two notes into cents."""
    ratio = f2 / f1
    cents = 1200 * np.log2(ratio)
    return cents
