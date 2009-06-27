#!/opt/python2.5/bin/python
# vim:set smartindent:

# timings: p6 0.57 sec
#          p7 0.47 sec
#          p2 0.35 sec
#          p1 0.19 sec

from __future__ import with_statement
import sys
import re
import pdb
import unittest

class Puzzle:
    def __init__(self, buf):
        self.fields = []
        for i in xrange(9*9):
            self.fields.append(Field(i, buf[i], self))

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
        return set([f.value for f in 
                    self.cell(pos) + self.row(pos) + self.column(pos)
                    if f.value != ' ' and f.index != pos])
    
    def zoneCheck(self, pos, char):
        """ returns True when no other empty field in the zone of pos has
            the value 'char' as a candidate """
        x = set()
        for f in self.cell(pos):
            if f.index != pos and f.value == ' ':
                x = x | f.candidates
        if char not in x:
            return True
        x = set()
        for f in self.row(pos):
            if f.index != pos and f.value == ' ':
                x = x | f.candidates
        if char not in x:
            return True
        x = set()
        for f in self.column(pos):
            if f.index != pos and f.value == ' ':
                x = x | f.candidates
        if char not in x:
            return True
        return False

    def zoneClear(self, pos, char):
        for f in self.cell(pos):
            f.candidates.discard(char)
        for f in self.row(pos):
            f.candidates.discard(char)
        for f in self.column(pos):
            f.candidates.discard(char)

    def printme(self):
        print "".join([str(f) for f in self.fields])

    def pretty(self):
        for i in range(9):
            print " ".join([str(f) for f in self.fields[i*9 : i*9+9]])

class Field:
    def __init__(self, index, value, puzzle):
        self.index = index
        self.puzzle = puzzle
        self.value = value 
        self.candidates = set()
        if self.value == ' ':
            self.candidates = set('123456789')

    def __str__(self):
        return self.value

    def solved(self):
        return self.value == ' '

    def elim2(self):
        if self.value != ' ':
            return 0
        # for each remaining candidate, check if any of the other
        # free fields in this line, column, cell can accept the value
        # if not, then it is the solution
        for c in self.candidates:
            if self.puzzle.zoneCheck(self.index, c):
                self.value = c
                self.candidates.clear()
                self.puzzle.zoneClear(self.index, c)
                print "Elim2: %d -> %c" % (self.index, c)
                return 1
        return 0
    
    def solve(self): 
        if self.value != ' ':
            return 0
        # check which of the candidates are still valid,
        # i.e. not taken on the line, column and cell
        foo = self.candidates.copy()
        zv = self.puzzle.zoneValues(self.index)
        self.candidates = self.candidates - zv
        if len(self.candidates) == 1:
            self.value = self.candidates.pop()
            self.puzzle.zoneClear(self.index, self.value)
            return 1
        elif len(self.candidates) == 0:
            pdb.set_trace()
            raise 'Bug!'
        return 0

def solvePuzzle(puzzle_lines):
    puzzle = Puzzle(puzzle_lines)
    while True:
        solved = 0
        for field in puzzle:
            solved += field.solve()        
        print "-" * 50
        puzzle.pretty()
        for field in puzzle:
            solved += field.elim2()        
        print " " * 50
        puzzle.pretty()
        if solved > 0:
            print "Solved %d fields" % solved
        else:
            break
        #pdb.set_trace()

def verify(puzzle): 
    # check if any field has more than one or less than one candidate
    if len([c for c in puzzle if len(c)!=1]) > 0:
        return False
    # check if all positions are valid
    for pos in xrange(9*9):
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
    with open('puzzles/top95.txt') as f:
        for line in f:
            puzzle = list(line.replace('.',' '))
            solvePuzzle(puzzle)
    
def main():
    if len(sys.argv) < 2:
        # no puzzle file name given, run Top95
        if False:
            runTop95()
        else:
            unittest.main()
    else:
        filename = sys.argv[1]
        puzzle = readPuzzle(filename)
        solvePuzzle(puzzle)

class PuzzleTest(unittest.TestCase):
    P1 = '38 6     '\
         '  9      '\
         ' 2  3 51 '\
         '     5   '\
         ' 3  1  6 '\
         '   4     '\
         ' 17 5  8 '\
         '      9  '\
         '     7 32'

    def testZoneValues(self):
        p1 = Puzzle(self.P1)
        self.assertEqual(p1.zoneValues(0), set('8692'))
        self.assertEqual(p1.zoneValues(1), set('362319'))
        self.assertEqual(p1.zoneValues(2), set('386927'))
        self.assertEqual(p1.zoneValues(3), set('3843'))
        self.assertEqual(p1.zoneValues(4), set('386315'))
        self.assertEqual(p1.zoneValues(8), set('386512'))
        self.assertEqual(p1.zoneValues(27), set('35'))
        self.assertEqual(p1.zoneValues(40), set('365435'))
        self.assertEqual(p1.zoneValues(45), set('34'))
        self.assertEqual(p1.zoneValues(79), set('289761'))
        self.assertEqual(p1.zoneValues(80), set('3987'))

    def testZoneCandidates(self):
        p1 = Puzzle(self.P1)
        self.assertEqual(p1.zoneCheck(2, '1'), False)
        self.assertEqual(p1.zoneCheck(2, '2'), False)
        self.assertEqual(p1.zoneCheck(2, '5'), False)
        #self.assertEqual(p1.zoneCheck(12, '5'), True)
        #self.assertEqual(p1.zoneCheck(65, '3'), True)

if __name__ == '__main__':
    main()
