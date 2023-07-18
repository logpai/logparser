# =========================================================================
# This software is a free software. Thus, it is licensed under GNU General Public License.
# Python implementation to Smith-Waterman Algorithm for Homework 1 of Bioinformatics class.
# Forrest Bao, Sept. 26 <http://fsbao.net> <forrest.bao aT gmail.com>

# zeros() was origianlly from NumPy.
# This version is implemented by alevchuk 2011-04-10
# =========================================================================


def zeros(shape):
    retval = []
    for x in range(shape[0]):
        retval.append([])
        for y in range(shape[1]):
            retval[-1].append(0)
    return retval

match_award      = 10
mismatch_penalty = 1
gap_penalty      = 0 # both for opening and extanding

def match_score(alpha, beta):
    if alpha == beta:
        return match_award
    elif alpha == '-' or beta == '-':
        return gap_penalty
    else:
        return mismatch_penalty

def finalize(align1, align2):
    align1.reverse()    #reverse sequence 1
    align2.reverse()    #reverse sequence 2

    i,j = 0,0
    
    #calcuate identity, score and aligned sequeces
    symbol = ''
    found = 0
    score = 0
    identity = 0
    for i in range(0,len(align1)):
        # if two AAs are the same, then output the letter
        if align1[i] == align2[i]:                
            symbol = symbol + align1[i]
            identity = identity + 1
            score += match_score(align1[i], align2[i])
    
        # if they are not identical and none of them is gap
        elif align1[i] != align2[i] and align1[i] != '-' and align2[i] != '-': 
            score += match_score(align1[i], align2[i])
            symbol += ' '
            found = 0
    
        #if one of them is a gap, output a space
        elif align1[i] == '-' or align2[i] == '-':          
            symbol += ' '
            score += gap_penalty
    
    identity = float(identity) / len(align1) * 100
    
    return align1, align2

def water(seq1, seq2):
    m, n = len(seq1), len(seq2)  # length of two sequences
    
    # Generate DP table and traceback path pointer matrix
    score = zeros((m+1, n+1))      # the DP table
    pointer = zeros((m+1, n+1))    # to store the traceback path
    
    max_score = 0        # initial maximum score in DP table
    # Calculate DP table and mark pointers
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diagonal = score[i-1][j-1] + match_score(seq1[i-1], seq2[j-1])
            score_up = score[i][j-1] + gap_penalty
            score_left = score[i-1][j] + gap_penalty
            score[i][j] = max(0,score_left, score_up, score_diagonal)
            if score[i][j] == 0:
                pointer[i][j] = 0 # 0 means end of the path
            if score[i][j] == score_left:
                pointer[i][j] = 1 # 1 means trace up
            if score[i][j] == score_up:
                pointer[i][j] = 2 # 2 means trace left
            if score[i][j] == score_diagonal:
                pointer[i][j] = 3 # 3 means trace diagonal
            if score[i][j] >= max_score:
                max_i = i
                max_j = j
                max_score = score[i][j];
    
    align1 = []
    align2 = []    # initial sequences
    
    i,j = max_i,max_j    # indices of path starting point
    
    #traceback, follow pointers
    while pointer[i][j] != 0:
        if pointer[i][j] == 3:
            align1.append(seq1[i-1])
            align2.append(seq2[j-1])
            i -= 1
            j -= 1
        elif pointer[i][j] == 2:
            align1.append('-')
            align2.append(seq2[j-1])
            j -= 1
        elif pointer[i][j] == 1:
            align1.append(seq1[i-1])
            align2.append('-')
            i -= 1

    return finalize(align1, align2)
