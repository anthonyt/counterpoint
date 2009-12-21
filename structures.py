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
        self.bar = bar
        self.beat = beat
        self.duration = duration

        if noteContainer is None or len(noteContainer) == 0:
            self.is_rest = True
            self.name = 'Rest'
            self.octave = 0
        else:
            self.is_rest = False
            note = noteContainer[0]
            Note.__init__(self, note)

    def __repr__(self):
        name = Note.__repr__(self)
        return "<NoteNode %s, %d, %0.2f, %d>" % (name, self.bar, self.beat, self.duration)

    def __eq__(self, other):
        return self is other

    @property
    def prev_actual_note(self):
        prev = self.prev
        while prev is not None and prev.is_rest:
            prev = prev.prev
        return prev

    @property
    def next_actual_note(self):
        next = self.next
        while next is not None and next.is_rest:
            next = next.next
        return next

    @property
    def start(self):
        return (self.bar, self.beat)

    @property
    def end(self):
        return (self.bar, self.beat + 1./self.duration)

    @property
    def pitch_end(self):
        # when does this pitch end?
        # NB: this method treats all consecutive identical pitches as
        #     one long tied note.
        cur = self
        while cur.next is not None and int(cur.next) == int(self):
            cur = cur.next
        end_beat = cur.beat + 1./cur.duration
        return (cur.bar, end_beat)

class NoteList(object):
    notes = None
    track = None

    def __init__(self, track):
        self.notes = []
        self.track = track

        bars = track.bars
        for i in range(0, len(bars)):
            last_beat = 0.0
            bar = bars[i]
            for n in bar:
                beat, duration, noteContainer = n

                if beat > last_beat:
                    # There's a gap between this note and the previous one.
                    # Insert a rest.
                    rest_duration = int(1./(beat - last_beat))
                    rest = NoteNode(None, i, last_beat, rest_duration)
                    self.append(rest)

                note = NoteNode(noteContainer, i, beat, duration)
                self.append(note)
                last_beat = note.end[1]


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

    def get_note_playing_at(self, bar, beat):
        for n in self.notes:
            if n.bar == bar and n.beat <= beat and n.end[1] > beat:
                return n
        return None

    def get_first_actual_note(self):
        # return the first non-rest note.
        note = self.notes[0]
        if note.is_rest:
            note = note.next_actual_note
        return note

    def __repr__(self):
        return "<NoteList %r>" % (self.notes)

    def __getitem__(self, index):
        return self.notes[index]

    def __len__(self):
        return len(self.notes)

def create_note_lists(composition):
    lists = {}
    for track in composition:
        lists[track.name] = NoteList(track)

    return lists
