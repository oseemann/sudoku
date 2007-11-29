#!/opt/python2.5/bin/python

# timings: p6 0.57 sec
#          p7 0.47 sec
#          p2 0.35 sec
#          p1 0.19 sec

from __future__ import with_statement
import sys
import re
import copy

def legal_candidate(puzzle, pos, x):
    # value on row?
    saved = puzzle[pos]
    puzzle[pos] = ' '
    if x in puzzle[pos-pos%9:pos-pos%9+9]: 
        puzzle[pos] = saved
        return False

    # value on column?
    if x in puzzle[pos%9::9]:  
        puzzle[pos] = saved
        return False

    # value in 3x3 cell?
    topleft = pos - pos%3 - 9*(((pos-pos%3)%27)/9)
    if x in puzzle[topleft   :topleft+3   ]:
        puzzle[pos] = saved
        return False
    if x in puzzle[topleft+9 :topleft+9+3 ]:
        puzzle[pos] = saved
        return False
    if x in puzzle[topleft+18:topleft+18+3]:
        puzzle[pos] = saved
        return False

    # not found
    puzzle[pos] = saved
    return True

def build_candidates(puzzle):
    candidates = []
    for pos in range(9*9):
        cand_list = ''
        if puzzle[pos] == ' ':
            for digit in "123456789":
                if legal_candidate(puzzle, pos, digit):
                   cand_list += digit
        else:
            cand_list += puzzle[pos]
        candidates.append(cand_list)

    return candidates

def eliminate(candidates):
    elimination_counter = 1
    while elimination_counter > 0:
        elimination_counter = 0
        for pos in range(9*9):
            if len(candidates[pos]) > 1:
                for digit in candidates[pos]:
                    if not legal_candidate(candidates, pos, digit):
                        candidates[pos] = candidates[pos].replace(digit,'')
                        elimination_counter += 1
                        if len(candidates[pos]) == 0:
                            return True
    return False

def print_candidates(puzzle):
    tab = 9 # max len(candidates[i])+1
    if verify(puzzle):
        print "Solution:"
        tab = 0
    for i in range(81):
        nCand = len(puzzle[i])
        print "".join(puzzle[i]), " " * (tab-nCand),
        if i % 9 == 8:
            print ""

def gen_guesses(candidates):
# find pos with smallest number of candidates
    ret = []
    pos = -1
    pos_len = 9
    for cand_list in candidates:
        if len(cand_list) == 1:
            continue
        if len(cand_list) < pos_len:
            pos_len = len(cand_list)
            pos = candidates.index(cand_list)
        if pos_len == 2:
            break
    if pos == -1:
        return ret
 
    for x in candidates[pos]:
        guess = copy.deepcopy(candidates)
        guess[pos] = x
        ret.append(guess)

    return ret 


def find_solutions(cand):
    ret = []
    guess_list = gen_guesses(cand)
    for guess in guess_list:
        if eliminate(guess) == True: # unsolvable?
            continue
        if verify(guess) and ret.count(guess) == 0:
            ret.append(guess)
        else:
            sols = find_solutions(guess)
            for X in sols:
                if ret.count(X) == 0:
                    ret.append(X)
    return ret

def solve(puzzle):
    cand = build_candidates(puzzle)
    eliminate(cand)
    if verify(cand):
        print_candidates(cand)
        return
    else:
        solutions = find_solutions(cand)
        for sol in solutions:
            print_candidates(sol)

def verify(puzzle): 
    # check if any field has more than one or less than one candidate
    if len([c for c in puzzle if len(c)!=1]) > 0:
        return False
    # check if all positions are valid
    for pos in range(9*9):
        if not legal_candidate(puzzle, pos, puzzle[pos]):
            return False
    return True

def readPuzzle(filename):
    puzzle = []
    linecheck = re.compile('^[ 0-9]{9}$')
    with open(filename) as f:
        for line in f:
            line = line.strip('\n')
            if linecheck.match(line):
                puzzle += list(line)
            else:
                raise "linecheck"
    if len(puzzle) != 81:
        print len(puzzle)
        raise "lengthcheck"
    return puzzle

def runTop95():
    print "Running Top95 Benchmark.."
    with open('top95.txt') as f:
        for line in f:
            puzzle = list(line.replace('.',' '))
            solve(puzzle)
    
def main():
    if len(sys.argv) < 2:
        # no puzzle file name given, run Top95
        runTop95()
    else:
        filename = sys.argv[1]
        puzzle = readPuzzle(filename)
        solve(puzzle)

if __name__ == '__main__':
    main()
