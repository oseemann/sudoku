#!/opt/python2.5/bin/python

from __future__ import with_statement
import sys
import copy

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

    # if not solved, find pos with shorted candidate list, then try again with each of those candidates
    return (puzzle, candidates)

def print_puzzle(puzzle):
    print "Solution:"
    for i in range(9):
        print " ".join(puzzle[i*9:i*9+9])
    if verify(puzzle):
        print "Correct!"
    else:
        print "Wrong!"

def print_candidates(puzzle):
    print "Candidates:"
    for i in range(81):
        nCand = len(puzzle[i])
        print "".join(puzzle[i]), " " * (9-nCand),
        if i % 9 == 8:
            print ""

def solved(puzzle):
    return puzzle.count(' ') == 0

def gen_guesses(puzzle, candidates):
    ret = []
    # find pos with smallest number of candidates
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
        guess[pos] = list(x)
        ret.append(guess)
    
    # return x number of guesses for each candidate
    return ret 

def find_solutions(puzzle, cand):
    ret = []
    guess_list = gen_guesses(puzzle, cand)
    for guess in guess_list:
        porig = copy.deepcopy(puzzle)
        (s, c) = eliminate(porig, guess)
        if s == puzzle:
            break
       # print_puzzle(s)
        if verify(s):
            ret.append(s)
        else:
            sols = find_solutions(s, c)
            if len(sols)>0:
                ret.extend(sols)
    return ret

def solve(puzzle):
    cand = build_candidates(puzzle)
    print_candidates(cand)
    (solution, cand) = eliminate(puzzle, cand)
    print_candidates(cand)
    if solved(solution):
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
