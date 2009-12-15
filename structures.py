# -*- coding: utf-8 -*-
from mingus.containers import Note, NoteContainer, Bar, Composition, Instrument, Track

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

class NoteNode(Note):
    prev = None
    next = None

    bar = 0
    beat = 0
    duration = 0

    def __init__(self, noteContainer, bar, beat, duration):
        # assume the notecontainer has at least one note in it.
        note = noteContainer[0]
        self.bar = bar
        self.beat = beat
        self.duration = duration
        Note.__init__(self, note)

    def __repr__(self):
        name = Note.__repr__(self)
        return "<NoteNode %s, %d, %0.2f, %d>" % (name, self.bar, self.beat, self.duration)

class NoteList(object):
    notes = None
    track = None

    def __init__(self, track):
        self.notes = []
        self.track = track

        bars = track.bars
        for i in range(0, len(bars)):
            bar = bars[i]
            for n in bar:
                beat, duration, noteContainer = n
                note = NoteNode(noteContainer, i, beat, duration)
                self.append(note)

    def append(self, note):
        if len(self.notes):
            note.prev = self.notes[-1]
            self.notes[-1].next = note
        self.notes.append(note)

    def get(self, bar, beat):
        for note in self.notes:
            if note.bar == bar and note.beat == beat:
                return note
        return None

    def __repr__(self):
        return "<NoteList %r>" % (self.notes)

    def __getitem__(self, index):
        return self.notes[index]

    def __len__(self):
        return len(self.notes)

def createNoteLists(composition):
    lists = {}
    for track in composition:
        lists[track.name] = NoteList(track)

    return lists
