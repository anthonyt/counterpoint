# -*- coding: utf-8 -*-

from mingus.core import intervals as mintervals
from mingus.containers import Note
from mingus.core.diatonic import get_notes
from structures import create_note_lists
from views import *

def get_interval(note_a, note_b):
    """
    Takes two NoteNode objects.
    Returns a tuple of the form:
        (str: interval name, int: octaves between)
    """
    if note_a.is_rest or note_b.is_rest:
        name = ' '
        octave = 0
    else:
        name = mintervals.determine(note_a, note_b, True)
        octave = abs(int(note_a) - int(note_b))/12
    return (name, octave)

def get_semitones(interval_tuplet):
    """
    Takes an interval tuplet of the form returned by get_interval()
    Returns an int representing the semitones within the interval.
    """
    return mintervals.semitones_from_shorthand(interval_tuplet[0]) + 12*interval_tuplet[1]


def get_note_onsets(a_list, b_list):
    """
    Takes two lists of NoteNode objects. These may be NoteList objects.
    Returns a list of tuples, each of the form:
        (int: bar #, float: beat #)
    Each of these tuples represents a time where a note starts in either
    a_list, b_list, or both.
    """
    changes = []
    for l in [a_list, b_list]:
        for note in l:
            if note.start not in changes:
                changes.append(note.start)
    return changes

def get_intervals(a_list, b_list):
    """
    Takes two NoteList objects.
    Returns a list of tuples, each of the form:
    (
        (str: interval name, int: octaves between),
        (int: bar #, float: beat #)
    )
    There is a 1:1 correlation between tuples and note onsets.
    Each tuple represents the interval created by one note onset.
    """

    # find the intervals at each place where a note changes
    changes = get_note_onsets(a_list, b_list)
    intervals = [
        get_interval(
            a_list.get_note_playing_at(bar, beat),
            b_list.get_note_playing_at(bar, beat)
        )
        for bar, beat in changes
    ]

    return zip(intervals, changes)

def combined_directions(a_list, b_list):
    """
    Takes two NoteList objects.
    Returns a list of (3)tuples each of the form:
    (
        int: a dir,
        int: b dir,
        (int: bar #, float: beat #)
    )
    """
    onsets = get_note_onsets(a_list, b_list)
    a_dirs = find_directions(a_list)
    b_dirs = find_directions(b_list)

    dirs = {}
    for time in onsets:
        dirs[time] = (0, 0)
    for dir, time in a_dirs:
        dirs[time] = (dir, dirs[time])
    for dir, time in b_dirs:
        dirs[time] = (dirs[time], dir)

    return [
        (dirs[time][0], dirs[time][1], time)
        for time in onsets
    ]

def find_directions(a_list):
    """
    Takes a NoteList object and a list of (bar, beat) tuples of the form
    returned by get_note_onsets() above.

    Returns a list of tuples representing the direction the melody moves.
    Format:
    (
        int: direction,
        (int: bar #, float: beat #)
    )

    Directions:
     1 for up
     0 for no movement
    -1 for down

    Rests are considered to be no movement.
    The note after a rest is considered to move relative to the note before the rest.
    """

    def get_dir(note):
        if note is None:
            direction = 0
        elif note.is_rest:
            direction = 0
        elif note.prev_actual_note is None:
            direction = 0
        else:
            direction = cmp(int(note), int(note.prev_actual_note))
        return direction

    directions = []
    for a_note in a_list:
        x = (get_dir(a_note), a_note.start)
        directions.append(x)

    return directions

