import streamlit as st
import numpy as np

st.header("Song Maker")

#🎸🎸

# Sample rate and base note duration
sample_rate = 44100  # 44100 samples per second
base_duration = 0.4  # Base note duration

def generate_note(frequency, duration_multiplier=1):
    duration = base_duration * duration_multiplier
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    note = np.sin(frequency * t * 2 * np.pi)
    return note  # This should be a one-dimensional array


# Function to generate a chord (multiple notes played together)
def generate_chord(frequencies, duration_multiplier=1):
    chord = np.zeros(int(base_duration * duration_multiplier * sample_rate))
    for frequency in frequencies:
        chord += generate_note(frequency, duration_multiplier)
    return chord  # This should be a one-dimensional array





# Frequencies for different notes (A4, B4, C5, etc.)
frequencies = {
    'A': 440.00,
    'B': 493.88,
    'C': 523.25,
    'D': 587.33,
    'E': 659.25,
    'F': 698.46,
    'G': 783.99,
    'A#': 466.16, 'Bb': 466.16,
    'C#': 554.37, 'Db': 554.37,
    'D#': 622.25, 'Eb': 622.25,
    'F#': 739.99, 'Gb': 739.99,
    'G#': 830.61, 'Ab': 830.61,
    # Add more notes as needed
}

chords = {
    'C': ['C', 'E', 'G'],
    'Dm': ['D', 'F', 'A'],
    'Em': ['E', 'G', 'B'],
    'F': ['F', 'A', 'C'],
    'G': ['G', 'B', 'D'],
    'Am': ['A', 'C', 'E'],
    # Add more chords as needed
}

def play_song(song_sequence):
    melody = []
    for element in song_sequence:
        note_or_chord, duration_multiplier = element
        if isinstance(note_or_chord, str):  # Single note or chord shorthand
            if note_or_chord in frequencies:  # It's a single note
                melody.append(generate_note(frequencies[note_or_chord], duration_multiplier))
            elif note_or_chord in chords:  # It's a chord shorthand
                chord_frequencies = [frequencies[note] for note in chords[note_or_chord]]
                melody.append(generate_chord(chord_frequencies, duration_multiplier))
        elif isinstance(note_or_chord, list):  # Explicit list of notes (custom chord)
            chord_frequencies = [frequencies[note] for note in note_or_chord]
            melody.append(generate_chord(chord_frequencies, duration_multiplier))

    song = np.concatenate(melody)
    st.audio(song, sample_rate=sample_rate)







## SONGS

st.write("Twinkle Twinkle Little Star")
twinkle_twinkle_full = [
    ('C', 1), ('C', 1), ('G', 1), ('G', 1), ('A', 1), ('A', 1), ('G', 2),
    ('F', 1), ('F', 1), ('E', 1), ('E', 1), ('D', 1), ('D', 1), ('C', 2),
    # Adding a chord progression
    ('C', 1), ('G', 1), ('Am', 1), ('F', 1),
    ('C', 1), ('G', 1), ('F', 1), ('C', 2),
]

twinkle_twinkle_fullv2 = [
    ('C', 1), ('C', 1), ('G', 1), ('G', 1), ('A', 1), ('A', 1), ('G', 1),  # C major chord and melody
    ('F', 1), ('F', 1), ('E', 1), ('E', 1), ('D', 1), ('D', 1), ('C', 1),  # F major chord and melody
    ('G', 1), ('G', 1), ('F', 1), ('F', 1), ('E', 1), ('E', 1), ('D', 1),  # G major chord and melody
    ('G', 1), ('G', 1), ('F', 1), ('F', 1), ('E', 1), ('E', 1), ('D', 1),  # G major chord and melody
    ('C', 1), ('C', 1), ('G', 1), ('G', 1), ('A', 1), ('A', 1), ('G', 1),  # C major chord and melody
    ('F', 1), ('F', 1), ('E', 1), ('E', 1), ('D', 1), ('D', 1), ('C', 1),  # F major chord and melody
]


play_song(twinkle_twinkle_fullv2)

st.write("AI original song 1")
song_sequence = [
    ('C', 1), ('E', 0.5), ('G', 0.5),  # C major chord and melody
    ('Am', 1), ('C', 0.5), ('E', 0.5),  # A minor chord and melody
    ('F', 1), ('A', 0.5), ('C', 0.5),  # F major chord and melody
    ('G', 1), ('B', 0.5), ('D', 0.5),  # G major chord and melody
    # Repeat
    ('C', 1), ('E', 0.5), ('G', 0.5),
    ('Am', 1), ('C', 0.5), ('E', 0.5),
    ('F', 1), ('A', 0.5), ('C', 0.5),
    ('G', 1), ('B', 0.5), ('D', 0.5),
]
play_song(song_sequence)

st.write("AI point and click game song")
loop_sequence = [
    ('Am', 1), ('A', 0.5), ('C', 0.5),  # A minor chord and melody
    ('Dm', 1), ('D', 0.5), ('F', 0.5),  # D minor chord and melody
    ('E', 1), ('E', 0.5), ('G', 0.5),   # E major chord and melody
    ('Am', 1), ('A', 0.5), ('C', 0.5),  # A minor chord and melody
    ('F', 1), ('F', 0.5), ('A', 0.5),   # F major chord and melody
    ('C', 1), ('C', 0.5), ('E', 0.5),   # C major chord and melody
    ('G', 1), ('G', 0.5), ('B', 0.5),   # G major chord and melody
    ('E', 1), ('E', 0.5), ('G', 0.5),   # E major chord and melody
]
song_sequence = loop_sequence * 6  # Repeating 6 times for around 60 seconds
play_song(song_sequence)









#######################################################################

st.markdown("---")




st.write("early tests")

st.write("test")
# Function to generate a single note


# Melody: sequence of notes
melody_notes = ['C', 'D', 'E', 'C', 'E', 'D', 'C']

# Generate melody
melody = np.concatenate([generate_note(frequencies[note]) for note in melody_notes])

# Play the melody
st.audio(melody, sample_rate=sample_rate)

## song test end

st.write("test 2")



# Function to play a fantasy song
def play_song_test():
    melody = []

    # Example melody
    melody.append(generate_chord(['C', 'E', 'G'], 1.5))  # C Major chord
    melody.append(generate_note(frequencies['E'], 0.5))
    melody.append(generate_note(frequencies['G'], 0.75))
    melody.append(generate_note(frequencies['C'], 1))
    melody.append(generate_chord(['A', 'C', 'E'], 1.5))  # A Minor chord
    melody.append(generate_note(frequencies['A'], 0.5))
    # Add more notes and chords as desired

    # Convert list to numpy array and play it
    #song = np.concatenate(melody)
    #st.audio(song, sample_rate=sample_rate)
    
    # Convert list to numpy array and play it
    song = np.hstack(melody)
    st.audio(song, sample_rate=sample_rate)

# Call the function to play the song
play_song_test()
