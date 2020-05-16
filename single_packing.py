# pack a single polyomino shape into a rectangle
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
              [7, 8, 9, 17, 16, 24, 32]
              ]

shapes = [[0, 7, 8, 9, 16],
          [1, 1, 2, 3, 4], [1, 8, 16, 24, 32],
          [2, 1, 2, 8, 16], [2, 1, 2, 10, 18], [2, 8, 14, 15, 16], [2, 8, 16, 17, 18],
          [3, 1, 2, 9, 17], [3, 6, 7, 8, 16], [3, 8, 15, 16, 17], [3, 8, 9, 10, 16],
          [4, 1, 2, 8, 10], [4, 1, 9, 16, 17], [4, 2, 8, 9, 10], [4, 1, 8, 16, 17],
          [5, 1, 7, 8, 15], [5, 1, 9, 10, 18], [5, 7, 8, 14, 15], [5, 8, 9, 17, 18],
          [6, 1, 8, 15, 16], [6, 8, 9, 10, 18], [6, 1, 9, 17, 18], [6, 6, 7, 8, 14],
          [7, 1, 2, 3, 8], [7, 1, 9, 17, 25], [7, 5, 6, 7, 8], [7, 8, 16, 24, 25], [7, 8, 9, 10, 11], [7, 1, 8, 16, 24], [7, 1, 2, 3, 11], [7, 8, 16, 23, 24],
          [8, 1, 2, 8, 9], [8, 1, 8, 9, 17], [8, 1, 7, 8, 9], [8, 8, 9, 16, 17], [8, 1, 8, 9, 10], [8, 1, 8, 9, 16], [8, 1, 2, 9, 10], [8, 7, 8, 15, 16],
          [9, 1, 2, 3, 9], [9, 7, 8, 16, 24], [9, 6, 7, 8, 9], [9, 8, 16, 17, 24], [9, 1, 2, 3, 10], [9, 8, 15, 16, 24], [9, 7, 8, 9, 10], [9, 8, 9, 16, 24],
          [10, 1, 9, 10, 11], [10, 7, 8, 15, 23], [10, 1, 2, 10, 11], [10, 8, 15, 16, 23], [10, 1, 2, 7, 8], [10, 8, 9, 17, 25], [10, 1, 6, 7, 8], [10, 8, 16, 17, 25],
          [11, 1, 9, 10, 17], [11, 6, 7, 8, 15], [11, 7, 8, 16, 17], [11, 7, 8, 9, 15], [11, 1, 7, 8, 16], [11, 7, 8, 9, 17], [11, 8, 9, 15, 16], [11, 8, 9, 10, 17],
          ]

target_sol = [(2, 22), (1, 27)]#, (2, 29), (1, 34), (2, 36)]

start_time = time()
number_placed = 0
iterations = 0


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
            # go through and add the statisfaction constraint for each type of piece
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
        if len(board_object.solution) > number_placed:
            number_placed = len(board_object.solution)
            print(loc, len(board_object.solution), iterations, time()-start_time)
        if board_object.solution == target_sol:
            print("got start of solution", time()-start_time)
        if not board_object.test(loc, piece_index):
            piece_index += 1
            continue
        if not board_object.board_has_holes():
            piece_index += 1
            continue

        board_object.place_on_board(loc=loc, piece_index=piece_index)
        #board_object.print_board()
        #board_object.board_has_holes()
        #print("has holes", board_object.board_has_holes())

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

    args = parser.parse_args()
    width = 28+7
    length = 19
    _board = Board(width, length, heptominos, unique=False)
    rebuild_shapes(_board, margin=False)
    #for piece_type, loc in target_sol:
    #    _board.place_on_board(piece_index=piece_type, loc=loc)

    #_board.print_board_locations()
    #place(_board, nsols=0)
    print(constraint_solution(_board))