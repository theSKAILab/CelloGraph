import difflib

def getMatches(gro, alt):
    seq = difflib.SequenceMatcher(a=gro, b=alt)

    matches = seq.get_matching_blocks()

    return matches