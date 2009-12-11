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

class Alto(Instrument):
    name = u'Alto'
    range = (Note('F', 3), Note('F', 5))

class Tenor(Instrument):
    name = u'Tenor'
    range = (Note('C', 3), Note('C', 5))

class Bass(Instrument):
    name = u'Bass'
    range = (Note('E', 2), Note('E', 4))

# Set up our vocal 'tracks'
sopranoTrack = Track(instrument=Soprano())
altoTrack = Track(instrument=Alto())
tenorTrack = Track(instrument=Tenor())
bassTrack = Track(instrument=Bass())

# Create a composition, and add the vocal tracks to it.
myComp = Composition()
myComp.set_title('Counterpoint Exercise', 'subtitle')
myComp.set_author('Anthony Theocharis', 'anthony.theocharis@gmail.com')
for track in [sopranoTrack, altoTrack, tenorTrack, bassTrack]:
    track.name = track.instrument.name
    myComp.add_track(track)

# Definition of a tenor melody - one bar per line.
tenorLine = [
    ('E-4', 1),
    ('F-4', 3), ('E-4', 3), ('F-4', 3),
    ('F#-4', 2), ('G-4', 2),
    ('G#-4', 1)
]

# Definition of a bass line - one bar per line.
bassLine = [
    ('E-3', 2), ('D-3', 2),
    ('C-3', 1),
    ('B-2', 2), ('G-2', 2),
    ('E-2', 1)
]

# Add the notes/durations to the appropriate vocal tracks
for x in tenorLine:
    tenorTrack.add_notes(*x)
for x in bassLine:
    bassTrack.add_notes(*x)

# Brief printout/analysis of notes that sound together
for track in myComp.tracks:
    print track
print ""

for i in range(0, len(tenorTrack.bars)):
    t = tenorTrack.bars[i]
    b = bassTrack.bars[i]
    for x in t:
        print 'Tenor Notes:', x
        print 'Simultaneously Sounding Bass Notes:', b.get_notes_playing_at(x[0])
        print 'Simultaneously Starting Bass Notes:', b.get_notes_starting_at(x[0])
        print ""

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

