# -*- coding: utf-8 -*-

from mingus.core import intervals as mintervals
from mingus.containers import Note
from mingus.core.diatonic import get_notes
from structures import create_note_lists


def get_interval(note_a, note_b):
    """
    Takes two NoteNode objects, returns a tuple of the form
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
    Returns the semitone equivalent of the interval as an integer
    """
    return mintervals.semitones_from_shorthand(interval_tuplet[0]) + 12*interval_tuplet[1]


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
    for a_note in [x for x in a_list]:
        for b_note in [y for y in b_list]:
            if (a_note.start, a_note.end) == (b_note.start, b_note.end):
                # remove the matched pair from their respective lists
                a_list.remove(a_note)
                b_list.remove(b_note)
                break

    return a_list, b_list

def find_changes(a_list, b_list):
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

def find_intervals(a_list, b_list):
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
    changes = find_changes(a_list, b_list)
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
        (int: a dir, int: b dir, (int: bar #, float: beat #))
    """
    changes = find_changes(a_list, b_list)
    a_dirs = find_directions(a_list, changes)
    b_dirs = find_directions(b_list, changes)
    return zip(a_dirs, b_dirs, changes)

def find_directions(a_list, changes):
    """
    Takes a NoteList object and a list of (bar, beat) tuples of the form
    returned by find_changes() above.

    Returns a list of integers representing the direction the melody moves
    in the NoteList at each time specified in the 'changes' list.

    Rests are considered to be no movement.
    The note after a rest is considered to move relative to the note before the rest.

     1 for up
     0 for no movement
    -1 for down
    """
    directions = []
    def get_dir(note):
        if note is None:
            direction = 0
        if note.is_rest:
            direction = 0
        elif note.prev_actual_note is None:
            direction = 0
        else:
            direction = cmp(int(note), int(note.prev_actual_note))
        return direction

    for time in changes:
        a_note = a_list.get(*time)
        directions.append(get_dir(a_note))

    return directions

def find_local_minima(a_list):
    """
    Takes a NoteList object.

    Returns a list of tuples of the form returned by find_changes().
    Each of these (int: bar #, float: beat #) tuples will represent the onset
    of a note that is a local minimum in the melody in a_list.
    """

    changes = find_changes(a_list, [])
    dirs = find_directions(a_list, changes)
    dirs = zip(dirs, changes)

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

    Returns a list of tuples of the form returned by find_changes().
    Each of these (int: bar #, float: beat #) tuples will represent the onset
    of a note that is a local maximum in the melody in a_list.
    """
    changes = find_changes(a_list, [])
    dirs = find_directions(a_list, changes)
    dirs = zip(dirs, changes)

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

def find_parallel_motion(a_list, b_list):
    """
    Takes two NoteList objects.

    Returns a list of lists.
    Each sub-list list will contain tuples representing intervals that appear at least
    twice.
    Each sub-list is of the form returned by find_intervals().
    """
    pairs = find_intervals(a_list, b_list)

    consecutives = []
    prev = ('0', None)
    x = None
    for i,cur in enumerate(pairs):
        # cur of form ((interval, octaves), (bar, beat))
        if cur[0] != prev[0] or (i == len(pairs) - 1):
            if i>0 and len(x) > 1:
                consecutives.append(x)
            x = []
        x.append(cur)
        prev = cur

    return consecutives

def find_invalid_parallel_intervals(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to find_parallel_motion() above.
    Sub-lists here will only contain illegal sets of parallel intervals,
    however.

    From the rules of first species counterpoint:
        Only 3rds and 6ths (and their octaves) may be repeated.
    """
    allowed_parallel_intervals = ['3', '6']
    consecutives = find_parallel_motion(a_list, b_list)

    invalid = []
    for c in consecutives:
        int_class = c[0][0][0]
        if len(c) > 2 and int_class not in allowed_parallel_intervals:
            invalid.append(c)
    return invalid

def find_invalid_consecutive_parallels(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to find_parallel_motion() above.
    Sub-lists here will only contain illegal sets of parallel intervals,
    however.

    From the rules of first species counterpoint:
        Any one interval may be repeated a maximum of three times consecutively.
    """
    max_consecutive_parallel = 3
    consecutives = find_parallel_motion(a_list, b_list)

    return [c for c in consecutives if len(c) > max_consecutive_parallel]

def find_coincident_maxima(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to find_local_maxima() above.
    Tuples returned here will only include note-onsets that are local maxima
    in both provided NoteList melodies, however.
    """
    a_maxima = find_local_maxima(a_list)
    b_maxima = find_local_maxima(b_list)

    return [x for x in a_maxima if x in b_maxima]

def find_voice_crossing(b_list, a_list, note_spacing=1):
    """
    Takes two NoteList objects and an integer.

    note_spacing parameter defines how many previous notes to consider when
    looking for voice crossings.
    0 means consider only the immediate note.
    1 means consider the previous note also.
    2 etc.

    Returns a list of notes that infringe on each other's space.
    a_list must represent the lower voice
    b_list must represent the higher voice

    Returns a list of tuples, each of the form:
        (NoteNode, NoteNode)
    """
    crossings = []

    def f_v_c(c_list, d_list, comparator):
        c_notes = [c for c in c_list]
        d_notes = [d_list.get_note_playing_at(c.bar, c.beat) for c in c_list]

        for x in range(0, note_spacing):
            if x > 0:
                d_notes = [d.prev for d in d_notes]
                d_notes.pop(0)
                c_notes.pop(0)

            for i in range(0, len(c_notes)):
                c = c_notes[i]
                d = d_notes[i]

                if c.is_rest or d.is_rest:
                    continue
                if comparator(int(c), int(d)):
                    if (d, c) not in crossings:
                        crossings.append((c, d))

    f_v_c(a_list, b_list, lambda a,b: a >= b)
    f_v_c(b_list, a_list, lambda a,b: a <= b)
    return crossings

def find_illegal_intervals(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to find_intervals() above.

    Returned tuples here, however, will only represent intervals that are
    not explicitly allowed by the allowed_intervals list.
    """
    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6']
    pairs = find_intervals(a_list, b_list)
    return [(i, t) for i, t in pairs if i[0] not in allowed_intervals]

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

def find_illegal_leaps(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to find_horizontal_intervals() above.

    Returned tuples here will only represent those intervals that are not
    explicitly allowed by the allowed_movements list below.
    """
    allowed_movements = ['1', 'b2', '2', 'b3', '3', '4', '5', 'b6', '6']
    intervals = find_horizontal_intervals(a_list)
    return [(i, a_list[x+1]) for x,i in enumerate(intervals) if i[0] not in allowed_movements]

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
        intervals.append((i, a, b))
    return intervals

def find_invalid_indirect_horizontal_intervals(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to find_indirect_horizontal_intervals() above.

    Intervals represented here, however, are only those that are not
    explicitly allowed by the allowed_intervals list below.
    """
    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6'] # same as allowed vertical intervals
    intervals = find_indirect_horizontal_intervals(a_list)
    return filter(lambda x: x[0] not in allowed_intervals, intervals)

def find_missed_leap_turnarounds(a_list):
    """
    Takes a single NoteList object.

    Return format is identical to find_changes() above.

    The only tuples returned here, however, are those that represent the
    onset of a note which has been approached by a leap greater than
    half an octave, and which has not been left by step in the opposite
    direction.
    """
    # immediately after a leap of (P5, m6, M6, P8), must move by step (m2, M2)
    # in opposite direction
    largest_leap_without_turnaround = 6 # semitones

    # get horizontal intervals as semitones
    h_i_semitones = [get_semitones(x) for x in find_horizontal_intervals(a_list)]

    # get list of directions for each interval
    changes = find_changes(a_list, [])
    dirs = find_directions(a_list, changes)
    dirs = zip(dirs, changes)

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
    return [changes[i+1] for i in invalid_leaps]

def find_direct_motion(a_list, b_list):
    """
    Takes two NoteList objects.

    Return format is identical to find_intervals() above.

    Intervals returned here, however, only represent intervals explicitly
    defined in the invalid_direct_intervals list below, which have been
    approached through similar motion (ie. both voices moving in the same
    direction)
    """
    invalid_direct_intervals = ['5', '1']

    intervals = find_intervals(a_list, b_list)
    directions = combined_directions(a_list, b_list)

    invalid_directs = []
    for i in range(0, len(intervals)):
        (interval, octaves), time = intervals[i]
        a_dir, b_dir, time = directions[i]

        if interval in invalid_direct_intervals and a_dir != 0 and a_dir == b_dir:
            invalid_directs.append(intervals[i])

    return invalid_directs

def starts_with_tonic(a_list):
    """
    Takes a single NoteList object.

    Returns True if the first non-rest note in the melody is the tonic
    of the key defined by the first bar in the melody.

    Returns False otherwise.
    """
    key = a_list.track.bars[0].key.name
    note = a_list.notes[0].name
    return note == key

def starts_with_tonic_or_fifth(a_list):
    """
    Takes a single NoteList object.

    Returns True if the first non-rest note in the melody is the tonic or the fifth
    of the key defined by the first bar in the melody.

    Returns False otherwise.
    """
    key = a_list.track.bars[0].key
    note = a_list.notes[0].name
    possible_notes = [key.name, Note(key).transpose('5', True).name]
    return note in possible_notes

def ends_with_lt_tonic(a_list):
    """
    Takes a single NoteList object.

    Returns True if the last two notes in the melody are the leading tone and tonic
    of the key defined by the first bar in the melody.

    Returns False otherwise.
    """
    key = a_list.track.bars[-1].key
    a, b = a_list.notes[-2:]
    lt, tonic = Note(key).transpose('7', True).name, key.name
    return (a.name, b.name) == (lt, tonic) and int(b) - int(a) == 1

def find_accidentals(a_list):
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

def first_species(composition):
    """
    Takes a mingus.containers.Composition object.

    Returns a dict of possible errors according to the rules of
    First Species counterpoint.
    """
    n, high_voice, low_voice, inner_voices, voice_combos = \
        get_and_split_note_lists(composition)

    # find errors in specific voices
    high_voice_beginning_error = not starts_with_tonic_or_fifth(high_voice)
    high_voice_ending_error = not ends_with_lt_tonic(high_voice)
    low_voice_beginning_error = not starts_with_tonic(low_voice)

    # find errors in each melody
    horizontal_errors = {}
    indirect_horizontal_errors = {}
    turnaround_errors = {}
    accidental_errors = {}
    for x in n:
        horizontal_errors[x] = find_illegal_leaps(n[x])
        indirect_horizontal_errors[x] = find_invalid_indirect_horizontal_intervals(n[x])
        turnaround_errors[x] = find_missed_leap_turnarounds(n[x])
        accidental_errors[x] = find_accidentals(n[x])

    # find errors between pairs of voices.
    alignment_errors = {}
    parallel_errors = {}
    consecutive_parallel_errors = {}
    high_point_errors = {}
    voice_crossing_errors = {}
    vertical_interval_errors = {}
    direct_motion_errors = {}
    for x, y in voice_combos:
        alignment_errors[(x, y)] = all_notes_line_up(n[x], n[y])
        parallel_errors[(x, y)] = find_invalid_parallel_intervals(n[x], n[y])
        consecutive_parallel_errors[(x, y)] = find_invalid_consecutive_parallels(n[x], n[y])
        high_point_errors[(x, y)] = find_coincident_maxima(n[x], n[y])
        voice_crossing_errors[(x, y)] = find_voice_crossing(n[x], n[y])
        vertical_interval_errors[(x, y)] = find_illegal_intervals(n[x], n[y])
        direct_motion_errors[(x, y)] = find_direct_motion(n[x], n[y])

    return dict(
        # find errors in specific voices
        high_voice_beginning_error = high_voice_beginning_error,
        high_voice_ending_error = high_voice_ending_error,
        low_voice_beginning_error = low_voice_beginning_error,
        # intra-voice errors
        horizontal_errors = horizontal_errors,
        indirect_horizontal_errors = indirect_horizontal_errors,
        turnaround_errors = turnaround_errors,
        accidental_errors = accidental_errors,
        # inter-voice errors
        aligmnent_errors = alignment_errors,
        parallel_errors = parallel_errors,
        consecutive_parallel_errors = consecutive_parallel_errors,
        high_point_errors = high_point_errors,
        voice_crossing_errors = voice_crossing_errors,
        vertical_interval_errors = vertical_interval_errors,
        direct_motion_errors = direct_motion_errors,
    )

def second_species(composition):
    return {}

def third_species(composition):
    return {}

def fourth_species(composition):
    return {}

