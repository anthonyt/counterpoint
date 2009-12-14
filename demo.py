#!/usr/bin/python
# -*- coding: utf-8 -*-

from mingus.midi.MidiFileIn import MIDI_to_Composition
from mingus.midi.MidiFileOut import write_Composition
from mingus.containers import Note, NoteContainer, Bar, Composition, Instrument, Track
from mingus.extra.LilyPond import from_Composition, to_png, to_pdf

# Set up our vocal classes
class Soprano(Instrument):
    name = u'Soprano'
    range = (Note('C', 4), Note('C', 6))
    clef = 'treble'

class Alto(Instrument):
    name = u'Alto'
    range = (Note('F', 3), Note('F', 5))
    clef = 'treble'

class Tenor(Instrument):
    name = u'Tenor'
    range = (Note('C', 3), Note('C', 5))
    clef = 'tenor'

class Bass(Instrument):
    name = u'Bass'
    range = (Note('E', 2), Note('E', 4))
    clef = 'bass'

# Set up our vocal 'tracks'
sopranoTrack = Track(instrument=Soprano())
altoTrack = Track(instrument=Alto())
tenorTrack = Track(instrument=Tenor())
bassTrack = Track(instrument=Bass())

# First Species Canti Firmi:
cf_1 = [
    ('C-4', 1),
    ('D-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('A-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

harm_1 = [
    ('C-5', 1),
    ('B-4', 1),
    ('A-4', 1),
    ('B-4', 1),
    ('C-5', 1),
    ('D-5', 1),
    ('D-5', 1),
    ('A-4', 1),
    ('B-4', 1),
    ('C-5', 1)
]

cf_2 = [
    ('C-4', 1),
    ('D-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('F-4', 1),
    ('G-4', 1),
    ('A-4', 1),
    ('G-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

cf_3 = [
    ('C-4', 1),
    ('G-3', 1),
    ('A-3', 1),
    ('B-3', 1),
    ('C-4', 1),
    ('D-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('C-4', 1)
]

cf_4 = [
    ('D-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('D-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('A-4', 1),
    ('G-4', 1),
    ('F-4', 1),
    ('E-4', 1),
    ('D-4', 1)
]

# Add the notes/durations to the appropriate vocal tracks
key = 'C'
meter = (4, 4)

# name our vocal tracks something useful
# cf = cantus firmus
# ctp = counterpoint
cf_track = altoTrack
ctp_track = sopranoTrack

cf_track.add_bar(Bar(key=key, meter=meter))
ctp_track.add_bar(Bar(key=key, meter=meter))

for x in cf_1:
    cf_track.add_notes(*x)

for x in harm_1:
    ctp_track.add_notes(*x)

# Create a composition, and add the vocal tracks to it.
myComp = Composition()
myComp.set_title('Counterpoint Exercise', 'subtitle')
myComp.set_author('Anthony Theocharis', 'anthony.theocharis@gmail.com')
for track in [ctp_track, cf_track]:
    track.name = track.instrument.name
    myComp.add_track(track)

# Save the midi file!
write_Composition('demo.mid', myComp, verbose=True)

"""
Useful Method Signatures:

from_Composition(composition):
- returns a string in LilyPonds format

to_png(ly_string, filename):
- Saves a string in LilyPonds format to a PNG. Needs LilyPond in the $PATH.

to_pdf(ly_string, filename):
- Saves a string in LilyPonds format to a PDF. Needs LilyPond in the $PATH.

Bar.place_notes_at(self, notes, duration, beat):
- Write notes (list, NoteContainer, or shorthand string) for 1/duration note, on beat
- Returns True if successful, False if unsuccessful.

write_Composition(file, composition, bpm=120, repeat=0, verbose=False):
- Writes a mingus.Composition to a midi file.

MIDI_to_Composition(file):
- Converts a MIDI file to a mingus.containers.Composition and returns it in a
  tuple with the last used tempo in beats per minute (this will change in the
  future). This function can raise all kinds of exceptions (IOError,
  HeaderError, TimeDivisionError, FormatError), so be sure to try and catch.
"""

