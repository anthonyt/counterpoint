# -*- coding: utf-8 -*-

from mingus.core import intervals as mintervals
from mingus.containers import Note
from rules import *
from views import *

def first_species(composition):
    """
    Takes a mingus.containers.Composition object.

    Returns a dict of possible errors according to the rules of
    First Species counterpoint.
    """
    n, high_voice, low_voice, inner_voices, voice_combos = \
        get_and_split_note_lists(composition)

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
        horizontal_errors[x] = illegal_horizontal_intervals(n[x])
        indirect_horizontal_errors[x] = illegal_indirect_horizontal_intervals(n[x])
        turnaround_errors[x] = missed_leap_turnarounds(n[x])
        accidental_errors[x] = accidentals(n[x])

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
        parallel_errors[(x, y)] = illegal_parallel_intervals(n[x], n[y])
        consecutive_parallel_errors[(x, y)] = illegal_consecutive_parallels(n[x], n[y])
        high_point_errors[(x, y)] = coincident_maxima(n[x], n[y])
        voice_crossing_errors[(x, y)] = voice_crossing(n[x], n[y])
        vertical_interval_errors[(x, y)] = illegal_vertical_intervals(n[x], n[y])
        direct_motion_errors[(x, y)] = illegal_direct_motion(n[x], n[y])

    return dict(
        # find errors in specific voices
        high_voice_beginning_error = {high_voice.track.name: high_voice_beginning_error},
        high_voice_ending_error = {high_voice.track.name: high_voice_ending_error},
        low_voice_beginning_error = {low_voice.track.name: low_voice_beginning_error},
        # intra-voice errors
        horizontal_errors = horizontal_errors,
        indirect_horizontal_errors = indirect_horizontal_errors,
        turnaround_errors = turnaround_errors,
        accidental_errors = accidental_errors,
        # inter-voice errors
        alignment_errors = alignment_errors,
        parallel_errors = parallel_errors,
        consecutive_parallel_errors = consecutive_parallel_errors,
        high_point_errors = high_point_errors,
        voice_crossing_errors = voice_crossing_errors,
        vertical_interval_errors = vertical_interval_errors,
        direct_motion_errors = direct_motion_errors,
    )