def find_local_minima(a_list):
    """
    Takes a NoteList object.

    Returns a list of tuples of the form returned by get_note_onsets().
    Each of these (int: bar #, float: beat #) tuples will represent the onset
    of a note that is a local minimum in the melody in a_list.
    """
    dirs = find_directions(a_list)
    minima = []

    # started on a low note?
    for cur, time in dirs:
        if cur == 0:
            continue
        elif cur == 1:
            # This is a bit tricky.
            # If the melody starts with a rest, just looking at the directions
            # will imply that the rest is a minimum, so we must find the first
            # non-rest note in the melody. That will be our minimum.
            note = a_list.get_first_actual_note()
            if note is not None:
                minima.append((note.bar, note.beat))
        break

    prev_d = 0
    prev_t = ()
    for dir, time in dirs:
        if prev_d == -1:
            if dir == 0:
                continue
            if dir == 1:
                minima.append(prev_t)
        prev_d = dir
        prev_t = time

    # ended on a low note
    if dir == -1:
        minima.append(time)

    return minima

def find_local_maxima(a_list):
    """
    Takes a NoteList object.

    Returns a list of tuples of the form returned by get_note_onsets().
    Each of these (int: bar #, float: beat #) tuples will represent the onset
    of a note that is a local maximum in the melody in a_list.
    """
    dirs = find_directions(a_list)
    maxima = []

    # started on a high note?
    for cur, time in dirs:
        if cur == 0:
            continue
        elif cur == -1:
            # This is a bit tricky.
            # If the melody starts with a rest, just looking at the directions
            # will imply that the rest is a maximum, so we must find the first
            # non-rest note in the melody. That will be our maximum.
            note = a_list.get_first_actual_note()
            if note is not None:
                maxima.append((note.bar, note.beat))
        break

    prev_d = 0
    prev_t = ()
    for dir, time in dirs:
        if prev_d == 1:
            if dir == 0:
                continue
            if dir == -1:
                maxima.append(prev_t)
        prev_d = dir
        prev_t = time

    # ended on a high note
    if dir == 1:
        maxima.append(time)

    return maxima

def find_horizontal_intervals(a_list):
    """
    Takes a single NoteList object.

    Returns a list of tuples of the form returned by get_interval() above,
    representing the intervals between each pair of consecutive notes in the
    provided NoteList.
    """
    return [
        get_interval(a, a.next_actual_note)
        for a in a_list
        if not a.is_rest
        and a.next_actual_note is not None
    ]

def find_indirect_horizontal_intervals(a_list):
    """
    Takes a single NoteList object.

    Returns a list of tuples representing intervals outlined by consecutive
    local maximum/local minimum pairs.

    Each tuple is of the form:
    (
        (int: bar #, float: beat #),
        (int: bar #, float: beat #),
        (str: interval name, int: octaves between)
    )
    """
    maxima = find_local_maxima(a_list)
    minima = find_local_minima(a_list)

    # Generate max/min pairs for all neighbouring maxima/minima
    if maxima[0][0] > minima[0][0] \
    or (maxima[0][0] == minima[0][0] and maxima[0][1] > minima[0][1]):
        a = minima
        b = maxima
    else:
        a = maxima
        b = minima
    # note that by definition, len(a)-1 <= len(b) <= len(a), as maxima and minima must alternate
    pairs = [(x, b[i]) for i,x in enumerate(a) if i < len(b)]
    pairs2 = [(x, b[i-1]) for i,x in enumerate(a) if i > 0 and i <= len(b)]
    pairs.extend(pairs2)

    intervals = []
    for a, b in pairs:
        x, y = a_list.get(*a), a_list.get(*b)
        if y in [x.next_actual_note, x.prev_actual_note]:
            # ignore 'indirect' intervals that are right beside eachother.
            continue
        i = mintervals.determine(x, y, True)
        intervals.append((i, x, y))
    return intervals

def find_strong_beat_horizontal_intervals(a_list):
    strong_beat_notes = sbn = [x for x in a_list if x.start[1] == 0]

    strong_beat_pairs = [
        (sbn[i], sbn[i+1])
        for i,x in enumerate(sbn)
        if (i+1) < len(sbn)
        and sbn[i] is not None and not sbn[i].is_rest
        and sbn[i+1] is not None and not sbn[i+1].is_rest
    ]

    intervals = [(mintervals.determine(a, b, True), a, b) for a, b in strong_beat_pairs]

    return intervals

