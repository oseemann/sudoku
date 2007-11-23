#!/opt/python2.5/bin/python

from __future__ import with_statement
import sys
import re
import copy

def value_on_row(puzzle, pos, x):
    return x in puzzle[pos-pos%9:pos-pos%9+9]

def value_on_col(puzzle, pos, x):
    return x in puzzle[pos%9::9]

def value_in_cell(puzzle, pos, x):
    topleft = pos - pos%3 - 9*(((pos-pos%3)%27)/9)
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
            cand_list = candidates[pos]
            if len(cand_list)==1:
                if puzzle[pos] == ' ':
                    puzzle[pos] = cand_list[0]
                    elc += 1
            else:
                for digit in cand_list:
                    if not legal_candidate(puzzle, pos, digit):
                        cand_list.remove(digit)
                        if len(cand_list) == 1:
                            puzzle[pos] = cand_list[0]
                        elc += 1

    return (puzzle, candidates)

def print_puzzle(puzzle):
    print "Solution:"
    for i in range(9):
        print " ".join(puzzle[i*9:i*9+9])
    if verify(puzzle):
        print "Correct!"
    else:
        print "Wrong! Uh-oh.."

def print_candidates(puzzle):
    print "Candidates:"
    for i in range(81):
        nCand = len(puzzle[i])
        print "".join(puzzle[i]), " " * (9-nCand),
        if i % 9 == 8:
            print ""

def gen_guesses(puzzle, candidates):
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
    guess_list = gen_guesses(puzzle, cand)
    for guess in guess_list:
        (s, c) = eliminate(copy.deepcopy(puzzle), guess)
        if s == puzzle:
            break # could not eliminate further
        if verify(s) and ret.count(s) == 0:
            ret.append(s)
        else:
            sols = find_solutions(s, c)
            for X in sols:
                if ret.count(X) == 0:
                    ret.append(X)
    return ret

def solve(puzzle):
    cand = build_candidates(puzzle)
    #print_candidates(cand)
    (solution, cand) = eliminate(puzzle, cand)
    if verify(solution):
        print_puzzle(solution)
        return
    else:
        solutions = find_solutions(solution, cand)
        for sol in solutions:
            print_puzzle(sol)
            
def verify(puzzle):
    for pos in range(9*9):
        digit = puzzle[pos]
        puzzle[pos] = ' '
        if not legal_candidate(puzzle, pos, digit):
            puzzle[pos] = digit
            return False
        puzzle[pos] = digit
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
