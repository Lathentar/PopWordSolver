#!/usr/bin/python

import sys, getopt, copy

skWordScoresByLength = [0, 0, 0, 1, 2, 4, 7, 11, 17, 25, 35, 50, 70, 100, 140, 200, 270, 300, 400, 500, 600, 700]

def printusage():
   print 'test.py -w <worldlistfile> -i <inputfile>' 

def breakup_word(word, wordlist):
   if (len(word) == 0):
      wordlist['*'] = 1
   elif (word[0] in wordlist.keys()):
      breakup_word(word[1:], wordlist[word[0]])
   else:
      wordlist[word[0]] = {}
      breakup_word(word[1:], wordlist[word[0]])


def parse_word_list_file(wordlistfile):
   with open(wordlistfile) as f:
      #read the words from the word list
      wordlist = {}
      for word in f:
         strippedWord = word.strip()
         if ( len(strippedWord) > 2 ):
            breakup_word(strippedWord, wordlist)

      return wordlist

def find_words_at_pos(wordlist, board, numRows, numColumns, pos, word):
   foundWords = []

   if (pos[0] < 0 or numRows <= pos[0]):
      return foundWords

   if (pos[1] < 0 or numColumns <= pos[1]):
      return foundWords

   charAtPos = board[pos[0]][pos[1]]

   # mark the letter at that position as - to indicated used
   word += charAtPos

   if (charAtPos == '-' or charAtPos == '*'):
      return foundWords

   if (charAtPos not in wordlist.keys()):
      return foundWords

   # is this a real word? add it to the found words list
   newBoard = copy.deepcopy(board)
   newBoard[pos[0]][pos[1]] = '*'

   if (len(word) >= 3 and '*' in wordlist[charAtPos]):
      foundWords.append((word, newBoard))

   # keep searching the rest of the board with this letter removed
   if ( len(wordlist) > 1 ):
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]-1, pos[1]-1), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]  , pos[1]-1), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]+1, pos[1]-1), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]-1, pos[1]  ), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]+1, pos[1]  ), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]-1, pos[1]+1), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]  , pos[1]+1), word)
      foundWords = foundWords + find_words_at_pos(wordlist[charAtPos], newBoard, numRows, numColumns, (pos[0]+1, pos[1]+1), word)

   return foundWords

def find_words_in_board(numRows, numColumns, board, wordlist):
   foundWords = []
   for r in xrange(0, numRows):
      for c in xrange(0, numColumns):
         foundWords += find_words_at_pos(wordlist, board, numRows, numColumns, (r, c), '')

   foundWords.sort(key=lambda x:len(x[0]), reverse=True)
   return foundWords

def minimize_board(numRows, numColumns, board):
   newBoard = copy.deepcopy(board)
   numLettersRemaining = 0

   # replace * with -
   for r in xrange(0, numRows):
      for c in xrange(0, numColumns):
         if newBoard[r][c] == '*':
            newBoard[r][c] = '-'
         elif newBoard[r][c] != '-':
            numLettersRemaining += 1

   # move letters downward
   for r in xrange(0, numRows):
      for c in reversed(xrange(0, numColumns)):
         if newBoard[r][c] == '-':
            # search up, until we find a valid letter
            for copyR in reversed(xrange(0, r)):
               if newBoard[copyR][c] != '-':
                  newBoard[r][c] = newBoard[copyR][c]

                  indexDiff = r - copyR
                  for replaceR in reversed(xrange(0, copyR + 1)):
                     if (replaceR - indexDiff >= 0):
                        newBoard[replaceR][c] = newBoard[replaceR - indexDiff][c]
                     else:
                        newBoard[replaceR][c] = '-'
               break

   validColumn = 0
   #find the last valid column
   for c in reversed(xrange(0, numColumns)):
      isValid = False
      for r in reversed(xrange(0, numRows)):
         if newBoard[r][c] != '-':
            isValid = True
            break
      if isValid:
         validColumn = c
         break

   # collapse empty columns
   checkColumn = validColumn - 1
   while (checkColumn >= 0):
      isValid = False
      # find if the check column is empty, if so shift all columns after that over
      for r in reversed(xrange(0, numRows)):
         if newBoard[r][checkColumn] != '-':
            isValid = True
            break
      if not isValid:
         for c in xrange(checkColumn, validColumn + 1):
            for r in xrange(0, numRows):
               if c == validColumn:
                  newBoard[r][c] = '-'
               else:
                  newBoard[r][c] = newBoard[r][c+1]
         # shift the valid Column over by one
         validColumn = validColumn - 1
      #shift check column over by one
      checkColumn = checkColumn - 1

   return ( newBoard, numLettersRemaining )