def second_species(composition):
    """
    Takes a mingus.containers.Composition object.

    Returns a dict of possible errors according to the rules of
    First Species counterpoint.

    NOTE: this huge function is a bit of a hack, and should really be factored
          into smaller bits
    """
    n, high_voice, low_voice, inner_voices, voice_combos = \
        get_and_split_note_lists(composition)

    # find the cantus firmus. In 2nd species, this is the voice that is
    # all whole notes.
    cantus_firmus = None
    for voice in n:
        if all([note.duration == 1 for note in n[voice]]):
            cantus_firmus = voice
            break

    # if we can't find the C.F. return right away.
    if cantus_firmus == None:
        return dict(
            cantus_firmus = None
        )

    other_voices = [voice for voice in n if voice != cantus_firmus]

    for voice in other_voices:
        # all other voices must be half notes (and not rests either!).
        # except:
        #   last note must be whole note
        #   penultimate note may be whole note
        #   first note may be half rest.
        invalid_rests = [note for note in n[voice][1:] if note.is_rest]
        invalid_durations = [note for note in n[voice][:-2] if note.duration != 0.5]
        if n[voice][-1].duration != 1:
            invalid_durations.append(n[voice][-1])
        if n[voice][-2].duration not in [1, 0.5]:
            invalid_durations.append(n[voice][-2])

    # find errors in specific voices
    high_voice_beginning_error = starts_with_tonic_or_fifth(high_voice)
    high_voice_ending_error = ends_with_lt_tonic(high_voice)
    low_voice_beginning_error = starts_with_tonic(low_voice)

    # find errors in each melody
    horizontal_errors = {}
    weak_horizontal_errors  = {}
    turnaround_errors = {}
    accidental_errors = {}
    repeated_notes = {}
    strong_beat_horizontals = {}
    for x in n:
        horizontal_errors[x] = illegal_horizontal_intervals(n[x])
        turnaround_errors[x] = missed_leap_turnarounds(n[x])
        accidental_errors[x] = accidentals(n[x])

        # no voice is allowed to repeat notes
        repeated = []
        note = n[x].get_first_actual_note()
        while note is not None:
            next = note.next_actual_note
            if next is not None and get_interval(note, next) == ('1', 0):
                repeated.append((note, next))
            note = next
        repeated_notes[x] = repeated

        # leaps greater than a 5th may only go from strong to weak beats
        intervals = horizontal_intervals(n[x])
        weak_horizontal_errors[x] = [
            (interval, n[x][i+1])
            for i,interval in enumerate(intervals)
            if get_semitones(interval) > 7 # leap is greater than 5th
            and n[x][i+1].beat == 0 # note falls on a strong beat
        ]

        # find invalid intervals between consecutive downbeats.
        strong_beat_horizontals[x] = \
            illegal_strong_beat_horizontal_intervals(n[x])

    # find errors between pairs of voices.
    parallel_errors = {}
    parallel_downbeat_errors = {}
    consecutive_parallel_errors = {}
    high_point_errors = {}
    voice_crossing_errors = {}
    vertical_interval_errors = {}
    direct_motion_errors = {}
    for x, y in voice_combos:
        parallel_errors[(x, y)] = illegal_parallel_intervals(n[x], n[y])
        # We also have to consider consecutive downbeats, now, when looking for
        # parallel intervals.
        downbeat_filter = lambda x: x[1][1] == 0
        parallel_downbeat_errors[(x, y)] = \
            parallel_motion(n[x], n[y], filter_fn=downbeat_filter)
        consecutive_parallel_errors[(x, y)] = illegal_consecutive_parallels(n[x], n[y])
        high_point_errors[(x, y)] = coincident_maxima(n[x], n[y])

        # second species has different rules for vertical intervals
        dissonances = illegal_vertical_intervals(n[x], n[y])
        legal_dissonance = legal_dissonances(n[x], n[y])
        vertical_interval_errors[(x, y)] = [
            d for d in dissonances
            if d not in legal_dissonance
        ]

        direct_motion_errors[(x, y)] = illegal_direct_motion(n[x], n[y])

        # voice crossing in the form of unison on weak beat is okay now.
        voice_crossings = voice_crossing(n[x], n[y])
        weak_beat_filter = lambda x: x.beat == 0.5
        legal_crossings = [
            v
            for v in voice_crossing(
                n[x], n[y],
                note_spacing=1,
                note_filter_fn=weak_beat_filter
            ) # find all weak beat voice crossings
            if get_interval(v[0], v[1]) == ('1', 0) # filter to perfect unisons
        ]
        voice_crossing_errors[(x, y)] = [v for v in voice_crossings if v not in legal_crossings]

    return dict(
        cantus_firmus = cantus_firmus,
        # find errors in specific voices
        high_voice_beginning_error = {high_voice.track.name: high_voice_beginning_error},
        high_voice_ending_error = {high_voice.track.name: high_voice_ending_error},
        low_voice_beginning_error = {low_voice.track.name: low_voice_beginning_error},
        # intra-voice errors
        horizontal_errors = horizontal_errors,
        turnaround_errors = turnaround_errors,
        weak_horizontal_errors = weak_horizontal_errors,
        accidental_errors = accidental_errors,
        strong_beat_horizontals = strong_beat_horizontals,
        # inter-voice errors
        parallel_errors = parallel_errors,
        consecutive_parallel_errors = consecutive_parallel_errors,
        high_point_errors = high_point_errors,
        voice_crossing_errors = voice_crossing_errors,
        vertical_interval_errors = vertical_interval_errors,
        direct_motion_errors = direct_motion_errors,
    )

def third_species(composition):
    return {}

def fourth_species(composition):
    return {}

