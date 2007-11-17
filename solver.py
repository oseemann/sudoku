#!/opt/python2.5/bin/python

from __future__ import with_statement
import sys

def value_on_row(puzzle, pos, x):
    return x in puzzle[pos-pos%9:pos-pos%9+9]

def value_on_col(puzzle, pos, x):
    return x in puzzle[pos%9::9]

def value_in_cell(puzzle, pos, x):
    topleft = pos - pos%3
    if topleft%27 >= 9: topleft -= 9
    if topleft%27 >= 9: topleft -= 9

    if x in puzzle[topleft   :topleft+3   ]: return True
    if x in puzzle[topleft+9 :topleft+9+3 ]: return True
    if x in puzzle[topleft+18:topleft+18+3]: return True

    return False
  
def legal_candidate(puzzle, pos, x):
    if value_on_row(puzzle, pos, x):
        return False
    if value_on_col(puzzle, pos, x):
        return False
    if value_in_cell(puzzle, pos, x):
        return False
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

def eliminate(puzzle, candidates):
    elc = 1
    while elc > 0:
        elc = 0
        for pos in range(9*9):
            if len(candidates[pos])==1 and puzzle[pos] == ' ':
                puzzle[pos] = candidates[pos][0]
            else:
                for x in candidates[pos]:
                    if not legal_candidate(puzzle, pos, x):
                        candidates[pos].remove(x)
                        elc += 1
    return puzzle

def print_puzzle(puzzle):
    print "Solution:"
    for i in range(9):
        print " ".join(puzzle[i*9:i*9+9])

def print_candidates(puzzle):
    print "Candidates:"
    for i in range(81):
        nCand = len(puzzle[i])
        print "".join(puzzle[i]), " " * (9-nCand),
        if i % 9 == 8:
            print ""

def solve(puzzle):
    cand = build_candidates(puzzle)
    print_candidates(cand)
    solution = eliminate(puzzle, cand)
    print_puzzle(solution)

def readPuzzle(filename):
    puzzle = []
    with open(filename) as f:
        for line in f:
            puzzle += list(line.strip('\n'))
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
