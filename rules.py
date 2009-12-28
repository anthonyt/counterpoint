# -*- coding: utf-8 -*-

from mingus.core import intervals as mintervals
from mingus.containers import Note
from mingus.core.diatonic import get_notes
from structures import create_note_lists
from views import *


def all_notes_line_up(a_list, b_list):
    """
    Takes two lists of NoteNode objects. These may be NoteList objects.
    Returns 2 lists.
    The first list contains the NoteNode objects in a_list that are unmatched in b_list.
    The second list contains the NoteNode objects in b_list that are unmatched in a_list.
    """
    a_list = [x for x in a_list if not x.is_rest] # copy NoteList to list
    b_list = [x for x in b_list if not x.is_rest] # copy NoteList to list

    # remove matched notes
    for a_note in a_list[:]:
        for b_note in b_list[:]:
            if (a_note.start, a_note.end) == (b_note.start, b_note.end):
                # remove the matched pair from their respective lists
                a_list.remove(a_note)
                b_list.remove(b_note)
                break

    return a_list, b_list

def illegal_parallel_intervals(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to parallel_motion() above.
    Sub-lists here will only contain illegal sets of parallel intervals,
    however.

    From the rules of first species counterpoint:
        Only 3rds and 6ths (and their octaves) may be repeated.
    """
    allowed_parallel_intervals = ['3', '6']
    consecutives = parallel_motion(a_list, b_list)

    return [
        c for c in consecutives
        if c[0][0][0] not in allowed_parallel_intervals
    ]

def illegal_consecutive_parallels(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to parallel_motion() above.
    Sub-lists here will only contain illegal sets of parallel intervals,
    however.

    From the rules of first species counterpoint:
        Any one interval may be repeated a maximum of three times consecutively.
    """
    max_consecutive_parallel = 3
    consecutives = parallel_motion(a_list, b_list)

    return [c for c in consecutives if len(c) > max_consecutive_parallel]

def coincident_maxima(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to local_maxima() above.
    Tuples returned here will only include note-onsets that are local maxima
    in both provided NoteList melodies, however.
    """
    a_maxima = local_maxima(a_list)
    b_maxima = local_maxima(b_list)

    return [x for x in a_maxima if x in b_maxima]

def voice_crossing(b_list, a_list, note_spacing=2, note_filter_fn=None):
    """
    Takes two NoteList objects and an integer.

    note_spacing parameter defines how many previous notes to consider when
    looking for voice crossings.
    1 means consider only the immediate note.
    2 means consider the previous note also.
    3 etc.

    Returns a list of notes that infringe on each other's space.
    a_list must represent the lower voice
    b_list must represent the higher voice

    Returns a list of tuples, each of the form:
        (NoteNode, NoteNode)
    """
    crossings = []

    def f_v_c(c_list, d_list, comparator):
        c_notes = [c for c in c_list]
        if callable(note_filter_fn):
            c_notes = filter(note_filter_fn, c_notes)
        d_notes = [d_list.get_note_playing_at(c.bar, c.beat) for c in c_notes]

        for x in range(0, note_spacing):
            if x > 0:
                d_notes = [d.prev for d in d_notes]
                d_notes.pop(0)
                c_notes.pop(0)

            for i in range(0, len(c_notes)):
                c = c_notes[i]
                d = d_notes[i]

                if c is None or d is None or c.is_rest or d.is_rest:
                    continue
                if comparator(int(c), int(d)):
                    if (d, c) not in crossings:
                        crossings.append((c, d))

    f_v_c(a_list, b_list, lambda a,b: a >= b)
    f_v_c(b_list, a_list, lambda a,b: a <= b)
    return crossings

def illegal_vertical_intervals(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to vertical_intervals() above.

    Returned tuples here, however, will only represent intervals that are
    not explicitly allowed by the allowed_intervals list.
    """
    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6']
    pairs = vertical_intervals(a_list, b_list)
    return [(i, t) for i, t in pairs if i[0] not in allowed_intervals]

def illegal_horizontal_intervals(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to horizontal_intervals() above.

    Returned tuples here will only represent those intervals that are not
    explicitly allowed by the allowed_movements list below.
    """
    allowed_movements = ['1', 'b2', '2', 'b3', '3', '4', '5', 'b6', '6']
    intervals = horizontal_intervals(a_list)
    return [(i, a_list[x+1]) for x,i in enumerate(intervals) if i[0] not in allowed_movements]

def illegal_indirect_horizontal_intervals(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to indirect_horizontal_intervals() above.

    Intervals represented here, however, are only those that are not
    explicitly allowed by the allowed_intervals list below.
    """
    allowed_intervals = ['1', 'b2', '2', 'b3', '3', '4', '5', 'b6', '6']
    intervals = indirect_horizontal_intervals(a_list)
    return [x for x in intervals if x[0][0] not in allowed_intervals]

def illegal_strong_beat_horizontal_intervals(a_list):
    allowed_intervals = ['1', 'b2', '2', 'b3', '3', '4', '5', 'b6', '6']
    intervals = strong_beat_horizontal_intervals(a_list)
    return [x for x in intervals if x[0][0] not in allowed_intervals]

def missed_leap_turnarounds(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to note_onsets() above.

    The only tuples returned here, however, are those that represent the
    onset of a note which has been approached by a leap greater than
    half an octave, and which has not been left by step in the opposite
    direction.
    """
    # immediately after a leap of (P5, m6, M6, P8), must move by step (m2, M2)
    # in opposite direction
    largest_leap_without_turnaround = 6 # semitones

    # get horizontal intervals as semitones
    h_i_semitones = [get_semitones(x) for x in horizontal_intervals(a_list)]

    # get list of directions for each interval
    dirs = directions(a_list)

    # figure out if the next movement after this one is a step in the opposite direction
    def turns_around_after(i):
        # is this the last interval?
        leap_dir, leap_time = dirs[i+1]
        leap_int = h_i_semitones[i]

        while i < len(h_i_semitones):
            i += 1

            next_dir, next_time = dirs[i+1]
            next_int = h_i_semitones[i]

            if next_int == 0: # doesn't move yet?
                continue
            elif next_dir == -leap_dir and next_int <= 2: # moves by step in opposite dir?
                return True
            else: # doesn't move by step in opposite dir :(
                return False
        return False

    # find all intervals that qualify as a leap
    invalid_leaps = [i for i,interval in enumerate(h_i_semitones)
               if interval > largest_leap_without_turnaround
               and not turns_around_after(i)]

    # return a list of the beats (notes) that have the leaped-to note
    # the note following these ones need to move in opposite direction by step
    return [dirs[i+1][1] for i in invalid_leaps]

def illegal_direct_motion(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to vertical_intervals() above.

    Intervals returned here, however, only represent intervals explicitly
    defined in the illegal_direct_intervals list below, which have been
    approached through similar motion (ie. both voices moving in the same
    direction)
    """
    illegal_direct_intervals = ['5', '1']
    illegal_direct_motions = []
    direct_motions = direct_motion(a_list, b_list)

    for x in direct_motions:
        (interval, octaves), time = x

        if interval in illegal_direct_intervals:
            illegal_direct_motions.append(x)

    return illegal_direct_motions

def starts_with_tonic(a_list):
    """
    Takes a single NoteList object.

    Returns an empty list if the first non-rest note in the melody is the tonic
    of the key defined by the first bar in the melody.

    Returns a list containing the start time of the first melodic note,
    otherwise.
    """
    key = a_list.track.bars[0].key.name
    note = a_list.get_first_actual_note()
    if note.name == key:
        return []
    else:
        return [note.start]


def starts_with_tonic_or_fifth(a_list):
    """
    Takes a single NoteList object.

    Returns an empty list if the first non-rest note in the melody is the tonic
    or the fifth of the key defined by the first bar in the melody.

    Returns a list containing the start time of the first melodic note,
    otherwise.
    """
    key = a_list.track.bars[0].key
    note = a_list.get_first_actual_note()
    possible_notes = [key.name, Note(key).transpose('5', True).name]
    if note.name in possible_notes:
        return []
    else:
        return [note.start]

def ends_with_lt_tonic(a_list):
    """
    Takes a single NoteList object.

    Returns an empty list if the last two notes in the melody are the leading
    tone and tonic of the key defined by the first bar in the melody.

    Returns a list containing the start time of each infringing note, otherwise
    """
    key = a_list.track.bars[0].key
    a, b = a_list.notes[-2:]
    lt, tonic = Note(key).transpose('7', True).name, key.name

    if (a.name, b.name) == (lt, tonic) and int(b) - int(a) == 1:
        return []
    else:
        return [a.start, b.start]

def accidentals(a_list):
    """
    Takes a single NoteList object.

    Returns a list of NoteNode objects from the melody that do not exist
    in the key defined by the first bar in the melody.
    """
    key = a_list.track.bars[0].key
    notes_in_key = get_notes(key.name)
    return [
        note for note in a_list
        if note.name not in notes_in_key
        and not note.is_rest
    ]

def legal_dissonances(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to vertical_intervals() above.

    Returned tuples here, however, will only represent intervals that are
    illegal in first species counterpoint, but legal in second species.

    Second Species Exception:
    Dissonant intervals that fall on weak beats, that are approached and left by step
    are okay.
    """
    def interval_is_step(x):
        return get_semitones(x) <= 2

    def approached_and_left_by_step(interval):
        i, t = interval
        a_note = a_list.get(*t)
        b_note = b_list.get(*t)

        if a_note is not None and b_note is not None:
            # both voices moved at the same time to get into the dissonance.
            # that means neither is cf, so both must leave by step
            a_approach = get_interval(a_note, a_note.prev)
            b_approach = get_interval(b_note, b_note.prev)
            a_depart = get_interval(a_note, a_note.next)
            b_depart = get_interval(b_note, b_note.next)

            movements = [a_approach, b_approach, a_depart, b_depart]
        else:
            # one of the notes was already playing, (probably the c.f.)
            # that note can do whatever it wants.
            # just make sure c_note was approached and left by step
            if a_note is not None:
                c_note = a_note
            elif b_note is not None:
                c_note = b_note
            c_approach = get_interval(c_note, c_note.prev)
            c_depart = get_interval(c_note, c_note.next)

            movements = [c_approach, c_depart]

        return all(map(
            interval_is_step,
            movements
        ))

    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6']
    pairs = vertical_intervals(a_list, b_list)
    weak_intervals = [(i, t) for i, t in pairs if t[1] == 0.5]
    weak_dissonances = [(i, t) for i, t in weak_intervals if i[0] not in allowed_intervals]
    safe_dissonances = [
        x for x in weak_dissonances
        if approached_and_left_by_step(x)
    ]
    return safe_dissonances


def get_and_split_note_lists(composition):
    """
    Takes a mingus.containers.Composition object.

    Converts the Composition to a categorized set of NoteLists.

    Assumes that composition will have Soprano, Alto, Tenor, Bass tracks.
    Also assumes that at least two of these tracks have content.
    Also assumes that Soprano track is higher than Alto track, etc.

    Returns a tuple:
    (
        dict of all voices (key => track name; value => NoteList),
        NoteList that represents the high voice,
        NoteList that represents the low voice,
        List of NoteLists that represent the inner voices,
        List of all possible combinations of voices, each represented by a tuple (a, b)
    )
    """
    lists = create_note_lists(composition)

    # create a dict of all tracks with notes in them
    n = {}
    for voice in lists:
        if len(lists[voice]):
            n[voice] = lists[voice]

    descending_voices = [x for x in ['Soprano', 'Alto', 'Tenor', 'Bass'] if x in n]
    ascending_voices = [x for x in['Bass', 'Tenor', 'Alto', 'Soprano'] if x in n]

    # find the high voice
    for voice in descending_voices:
        high_voice = n[voice]
        break

    # find the low voice
    for voice in ascending_voices:
        low_voice = n[voice]
        break

    # find the inner voices
    inner_voices = []
    for voice in ['Tenor', 'Alto']:
        if voice in n and n[voice] not in [high_voice, low_voice]:
            inner_voices.append(n[voice])

    # find all possible combinations of voices
    voice_combos = []
    for i,x in enumerate(descending_voices):
        for y in descending_voices[i+1:]:
            voice_combos.append((x, y))

    return n, high_voice, low_voice, inner_voices, voice_combos

