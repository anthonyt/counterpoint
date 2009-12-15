#!/usr/bin/python
# -*- coding: utf-8 -*-

from mingus.midi.MidiFileIn import MIDI_to_Composition
from mingus.midi.MidiFileOut import write_Composition
from mingus.containers import Note, NoteContainer, Bar, Composition, Instrument, Track
from mingus.extra.LilyPond import from_Composition, to_png, to_pdf
from structures import Soprano, Alto, Tenor, Bass, NoteNode, NoteList, createNoteLists
from rules import *

###
# WE'RE GOING TO MAKE A MAJOR ASSUMPTION IN THIS PROGRAM, AND ASSUME THAT
# NO TRACK WILL HAVE POLYPHONY. ALL NOTES IN A TRACK WILL START ONLY AFTER
# THE PREVIOUS NOTE HAS FINISHED.
###

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

# Set up our vocal 'tracks'
sopranoTrack = Track(instrument=Soprano())
altoTrack = Track(instrument=Alto())
tenorTrack = Track(instrument=Tenor())
bassTrack = Track(instrument=Bass())

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

# Save the PNG
string = from_Composition(myComp)
to_png(string, 'demo.png')


note_lists = createNoteLists(myComp)

errors, unmatched_sop, unmatched_alto = \
        all_notes_line_up(note_lists['Soprano'], note_lists['Alto'])

print errors, 'unmatched notes'

"""
Methods we need on each note:
    what is your time signature
    what is your starting beat number
    what is your duration
    what is your key signature
    what is your scale degree
    what is the interval between you and this other note

    get previous note
    get next note
        find next local minimum
        find next local maximum

    we can do this with a
    doubly linked list, with properties like note, midi note number, bar number, beat number, duration, and a reference to the enclosing data structure.
    linked list has accessor functions to get note wrappers by bar/beat number.

"""

