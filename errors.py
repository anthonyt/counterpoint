# -*- coding: utf-8 -*-

# The rules of first and second species counterpoint, described:
# Each key in the following dictionary corresponds to a key in the result
# dict from either species.first_species() or species.second_species()
written_rules = dict(
    accidental_errors = "This note is not within the key.",
    alignment_errors = "First Species counterpoint requires 1:1 correspondence between notes in the melody and the cantus firmus.",
    cantus_firmus = "I have detected that this voice is the cantus firmus.",
    consecutive_parallel_errors = "No parallel interval may repeat more than 3 times.",
    direct_motion_errors = "Direct (similar) motion to a P5, P1, or their octaves, is forbidden.",
    high_point_errors = "High points of melodic curves should not coincide.",
    high_voice_beginning_error = "Upper voice must begin with the tonic.",
    high_voice_ending_error = "Upper voice must end with Leading Tone, Tonic",
    horizontal_errors = "The only permissable horizontal motions are m2, M2, m3, M3, P4, P5, m6, M6 and their octaves.",
    indirect_horizontal_errors = "Consecutive high/low points of a melody must not outline dissonant intervals.",
    low_voice_beginning_error = "Lower voice must begin with the tonic.",
    parallel_errors = "The only acceptable parallel intervals are m3, M3, m6, M6 and their octaves.",
    strong_beat_horizontals = "Adjacent strong beats must not outline dissonant intervals.",
    turnaround_errors = "Leaps equal to or greater than a P5 must be left by step in the opposite direction.",
    vertical_interval_errors = "Vertical intervals must not be dissonant. The permissible vertical intervals are P1, m3, M3, P4, P5, m6, M6, and their octaves.",
    voice_crossing_errors = "Voices must not cross into the space of other voices within one note.",
    weak_horizontal_errors = "Leaps greater than a 5th may only go from strong to weak beats.",
)

jazz_to_classical = {
    # TODO: update this dict to be a function that can handle wierd combinations of accidentals.
    '1': 'P1',
    '#1': 'aug1',
    'b2': 'm2',
    '2': 'M2',
    '#2': 'aug2',
    'b3': 'm3',
    '3': 'M3',
    '#3': 'aug3',
    'b4': 'dim4',
    '4': 'P4',
    '#4': 'aug4',
    'b5': 'dim5',
    '5': 'P5',
    '#5': 'aug5',
    'b6': 'm6',
    '6': 'M6',
    '#6': 'aug6',
    'b7': 'm7',
    '7': '7',
    '#7': 'aug7',
    ' ': 'no harmony'
}

def get_error_text(error):
    """
    Returns a string describing the passed in error in standardized format.

    Standard error format is:
        ( (list of events), message, error_name ) OR
        ( (list of events), error_name )

    Where message and error_name are both strings.

    And where "list of events" is a tuple of the form:
        ( voices, name, bar_no, beat_no )

    Where voices is either a string (the name of a voice)
    or a tuple of two strings (the names of two voices)

    And where name is a string that either represents note name (if voices
    is a string) or an interval (if voices is a tuple)

    And where bar_no is an int. representing the 0 offset measure number of
    the event.

    And where beat_no is a float. representing the 0 offset fraction
    (position of event/beats in whole note)
    """
    if len(error) == 3:
        notes, message, errid = error
    elif len(error) == 2:
        notes, errid = error
        message = ''

    note_strings = []
    for note in notes:
        voice, name, bar, beat = note
        if name in jazz_to_classical:
            name = jazz_to_classical[name]
        if type(voice) is tuple:
            voice = 'between %s and %s' % (voice[0], voice[1])
        else:
            voice = 'in %s' % voice

        bar = bar + 1
        beat = beat * 4 + 1
        position = 'mm. %d beat %.2f' % (bar, beat)
        note_strings.append("%s at %s %s" % (name, position, voice))

    if len(note_strings) > 1:
        err = "Error: between %s" % ', '.join(note_strings)
    else:
        err = "Error: %s" % ', '.join(note_strings)
    if message:
        err += ": " + message

    return err

# The following methods are a bit of a hack.
# We need to get the errors into a common format somehow, though.
# A more ideal solution would be to refactor the rules to standardize the output.

def accidental_errors(x):
#    {u'Alto': [], u'Soprano': [<NoteNode 'Bb-4', 2, 0.00, 2>, <NoteNode 'Bb-4', 2, 0.50, 2>]}
    errors = []
    for voice in x:
        for note in x[voice]:
            error = (((voice, note.name, note.bar, note.beat),), 'accidental_errors')
            errors.append(error)
    return errors

