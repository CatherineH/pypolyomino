# pack a single polyomino shape into a rectangle
import sys
from argparse import ArgumentParser
from time import time

from constraint import Problem

from common import Board, rebuild_shapes, output_to_svg

heptominos = [[0, 1, 8, 9, 10, 11, 7],
              [1, 1, 8, 9, 10, 6, 7],
              [2, 1, 2, 3, 4, 9, 10],
              [3, 1, 2, 3, 4, 10, 11],
              [4, 8, 9, 16, 17, 24, 32],
              [5, 8, 16, 17, 24, 25, 32],
              [6, 8, 15, 16, 23, 24, 32],
              [7, 7, 8, 15, 16, 24, 32]
              ]

target_sol = [2,1,2,1,2,1,3,4,7,3,0,3,0,3]


start_time = time()
number_placed = 0
iterations = 0


class HeptominoBoard(Board):
    def __init__(self, width, length, shapes, unique=True):
        super().__init__(width, length, shapes, unique=True)

    def test(self, loc, pattern):
        piece = self.shapes[pattern][0]
        # don't create a board with a hole
        if piece == 0:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row, col - 2)
            upper_index = self.board_row_col_to_index(row+1, col - 3)
            right_index = self.board_row_col_to_index(row+2, col-2)
            hole_index = self.board_row_col_to_index(row+1, col-2)
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[right_index] is not None) and (self.board[hole_index] is None):
                return 0
        elif piece == 2:
            row, col = self.board_index_to_row_col(loc)
            upper_index = self.board_row_col_to_index(row + 1, col - 1)
            right_index = self.board_row_col_to_index(row + 2, col)
            hole_index = self.board_row_col_to_index(row + 1, col)
            if (self.board[upper_index] is not None) and (self.board[hole_index] is None) and \
                    (self.board[right_index] is not None):
                return 0
        elif piece == 3:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row + 1, col - 1)
            right_index = self.board_row_col_to_index(row + 2, col)
            hole_index = self.board_row_col_to_index(row + 1, col)
            if (self.board[left_index] is not None) and (self.board[hole_index] is None) and \
                    (self.board[right_index] is not None):
                return 0
        elif piece == 4:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row, col + 2)
            right_index = self.board_row_col_to_index(row + 2, col + 2)
            lower_index = self.board_row_col_to_index(row + 1, col + 3)
            hole_index = self.board_row_col_to_index(row + 1, col + 2)
            if (self.board[left_index] is not None) and (self.board[lower_index] is not None) and \
                    (self.board[right_index] is not None) and (self.board[hole_index] is None):
                return 0
        elif piece == 5:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row, col+1)
            upper_index = self.board_row_col_to_index(row+1, col+2)
            hole_index = self.board_row_col_to_index(row + 1, col + 1)
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[hole_index] is None):
                return 0
            upper_index = self.board_row_col_to_index(row + 1, col + 3)
            hole_index2 = self.board_row_col_to_index(row + 1, col + 2)
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[hole_index] is None) and (self.board[hole_index2] is None):
                return 0
            left_index = self.board_row_col_to_index(row-1, col)
            right_index = self.board_row_col_to_index(row - 2, col)
            upper_index = self.board_row_col_to_index(row - 3, col+1)
            hole_index = self.board_row_col_to_index(row+1, col-1)
            hole_index2 = self.board_row_col_to_index(row + 1, col - 2)
            if (self.board[left_index] is not None) and (self.board[right_index] is not None) and \
                    (self.board[upper_index] is not None) and (self.board[hole_index] is None) and (self.board[hole_index2] is None):
                return 0
        elif piece == 6:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row, col-1)
            upper_index = self.board_row_col_to_index(row+1, col-2)
            hole_index = self.board_row_col_to_index(row+1, col -1)
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[hole_index] is None):
                return 0
            upper_index = self.board_row_col_to_index(row + 1, col - 3)
            hole_index2 = self.board_row_col_to_index(row+1, col -2 )
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[hole_index] is None) and (self.board[hole_index2] is None):
                return 0
        elif piece == 7:
            row, col = self.board_index_to_row_col(loc)
            left_index = self.board_row_col_to_index(row, col-2)
            upper_index = self.board_row_col_to_index(row+1, col-3)
            right_index = self.board_row_col_to_index(row+2, col-2)
            hole_index = self.board_row_col_to_index(row +1, col -2)
            if (self.board[left_index] is not None) and (self.board[upper_index] is not None) and \
                    (self.board[right_index] is not None) and (self.board[hole_index] is None):
                return 0

        for shape_loc in self.shapes[pattern][1:]:
            if self.board[loc+shape_loc] is not None:
                return 0
        # we also want to make sure that the board does not contain any empty islands
        return 1


