#!/usr/bin/python
# vim: set ts=4 sw=4 smartindent expandtab:
#
# My own Sudoku solver.
# Solves the top95 hardest puzzles (http://magictour.free.fr/top95)
# in less than a minute. Still rather slow, but hey, at least it solves
# them all.
# Performance can be improved by not using strings to store the candidates
# but maybe an integer representation.
#
# Author: Oliver Seemann <os (at) oebs.net>
# 
# This code is in the public domain. 

import sys
import re
import pdb
import copy

# Exceptions 
class InvalidPuzzle: pass

class Field:
    """ This class represents one of the 81 fields of a sudoku puzzle.
    It tracks all its own candidates and provides functions elim1 and
    elim2 to elimnate candidates. """
    def __init__(self, index, value, puzzle):
        self.index = index
        self.puzzle = puzzle
        self.value = value 
        self.candidates = ''
        if not self.solved():
            # initialize with all possible candidates
            self.candidates = '123456789'

    def __str__(self):
        return self.value

    def solved(self):
        """ Returns True when the field is solved. """
        return self.value != ' '

    def elim2(self):
        """ For each remaining candidate, check if any of the other
            free fields in this line, column, cell can accept the value.
            If not, then it is the solution.
            Returns the number of fields solved (0 or 1) """
        for c in self.candidates:
            if self.puzzle.zoneCheck(self.index, c):
                self.value = c
                self.candidates = ''
                self.puzzle.zoneClear(self.index, c)
                return 1
        return 0
    
    def elim1(self): 
        """ Check which of this field's candidates are still valid, i.e. not
            already taken on this line, column and cell.
            Returns number of fields solved (0 or 1). """
        if self.solved():
            return 0
        zv = self.puzzle.zoneValues(self.index)
        for c in zv:
            # remove all existing, fixed values in the zone from our own candidates
            if c in self.candidates:
                self.candidates = self.candidates.replace(c,'')
        if len(self.candidates) == 1:
            # only one candidate left, then this is the solution
            self.value = self.candidates
            self.candidates = ''
            self.puzzle.zoneClear(self.index, self.value)
            return 1
        elif len(self.candidates) == 0:
            raise InvalidPuzzle
        return 0

class Puzzle:
    """ This class represents the puzzle, consisting of 81 Field instances. """
    def __init__(self, buf=''):
        self.fields = []
        if len(buf):
            for i in xrange(9*9):
                self.fields.append(Field(i, buf[i], self))

    def copy(self):
        """ Some (hard) puzzles cannot be solved by simple elimination and solutions
            can only be found by trying out each candidate and eliminate again.
            This function is used to copy the puzzle in such a case in order to allow
            backtracking. """
        c = Puzzle()
        c.fields = copy.deepcopy(self.fields)
        return c

    def __iter__(self):
        for f in self.fields:
            yield f
        raise StopIteration()

    def row(self, index):
        """ Returns all fields in the same row as the given index. """
        return self.fields[index-index%9 : index-index%9+9]

    def column(self, index):
        """ Returns all fields in the same column as the given index. """
        return self.fields[index%9 :: 9]

    def cell(self, index):
        """ returns all fields in the same 3x3 cell as the given index. """
        topleft = index - index%3 - 9*(((index-index%3)%27)/9)
        r = self.fields[topleft   :topleft+3]   \
          + self.fields[topleft+9 :topleft+9+3] \
          + self.fields[topleft+18:topleft+18+3]
        return r
 
    def zoneValues(self, pos):
        """ Returns all solved values in the zone of given position. The zone is 
            set of all fields in the line, column and cell the given position."""
        result = ''
        values = [f.value for f in 
                    self.cell(pos) + self.row(pos) + self.column(pos)
                    if f.value != ' ' and f.index != pos]
        for val in values:
            if val not in result:
                result += val
        return result
    
    def zoneCheck(self, pos, char):
        """ Returns True when no other empty field in the zone of pos has
            the value 'char' as a candidate """
        x = "".join([f.candidates for f in self.row(pos) if f.index!=pos and f.value==' '])
        if char not in x:
            return True
        x = "".join([f.candidates for f in self.column(pos) if f.index!=pos and f.value==' '])
        if char not in x:
            return True
        x = "".join([f.candidates for f in self.cell(pos) if f.index!=pos and f.value==' '])
        if char not in x:
            return True
        return False

    def zoneClear(self, pos, char):
        """ Removes a candidate from the list of candidates of all fields in the
            zone f the given position. Called when solution for a field was found. """
        for f in self.cell(pos):
            f.candidates = f.candidates.replace(char, '')
        for f in self.row(pos):
            f.candidates = f.candidates.replace(char, '')
        for f in self.column(pos):
            f.candidates = f.candidates.replace(char, '')

    def pretty(self):
        """ Print the puzzle. """
        for i in range(9):
            print " ".join([str(f) for f in self.fields[i*9 : i*9+9]])

    def solved(self):
        """ Return True when the puzzle is solved. """
        for field in self.fields:
            if not field.solved():
                return False
        return True

    def elim1(self):
        """ First elimination round on all fields. """
        solved = 0
        for field in self.fields:
            solved += field.elim1()
        return solved

    def elim2(self):
        """ Second elimination round on all fields. """
        solved = 0
        for field in self.fields:
            solved += field.elim2()
        return solved

    def findTrialField(self):
        """ Returns a field with the least number of candidates in order
            to be used for trial-and-error and backtracking. """
        result = None
        for field in self.fields:
            if field.solved():
                continue
            if result == None or len(field.candidates) < len(result.candidates):
                result = field
        return result

    def solve(self):
        """ Solve the puzzle. """
        while True:
            # first try and use straight elimination until no fields could
            # eliminated any more
            solved = 0
            solved += self.elim1()
            solved += self.elim2()
            if solved == 0:
                # stop elimination, no new solution was found this round
                # must resort to trial-and-error (or puzzle was solved)
                break
        if self.solved():
            return self
        else:
            # find field with the lowest number of candidates 
            field = self.findTrialField()
            # if lowest number of candidates is zero, abort, wrong path
            if field == None or len(field.candidates) == 0:
                return None
            # for each such candidate, set it as a solution and try to solve
            trialcandidates = field.candidates
            field.candidates = ''
            for value in trialcandidates:
                #print "Trying value %s for field %d" % (value, field.index)
                field.value = value
                C = self.copy()
                try:
                    C = C.solve()
                    if C != None:
                        return C
                except InvalidPuzzle:
                    # this trial candidate resulted in an invalid puzzle
                    # continue with next candidate
                    pass
                del C
        return None

def solvePuzzle(puzzle_lines):
    """ Solves and prints a sudoku given as a 1 dimensional array [0..80] """
    puzzle = Puzzle(puzzle_lines)
    solution = puzzle.solve()
    if solution: 
       solution.pretty()

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
    with open('puzzles/top95.txt') as f:
        i = 0
        for line in f:
            puzzle = list(line.replace('.',' '))
            i += 1
            print "%d ..." % i
            solvePuzzle(puzzle)

def main():
    if len(sys.argv) < 2:
        runTop95()
    else:
        filename = sys.argv[1]
        puzzle = readPuzzle(filename)
        solvePuzzle(puzzle)

if __name__ == '__main__':
    main()