def alignment_errors(x):
    errors = []
    for voices in x:
        voice_a, voice_b = voices
        combos = ((voice_a, voice_b, x[voices][0]), (voice_b, voice_a, x[voices][1]))
        for voice_c, voice_d, notes in combos:
            for note in notes:
                error = (((voice_c, note.name, note.bar, note.beat),), 'Has no matching note in the %s' % voice_d, 'alignment_errors')
                errors.append(error)
    return errors

def cantus_firmus(x):
    return [(((x, None, None, None),), 'cantus_firmus')]

def consecutive_parallel_errors(x):
    # {('Soprano', 'Alto'): [[(('b3', 0), (1, 0.0)), (('b3', 0), (1, 0.5)), (('b3', 0), (2, 0.0)), (('b3', 0), (2, 0.5))]]}
    errors = []
    for voices in x:
        for run in x[voices]:
            notes = []
            for (i, o), (bar, beat) in run:
                note = (voices, i, bar, beat)
                notes.append(note)
            notes = tuple(notes)
            error = (notes, 'Interval %s is repeated %d times.' % (i, len(notes)), 'consecutive_parallel_errors')
            errors.append(error)
    return errors

def direct_motion_errors(x):
    # {('Soprano', 'Alto'): [(('5', 0), (3, 0.0))]}
    errors = []
    for voices in x:
        for (i, o), (bar, beat) in x[voices]:
            notes = ((voices, i, bar, beat),)
            error = (notes, 'direct_motion_errors')
            errors.append(error)
    return errors

def high_point_errors(x):
    # {('Soprano', 'Alto'): [(3, 0.0), (6, 0.0)]}
    errors = []
    for voices in x:
        notes = []
        for (bar, beat) in x[voices]:
            note = (voices, 'melodic high point', bar, beat)
            error = ((note, ), 'high_point_errors')
            errors.append(error)
    return errors

def high_voice_beginning_error(x):
    # {'Soprano': [(1, 0.00)]}
    errors = []
    for voice in x:
        for note in x[voice]:
            error = (((voice, note.name, note.bar, note.beat),), 'high_voice_beginning_error')
            errors.append(error)
    return errors

def high_voice_ending_error(x):
    # {'Soprano': [(8, 0.50), (9, 1.00)]}
    errors = []
    for voice in x:
        notes = []
        for note in x[voice]:
            note = (voice, note.name, note.bar, note.beat)
            notes.append(note)
        if notes:
            notes = tuple(notes)
            error = (notes, 'high_voice_ending_error')
            errors.append(error)
    return errors

def horizontal_errors(x):
    # {u'Alto': [], u'Soprano': [(('#4', 0), <NoteNode 'Bb-4', 2, 0.50, 2>)]}
    errors = []
    for voice in x:
        for (i, o), note in x[voice]:
            note = (voice, note.name, note.bar, note.beat)
            error = ((note, ), 'Approached by %s leap' % jazz_to_classical[i], 'horizontal_errors')
            errors.append(error)
    return errors

def indirect_horizontal_errors(x):
    # {u'Alto': [], u'Soprano': [('b5', <NoteNode 'F-5', 6, 0.00, 2>, <NoteNode 'B-4', 8, 0.00, 2>), ('b5', <NoteNode 'F-5', 6, 0.00, 2>, <NoteNode 'B-4', 4, 0.50, 2>)]}
    errors = []
    for voice in x:
        for i, note_a, note_b in x[voice]:
            note_a = (voice, note_a.name, note_a.bar, note_a.beat)
            note_b = (voice, note_b.name, note_b.bar, note_b.beat)
            error = ((note_a, note_b), 'outlines a %s' % jazz_to_classical[i], 'indirect_horizontal_errors')
            errors.append(error)
    return errors

def low_voice_beginning_error(x):
    # {'Bass': [(1, 0.00)]}
    errors = []
    for voice in x:
        notes = []
        for note in x[voice]:
            note = (voice, note.name, note.bar, note.beat)
            notes.append(note)
        if notes:
            notes = tuple(notes)
            error = (notes, 'low_voice_beginning_error')
            errors.append(error)
    return errors

