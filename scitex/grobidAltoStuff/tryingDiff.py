import difflib

def getMatches(gro, alt):
    seq = difflib.SequenceMatcher(b=gro, a=alt)

    matches = seq.get_matching_blocks()

    return matches