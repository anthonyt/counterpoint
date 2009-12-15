# -*- coding: utf-8 -*-

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
    for a_note in [x for x in a_list]:
        for b_note in [x for x in b_list]:
            if (a_note.start, a_note.end) == (b_note.start, b_note.end):
                # remove the matched pair from their respective lists
                a_list.remove(a_note)
                b_list.remove(b_note)
                break
    errors = len(a_list) + len(b_list) # count up the unmatched notes

    return errors, a_list, b_list

