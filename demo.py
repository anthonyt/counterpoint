#!/usr/bin/python
# -*- coding: utf-8 -*-

from mingus.midi.MidiFileIn import MIDI_to_Composition
from mingus.midi.MidiFileOut import write_Composition
from mingus.containers import Note, NoteContainer, Bar, Composition, Instrument, Track
from mingus.extra.LilyPond import from_Composition, to_png, to_pdf
from structures import Soprano, Alto, Tenor, Bass, NoteNode, NoteList, create_note_lists
from rules import *
from tracks import melodies, cantus_firmus, key, meter, species, author

###
# WE'RE GOING TO MAKE A MAJOR ASSUMPTION IN THIS PROGRAM, AND ASSUME THAT
# NO TRACK WILL HAVE POLYPHONY. ALL NOTES IN A TRACK WILL START ONLY AFTER
# THE PREVIOUS NOTE HAS FINISHED.
###

# Create a composition, and add the vocal tracks to it.
composition = Composition()
composition.set_title('Counterpoint Exercise', '')
composition.set_author(author, '')

# Set up our vocal 'tracks' with the notes, key, meter defined in tracks.py
tracks = {}
for voice in [Soprano, Alto, Tenor, Bass]:
    if len(melodies[voice.name]):
        tracks[voice.name] = Track(instrument=voice())
        tracks[voice.name].add_bar(Bar(key=key, meter=meter))
        tracks[voice.name].name = voice.name
        for note in melodies[voice.name]:
            tracks[voice.name].add_notes(*note)
        composition.add_track(tracks[voice.name])

# Save the midi file!
write_Composition('demo.mid', composition, verbose=True)

# Save the PNG
string = from_Composition(composition)
to_png(string, 'demo.png')

# Compute and print out the errors.
rulesets = [first_species, second_species, third_species, fourth_species]
errors = rulesets[species-1](composition)
length = max(*[len(s) for s in errors]) + 2
for key in errors:
    print key
    print errors[key]
    print ""