def constraint_solution(board_object):
    problem = Problem()
    number_of_pieces = 76
    width = 28
    length = 19
    # board locations
    variables = [f"row{row}col{col}" for row in range(width) for col in range(length)]
    # pieces
    values = [f"piece{piece}part{part}" for part in range(7) for piece in range(number_of_pieces)]
    for variable in variables:
        problem.addVariable(variable, values)
    # only one piece per board location
    for location1 in variables:
        for location2 in variables:
            if location1 == location2:
                continue
            problem.addConstraint(lambda x, y: x != y, (location1, location2))

    # add constraints for the pieces

    for i in range(len(variables)):
        def piece_constraint(*args):
            location = i
            board = args[1:]
            # go through and add the satisfaction constraint for each type of piece
            for shape in board_object.shapes:
                for shape_index in range(number_of_pieces):
                    other_parts = []
                    for part, offset in enumerate(shape[1:]):
                        if (location + offset) >= len(board): # piece is off the board
                            return 0

                        other_parts.append(board[location + offset] == f"piece{shape_index}part{part + 1}")
                    if board[location] == f"piece{shape_index}part0" and all(other_parts):
                        return 1
            return 0

        problem.addConstraint(piece_constraint, (variables))

    return problem.getSolution()


# place a piece in the board; recursive
def place(board_object, nsols):
    piece_index = 0
    global number_placed
    global iterations
    iterations += 1
    while (loc := board_object.findloc()) and piece_index < len(board_object.shapes):
        if not board_object.test(loc, piece_index):

            i = 0
            while i < min(len(board_object.solution), len(target_sol)):
                if board_object.solution[i][0] < target_sol[i]:
                    break
                i += 1
            try:
                if piece_index == target_sol[i] and len(board_object.solution) == i:
                    print("passing over solution!", board_object.solution, i, piece_index, target_sol[i])
                    sys.exit()
            except IndexError:
                print("index error", i, board_object.solution, target_sol)
                sys.exit()

            piece_index += 1
            continue

        #if iterations % 1000 == 0:
        if all(board_object.solution[i][0] == target_sol[i] for i in range(min(len(board_object.solution),len(target_sol)))):
            number_placed = len(board_object.solution)
            print(loc, len(board_object.solution), iterations, time()-start_time, [entry[0] for entry in board_object.solution])
            board_object.print_board()
        for i in range(min(len(board_object.solution), len(target_sol))):
            if board_object.solution[i][0] < target_sol[i]:
                break
            if board_object.solution[i][0] > target_sol[i]:
                print(board_object.solution)
                board_object.print_board()
                print("failed to find solution!")
                sys.exit()

        board_object.place_on_board(loc=loc, piece_index=piece_index)

        if args.debug:
            print(f"placing piece [{piece_index}] at square {loc}")  # if the entire board is occupied
            board_object.print_board()
            print(loc, board_object.solution)
        if not board_object.findloc():
            nsols += 1
            if args.svg:
                output_to_svg(board_object, nsols)
            #  print solution
            if args.dispflag:
                print(f"solution {nsols}: ")
                board_object.print_board()
        else:
            nsols = place(board_object, nsols)
        #  remove piece
        board_object.remove_piece_from_board(piece_index, loc)
        piece_index += 1
    return nsols
#  place


if __name__ == "__main__":
    parser = ArgumentParser(description='Generate rectangular packings of a single polyomino shape.')
    parser.add_argument('-d', dest='dispflag', action='store_true', help='print all board solutions')
    parser.add_argument('-c', dest='countflag', action='store_true',
                        help='print number of solutions')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true',
                        help='print debugging info')
    parser.add_argument('-s', dest='svg', action='store_true', help='save solution as svg')

    parser.add_argument('--csp', dest='use_csp', action='store_true', help='save solution as svg')

    args = parser.parse_args()
    width = 26
    length = 19
    _board = HeptominoBoard(width, length, heptominos, unique=False)

    rebuild_shapes(_board, margin=not args.use_csp)
    if args.use_csp:
        print(constraint_solution(_board))
    else:
        place(_board, nsols=0)