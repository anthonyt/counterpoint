# -*- coding: utf-8 -*-

from mingus.core import intervals as mintervals
from mingus.core.diatonic import get_notes
from structures import create_note_lists


def get_interval(note_a, note_b):
    name = mintervals.determine(note_a, note_b, True)
    octave = abs(int(note_a) - int(note_b))/12
    return (name, octave)

def get_semitones(interval_tuplet):
    return mintervals.semitones_from_shorthand(interval_tuplet[0]) + 12*interval_tuplet[1]


def all_notes_line_up(cf_list, ctp_list):
    """Counterpoint moves with same rhythm as cantus-firmus (note for note)

    We check this by ensuring that no note in either track starts without
    A corresponding note, with equal duration, in the other track.

    Returns a tuple (num errors, unmatched notes in CF, unmatched notes in CTP)

    Note: this function's worst-case run-time could be made much more efficient
    """
    a_list = [x for x in cf_list]  # cast NoteList to list
    b_list = [x for x in ctp_list] # cast NoteList to list

    # remove matched notes
    for i,a_note in enumerate(a_list):
        for j,b_note in enumerate(b_list):
            if (a_note.start, a_note.end) == (b_note.start, b_note.end):
                # remove the matched pair from their respective lists
                a_list.remove(a_note)
                b_list.remove(b_note)
                break
    errors = len(a_list) + len(b_list) # count up the unmatched notes

    return errors, a_list, b_list

def find_changes(a_list, b_list):
    # find all places where a note changes, in order.
    # return as a list of (bar_no, beat_no) pairs
    changes = []
    for l in [a_list, b_list]:
        for note in l:
            if note.start not in changes:
                changes.append(note.start)
    return changes

def find_intervals(a_list, b_list):
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
    changes = find_changes(a_list, b_list)
    a_dirs = find_directions(a_list, changes)
    b_dirs = find_directions(b_list, changes)
    return zip(a_dirs, b_dirs, changes)

def find_directions(a_list, changes):
    # find the direction (up, down, straight) that a line moves in
    # each time a note changes
    directions = []
    def get_dir(note):
        if note is None:
            direction = 0
        elif note.prev is None:
            direction = 0
        else:
            direction = cmp(int(note), int(note.prev))
        return direction

    for time in changes:
        a_note = a_list.get(*time)
        directions.append(get_dir(a_note))

    return directions

def find_local_minima(a_list):
    changes = find_changes(a_list, [])
    dirs = find_directions(a_list, changes)
    dirs = zip(dirs, changes)

    minima = []

    # started on a low note?
    for cur, time in dirs:
        if cur == 0:
            continue
        elif cur == 1:
            minima.append(changes[0])
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
    changes = find_changes(a_list, [])
    dirs = find_directions(a_list, changes)
    dirs = zip(dirs, changes)

    maxima = []

    # started on a high note?
    for cur, time in dirs:
        if cur == 0:
            continue
        elif cur == -1:
            maxima.append(changes[0])
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
    # if the pairs of intervals are not the same
    #   take them out of the list
    # if they are the same
    #   if they're m3, m6, or octaves thereof
    #     m
    #   if yes
    # make sure they're 3rds, 6ths, or octaves thereof.
    pairs = find_intervals(a_list, b_list)

    consecutives = []
    prev = ('0', None)
    x = None
    for i,cur in enumerate(pairs):
        # cur of form ((interval, octaves), (bar, beat))
        if cur[0] != prev[0]:
            if i>0 and len(x) > 1:
                consecutives.append(x)
            x = []
        x.append(cur)
        prev = cur

    return consecutives

def find_invalid_parallel_intervals(a_list, b_list):
    allowed_parallel_intervals = ['3', '6']
    consecutives = find_parallel_motion(a_list, b_list)

    invalid = []
    for c in consecutives:
        int_class = c[0][0][0]
        if len(c) >= 2 and int_class not in allowed_parallel_intervals:
            invalid.append(c)
    return invalid

def find_invalid_consecutive_parallels(a_list, b_list):
    max_consecutive_parallel = 3
    consecutives = find_parallel_motion(a_list, b_list)

    return [c for c in consecutives if len(c) > max_consecutive_parallel]

def find_coincident_maxima(a_list, b_list):
    a_maxima = find_local_maxima(a_list)
    b_maxima = find_local_maxima(b_list)

    return [x for x in a_maxima if x in b_maxima]

