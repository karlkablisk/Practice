import streamlit as st
import numpy as np

st.write("Song Test")

# Sample rate and note duration
sample_rate = 44100  # 44100 samples per second
seconds = 0.4  # Note duration of 0.4 seconds

# Frequencies for different notes
frequencies = {
    'A': 440.00,
    'B': 493.88,
    'C': 523.25,
    'D': 587.33,
    'E': 659.25,
    'F': 698.46,
    'G': 783.99,
    # Add more notes as needed
}

# Function to generate a single note
def generate_note(frequency):
    t = np.linspace(0, seconds, int(seconds * sample_rate), False)
    note = np.sin(frequency * t * 2 * np.pi)
    return note

# Melody: sequence of notes
melody_notes = ['C', 'D', 'E', 'C', 'E', 'D', 'C']

# Generate melody
melody = np.concatenate([generate_note(frequencies[note]) for note in melody_notes])

# Play the melody
st.audio(melody, sample_rate=sample_rate)

## song test end


st.write("song 2 test")



# Sample rate and base note duration
sample_rate = 44100  # 44100 samples per second
base_duration = 0.4  # Base note duration

# Frequencies for different notes (A4, B4, C5, etc.)
frequencies = {
    'A': 440.00,
    'B': 493.88,
    'C': 523.25,
    'D': 587.33,
    'E': 659.25,
    'F': 698.46,
    'G': 783.99,
    # Add more notes as needed
}

# Function to generate a single note with variable duration
def generate_note(frequency, duration_multiplier=1):
    duration = base_duration * duration_multiplier
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    return np.sin(frequency * t * 2 * np.pi)

# Function to generate a chord (multiple notes played together)
def generate_chord(notes, duration_multiplier=1):
    chord = np.zeros(int(base_duration * duration_multiplier * sample_rate))
    for note in notes:
        chord += generate_note(frequencies[note], duration_multiplier)
    return chord / len(notes)  # Normalize the amplitude

# Function to play a fantasy song
def play_song():
    melody = []

    # Example melody
    melody.extend(generate_chord(['C', 'E', 'G'], 1.5))  # C Major chord
    melody.extend(generate_note(frequencies['E'], 0.5))
    melody.extend(generate_note(frequencies['G'], 0.75))
    melody.extend(generate_note(frequencies['C'], 1))
    melody.extend(generate_chord(['A', 'C', 'E'], 1.5))  # A Minor chord
    melody.extend(generate_note(frequencies['A'], 0.5))
    # Add more notes and chords as desired

    # Convert list to numpy array and play it
    song = np.concatenate(melody)
    st.audio(song, sample_rate=sample_rate)

# Call the function to play the song
play_song()
