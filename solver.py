#!/usr/bin/python
# vim: set ts=4 sw=4 smartindent:

from __future__ import with_statement
import sys
import re
import pdb
import copy
import unittest

# Exceptions 
class InvalidPuzzle: pass

class Field:
    def __init__(self, index, value, puzzle):
        self.index = index
        self.puzzle = puzzle
        self.value = value 
        self.candidates = ''
        if not self.solved():
            self.candidates = '123456789'

    def __str__(self):
        return self.value

    def solved(self):
        return self.value != ' '

    def elim2(self):
        # for each remaining candidate, check if any of the other
        # free fields in this line, column, cell can accept the value
        # if not, then it is the solution
        for c in self.candidates:
            if self.puzzle.zoneCheck(self.index, c):
                self.value = c
                self.candidates = ''
                self.puzzle.zoneClear(self.index, c)
                return 1
        return 0
    
    def elim1(self): 
        if self.solved():
            return 0
        # check which of the candidates are still valid,
        # i.e. not taken on the line, column and cell
        zv = self.puzzle.zoneValues(self.index)
        for c in zv:
            if c in self.candidates:
                self.candidates = self.candidates.replace(c,'')
        if len(self.candidates) == 1:
            self.value = self.candidates
            self.candidates = ''
            self.puzzle.zoneClear(self.index, self.value)
            return 1
        elif len(self.candidates) == 0:
            raise InvalidPuzzle
        return 0

class Puzzle:
    def __init__(self, buf=''):
        self.fields = []
        if len(buf):
            for i in xrange(9*9):
                self.fields.append(Field(i, buf[i], self))

    def copy(self):
        c = Puzzle()
        c.fields = copy.deepcopy(self.fields)
        return c

    def __iter__(self):
        for f in self.fields:
            yield f
        raise StopIteration()

    def row(self, index):
        """ returns all fields in the same row as the given index """
        return self.fields[index-index%9 : index-index%9+9]

    def column(self, index):
        """ returns all fields in the same column as the given index """
        return self.fields[index%9 :: 9]

    def cell(self, index):
        """ returns all fields in the same 3x3 cell as the given index """
        topleft = index - index%3 - 9*(((index-index%3)%27)/9)
        r = self.fields[topleft   :topleft+3]   \
          + self.fields[topleft+9 :topleft+9+3] \
          + self.fields[topleft+18:topleft+18+3]
        return r
 
    def zoneValues(self, pos):
        r = ''
        L = [f.value for f in 
                    self.cell(pos) + self.row(pos) + self.column(pos)
                    if f.value != ' ' and f.index != pos]
        for l in L:
            if l not in r:
                r += l
        return r
    
    def zoneCheck(self, pos, char):
        """ returns True when no other empty field in the zone of pos has
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
        for f in self.cell(pos):
            f.candidates = f.candidates.replace(char, '')
        for f in self.row(pos):
            f.candidates = f.candidates.replace(char, '')
        for f in self.column(pos):
            f.candidates = f.candidates.replace(char, '')

    def pretty(self):
        for i in range(9):
            print " ".join([str(f) for f in self.fields[i*9 : i*9+9]])

    def solved(self):
        for field in self.fields:
            if not field.solved():
                return False
        return True

    def elim1(self):
        solved = 0
        for field in self.fields:
            solved += field.elim1()        
        return solved

    def elim2(self):
        solved = 0
        for field in self.fields:
            solved += field.elim2()
        return solved

    def findTrialField(self):
        f = None
        for field in self.fields:
            if field.solved():
                continue
            if f == None or len(field.candidates) < len(f.candidates):
                f = field
        return f

    def solve(self):
        while True:
            solved = 0
            solved += self.elim1()
            solved += self.elim2()
            if solved == 0:
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
            c = field.candidates
            field.candidates = ''
            for value in c:
                #print "Trying value %s for field %d" % (value, field.index)
                field.value = value
                C = self.copy()
                try:
                    C = C.solve()
                    if C != None:
                        return C
                except InvalidPuzzle:
                    #print "Invalid!"
                    pass
                del C
        return None

def solvePuzzle(puzzle_lines):
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