def find_voice_crossing(a_list, b_list):
    """NB: a_list must be lower voice; b_list must be higher voice"""
    # 0 -> no crossing into current note's space
    # 1 -> no crossing into previous note's space
    note_spacing = 1
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
                if comparator(int(c), int(d)):
                    if (d, c) not in crossings:
                        crossings.append((c, d))

    f_v_c(a_list, b_list, lambda a,b: a >= b)
    f_v_c(b_list, a_list, lambda a,b: a <= b)
    return crossings

def find_illegal_intervals(a_list, b_list):
    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6']
    pairs = find_intervals(a_list, b_list)
    return [(i, t) for i, t in pairs if i[0] not in allowed_intervals]

def find_horizontal_intervals(a_list):
    return [get_interval(a, a.next) for a in a_list if a.next is not None]

def find_illegal_leaps(a_list):
    allowed_movements = ['1', 'b2', '2', 'b3', '3', '4', '5', 'b6', '6']
    intervals = find_horizontal_intervals(a_list)
    return [(i, a_list[x+1]) for x,i in enumerate(intervals) if i[0] not in allowed_movements]

def find_indirect_horizontal_intervals(a_list):
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
        i = mintervals.determine(x, y, True)
        intervals.append((i, a, b))
    return intervals

def find_invalid_indirect_horizontal_intervals(a_list):
    allowed_intervals = ['1', 'b3', '3', '4', '5', 'b6', '6'] # same as allowed vertical intervals
    intervals = find_indirect_horizontal_intervals(a_list)
    return filter(lambda x: x[0] not in allowed_intervals, intervals)

def find_missed_leap_turnarounds(a_list):
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
    key = a_list.track.bars[0].key.name
    note = a_list.notes[0].name
    return note == key

def starts_with_tonic_or_fifth(a_list):
    key = a_list.track.bars[0].key
    note = a_list.notes[0].name
    possible_notes = [key.name, mintervals.perfect_fifth(key.name)]
    return note in possible_notes

def ends_with_lt_tonic(a_list):
    key = a_list.track.bars[-1].key
    a, b = a_list.notes[-2:]
    lt, tonic = mintervals.major_seventh(key.name), key
    return (a, b) == (lt, tonic)

def find_accidentals(a_list):
    key = a_list.track.bars[0].key
    notes_in_key = get_notes(key.name)
    return [note for note in a_list if note.name not in notes_in_key]


def first_species(composition):
    # assumes that composition will have Soprano, Alto, Tenor, Bass tracks
    # also assumes that at least two of these tracks have content
    # also assumes that Soprano track is higher than Alto track, etc, etc.

    # create a dict of all tracks with notes in them
    lists = create_note_lists(composition)
    n = {}
    for voice in lists:
        if len(lists[voice]):
            n[voice] = lists[voice]


    # find the high voice
    for voice in ['Soprano', 'Alto', 'Tenor', 'Bass']:
        if voice in n:
            high_voice = n[voice]
            break

    # find the low voice
    for voice in ['Bass', 'Tenor', 'Alto', 'Soprano']:
        if voice in n:
            low_voice = n[voice]
            break

    # find the inner voices
    inner_voices = []
    for voice in ['Tenor', 'Alto']:
        if voice in n and n[voice] not in [high_voice, low_voice]:
            inner_voices.append(n[voice])

    # find all possible combinations of voices
    voice_combos = []
    for x in n:
        for y in n:
            if x != y and (x, y) not in voice_combos and (y, x) not in voice_combos:
                voice_combos.append((x, y))

    # find errors in specific voices
    high_voice_beginning_error = starts_with_tonic_or_fifth(high_voice)
    high_voice_ending_error = ends_with_lt_tonic(high_voice)
    low_voice_beginning_error = starts_with_tonic(low_voice)

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
        parallel_errors[(x, y)] = find_invalid_consecutive_parallels(n[x], n[y])
        high_point_errors[(x, y)] = find_coincident_maxima(n[x], n[y])
        voice_crossing_errors[(x, y)] = find_voice_crossing(n[x], n[y])
        vertical_interval_errors[(x, y)] = find_illegal_intervals(n[x], n[y])
        direct_motion_errors[(x, y)] = find_illegal_intervals(n[x], n[y])

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