def parallel_errors(x):
    # {('Soprano', 'Alto'): [[(('5', 0), (1, 0.0)), (('5', 0), (1, 0.5))], [(('1', 1), (2, 0.0)), (('1', 1), (2, 0.5))]}
    errors = []
    for voices in x:
        for run in x[voices]:
            notes = []
            for (i, o), (bar, beat) in run:
                note = (voices, i, bar, beat)
                notes.append(note)
            notes = tuple(notes)
            error = (notes, 'Interval %s is repeated %d times.' % (i, len(notes)), 'parallel_errors')
            errors.append(error)
    return errors

def strong_beat_horizontals(x):
    # {u'Alto': [], u'Soprano': [('b5', <NoteNode 'F-5', 6, 0.00, 2>, <NoteNode 'B-4', 7, 0.00, 2>), ('b5', <NoteNode 'F-5', 7, 0.00, 2>, <NoteNode 'B-4', 8, 0.00, 2>)]}
    errors = []
    for voice in x:
        for i, note_a, note_b in x[voice]:
            note_a = (voice, note_a.name, note_a.bar, note_a.beat)
            note_b = (voice, note_b.name, note_b.bar, note_b.beat)
            error = ((note_a, note_b), 'outlines a %s' % jazz_to_classical[i], 'strong_beat_horizontals')
            errors.append(error)
    return errors

def turnaround_errors(x):
    #{u'Alto': [(6, 0.0)], u'Soprano': []}
    errors = []
    for voice in x:
        for bar, beat in x[voice]:
            note = (voice, 'leap', bar, beat)
            error = ((note, ), 'turnaround_errors')
            errors.append(error)
    return errors

def vertical_interval_errors(x):
    # {('Soprano', 'Alto'): [((' ', 0), (0, 0.0)), (('#4', 0), (3, 0.5))]}
    errors = []
    for voices in x:
        for (i, o), (bar, beat) in x[voices]:
            notes = ((voices, i, bar, beat),)
            error = (notes, 'vertical_interval_errors')
            errors.append(error)
    return errors

def voice_crossing_errors(x):
    #{('Soprano', 'Alto'): [(<NoteNode 'G-4', 2, 0.00, 1>, <NoteNode 'G-4', 1, 0.50, 2>), (<NoteNode 'G-4', 9, 0.50, 2>, <NoteNode 'G-4', 8, 0.00, 1>)]}
    errors = []
    for voices in x:
        for note_tuple in x[voices]:
            notes = (
                (voices[0], note_tuple[0].name, note_tuple[0].bar, note_tuple[0].beat),
                (voices[1], note_tuple[1].name, note_tuple[1].bar, note_tuple[1].beat)
            )
            error = (notes, 'voice_crossing_errors')
            errors.append(error)
    return errors

def weak_horizontal_errors(x):
    # {u'Alto': [(('6', 0), <NoteNode 'A-4', 6, 0.00, 1>)], u'Soprano': [(('b6', 0), <NoteNode 'D-4', 2, 0.00, 2>), (('1', 1), <NoteNode 'E-5', 3, 0.00, 2>)]}
    errors = []
    for voice in x:
        for (i, o), note in x[voice]:
            note = (voice, note.name, note.bar, note.beat)
            error = ((note, ), '%s leap to strong beat' % jazz_to_classical[i], 'weak_horizontal_errors')
            errors.append(error)
    return errors

written_errors = dict(
    accidental_errors = accidental_errors,
    alignment_errors = alignment_errors,
#    cantus_firmus = cantus_firmus,
    consecutive_parallel_errors = consecutive_parallel_errors,
    direct_motion_errors = direct_motion_errors,
    high_point_errors = high_point_errors,
    high_voice_beginning_error = high_voice_beginning_error,
    high_voice_ending_error = high_voice_ending_error,
    horizontal_errors = horizontal_errors,
    indirect_horizontal_errors = indirect_horizontal_errors,
    low_voice_beginning_error = low_voice_beginning_error,
    parallel_errors = parallel_errors,
    strong_beat_horizontals = strong_beat_horizontals,
    turnaround_errors = turnaround_errors,
    vertical_interval_errors = vertical_interval_errors,
    voice_crossing_errors = voice_crossing_errors,
    weak_horizontal_errors = weak_horizontal_errors,
)

def standardize_errors(error_dict):
    errors = []
    for key in error_dict:
        if key in written_errors and callable(written_errors[key]):
            extra_errors = written_errors[key](error_dict[key])
            if extra_errors:
                errors.extend(extra_errors)
    return errors

