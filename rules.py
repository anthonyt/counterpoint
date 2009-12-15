# -*- coding: utf-8 -*-

def all_notes_line_up(cf_list, ctp_list):
    """Counterpoint moves with same rhythm as cantus-firmus (note for note)

    We check this by ensuring that no note in either track starts without
    Ga corresponding note, with equal duration, in the other track.

    Returns a tuple (num errors, unmatched notes in CF, unmatched notes in CTP)
    """
    def has_matching_note(note, list, offset):
        for x in list[offset:]:
            if x.bar > note.bar:
                return False, offset
            offset += 1
            if x.beat == note.beat \
            and x.duration == note.duration:
                return True, offset
        return False, offset

    def a_n_l_u(a_list, b_list):
        unmatched = []
        i = 0
        for a_note in a_list:
            has_match, i = has_matching_note(a_note, b_list, i)
            if not has_match:
                errors += 1
                unmatched.append(a_note)
        return unmatched

    unmatched_cf = a_n_l_u(cf_list, ctp_list)
    unmatched_ctp = a_n_l_u(ctp_list, cf_list)
    errors = len(unmatched_cf) + len(unmatched_ctp)

    return errors, unmatched_cf, unmatched_ctp
