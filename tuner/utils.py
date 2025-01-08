import numpy as np

A4_FREQUENCY = 440.0

def frequency_to_midi(frequency):
    """Convert frequency to the closest MIDI note."""
    if frequency is None:
        return -128

    if frequency <= 0:
        return -128
    midi_number = 69 + 12 * np.log2(frequency / A4_FREQUENCY)
    return round(midi_number)

def frequency_to_midi_with_cents(frequency):
    if frequency is None:
        return -128

    """Convert frequency to the closest MIDI note."""
    if frequency <= 0:
        return -128
    midi_number = 69 + 12 * np.log2(frequency / A4_FREQUENCY)
    return midi_number

def frequency_to_cents(f1, f2):
    """Convert the frequency difference between two notes into cents."""
    if f1 is None or f2 is None:
        return None

    ratio = f2 / f1
    cents = 1200 * np.log2(ratio)
    return cents

def midi_to_note_name(midi_number):
    """Convert MIDI number to its note name."""
    if midi_number is None or midi_number < -64:
        return "..."

    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = round(midi_number // 12) - 1
    return f"{notes[round(midi_number) % 12]}{octave}" if octave >= 0 else ""


def semitone_to_midi(semitones, octave):
    """Convert note to its MIDI number, where A4 is semitones=0 octave=4."""

    octave_midi = (octave + 1) * 12
    return octave_midi + semitones

def midi_to_frequency(midi_number=69+12):
    if midi_number <= 0:
        return None
    frequency = A4_FREQUENCY * 2 ** ((midi_number - 69) / 12)
    return frequency