def is_board_complete(numRows, numColumns, board):
   for r in xrange(0, numRows):
      for c in xrange(0, numColumns):
         if board[r][c] != '-':
            return False
   return True

def board_to_string(board):
   str = ''
   for r in board:
      for c in r:
         str += c
   return str

def solve_board(numRows, numColumns, board, wordlist, board_mem):
   boardAsString = board_to_string(board)
   if boardAsString not in board_mem:
      foundWords = find_words_in_board(numRows, numColumns, board, wordlist)

      board_mem[boardAsString] = None

      # run through the found words, minimize the board and repeat
      for wordBoardPair in foundWords:
         miniPair = minimize_board(numRows, numColumns, wordBoardPair[1])
         newBoard = miniPair[0]
         numLettersRemaining = miniPair[1]

         if numLettersRemaining == 0:
            print 'Complete', boardAsString, 'Word', wordBoardPair[0], ' WordScore', skWordScoresByLength[len(wordBoardPair[0])]
            return [ (wordBoardPair, skWordScoresByLength[len(wordBoardPair[0])]) ]
         elif numLettersRemaining >= 3:         
            solvedBoard = solve_board(numRows, numColumns, newBoard, wordlist, board_mem);

            if solvedBoard != None:
               oldScore = solvedBoard[0][1]
               newScore = skWordScoresByLength[len(wordBoardPair[0])] + oldScore

               if board_mem[boardAsString] is None:
                  board_mem[boardAsString] = [(wordBoardPair, newScore)] + solvedBoard
               else:
                  # replace if the score is higher
                  if board_mem[boardAsString][1] < newScore:
                     board_mem[boardAsString] = [(wordBoardPair, newScore)] + solvedBoard

      if board_mem[boardAsString] is not None:
         print boardAsString, 'Word', board_mem[boardAsString][0][0][0], ' WordScore', skWordScoresByLength[len(board_mem[boardAsString][0][0][0])], 'TotalScore', board_mem[boardAsString][0][1]

   return board_mem[boardAsString]


def solve_popwords(wordlist, inputfile, justFindBestWord):
   #parse the input file
   numRows = 0
   numColumns = 0
   startingBoard = []
   with open(inputfile) as f:
      numRows = int( f.readline() )
      numColumns = int( f.readline() )

      for lines in f:
         row = lines.strip()
         startingBoard.append(list(row))

         if (len(row) != numColumns):
            print 'Error: row', row, ' is not long enough, expected length', numColumns
            sys.exit()

      if (len(startingBoard) != numRows):
         print 'Error: not enough rows in board', numRows

   # start with a depth first word search starting from the top left
   print 'Solving for board'
   for row in startingBoard:
      for letter in row:
         sys.stdout.write(letter)
      print

   if justFindBestWord == False:
      solvedBoard = solve_board(numRows, numColumns, startingBoard, wordlist, {})
      stepNum = 1
      if solvedBoard is not None:
         for step in solvedBoard:
            print 'Step', stepNum
            print '   Word', step[0][0], ' WordScore', skWordScoresByLength[len(step[0][0])]
            for line in step[0][1]:
               print '   ', ''.join(line)
            print
            stepNum += 1

         print 'Expected score', solvedBoard[0][1] * 2
      else:
         print 'No Solution Found'
   else:
      foundBestWord = find_words_in_board(numRows, numColumns, startingBoard, wordlist)[0]
      print 'Best Word', foundBestWord[0]
      for line in foundBestWord[1]:
         print '   ', ''.join(line)
      print



def main(argv):
   wordlistfile = ''
   inputfile = ''
   bestWord = False
   try:
      opts, args = getopt.getopt(argv,"hw:i:b",["wfile=", "ifile="])
   except getopt.GetoptError:
      printusage()
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         printusage()
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-w", "--wfile"):
         wordlistfile = arg
      elif opt == '-b':
         bestWord = True

   if (wordlistfile == '' or inputfile == ''):
      print 'Error: requires word list file and input file to function'
      printusage()
      sys.exit(2);

   wordlist = parse_word_list_file(wordlistfile)
   print 'Finished parsing wordlist'

   solve_popwords(wordlist, inputfile, bestWord)


if __name__ == "__main__":
   main(sys.argv[1:])