#!/opt/python2.5/bin/python

from __future__ import with_statement
import sys
import re
import copy

def legal_candidate(puzzle, pos, x):
    # value on row?
    if [x] in puzzle[pos-pos%9:pos-pos%9+9]: 
        return False
    # value on column?
    if [x] in puzzle[pos%9::9]:  
        return False
    # value in 3x3 cell?
    topleft = pos - pos%3 - 9*(((pos-pos%3)%27)/9)
    if [x] in puzzle[topleft   :topleft+3   ]: return False
    if [x] in puzzle[topleft+9 :topleft+9+3 ]: return False
    if [x] in puzzle[topleft+18:topleft+18+3]: return False
    # not found
    return True

def build_candidates(puzzle):
    candidates = []
    for pos in range(9*9):
        cand_list = []
        if puzzle[pos] == ' ':
            for digit in "123456789":
                if legal_candidate(puzzle, pos, digit):
                   cand_list.append(digit)
        else:
            cand_list.append(puzzle[pos])
        candidates.append(cand_list)

    return candidates

def eliminate(candidates):
    elc = 1
    while elc > 0:
        elc = 0
        for pos in range(9*9):
            if len(candidates[pos]) > 1:
                for digit in candidates[pos]:
                    if not legal_candidate(candidates, pos, digit):
                        candidates[pos].remove(digit)
                        elc += 1

    return candidates

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
    
    for x in candidates[pos]:
        guess = copy.deepcopy(candidates)
        guess[pos] = [x]
        ret.append(guess)

    return ret 

def find_solutions(puzzle, cand):
    ret = []
    guess_list = gen_guesses(cand)
    for guess in guess_list:
        newcand = eliminate(guess)
        if newcand == puzzle:
            break # could not eliminate further
        if verify(newcand) and ret.count(newcand) == 0:
            ret.append(newcand)
        else:
            sols = find_solutions(cand, newcand)
            for X in sols:
                if ret.count(X) == 0:
                    ret.append(X)
    return ret

def solve(puzzle):
    cand = build_candidates(puzzle)
    cand = eliminate(cand)
    print_candidates(cand)
    if verify(cand):
        print_candidates(cand)
        return
    else:
        solutions = find_solutions(puzzle, cand)
        for sol in solutions:
            print_candidates(sol)

def verify(puzzle):
    for pos in range(9*9):
        if len(puzzle[pos]) != 1:
            return False
        digit = puzzle[pos][0]
        puzzle[pos] = []
        if not legal_candidate(puzzle, pos, digit):
            puzzle[pos] = [digit]
            return False
        puzzle[pos] = [digit]
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
    
def main():
    if len(sys.argv) < 2:
        print "No puzzle file name given"
        return
    filename = sys.argv[1]
    puzzle = readPuzzle(filename)
    solve(puzzle)

if __name__ == '__main__':
    main()
