# pack a single polyomino shape into a rectangle
import sys
from argparse import ArgumentParser
from copy import deepcopy
from multiprocessing import Pool
from time import time

from constraint import Problem

from common import Board, rebuild_shapes, output_to_svg

heptominos = [
    [0, 1, 7, 8, 9, 10, 11],
    [1, 1, 6, 7, 8, 9, 10],
    [2, 1, 2, 3, 4, 9, 10],
    [3, 1, 2, 3, 4, 10, 11],
    [4, 8, 9, 16, 17, 24, 32],
    [5, 8, 16, 17, 24, 25, 32],
    [6, 8, 15, 16, 23, 24, 32],
    [7, 7, 8, 15, 16, 24, 32],
]

hexominos = [
    [0, 7, 8, 9, 10, 11],
    [1, 5, 6, 7, 8, 9],
    [2, 1, 2, 3, 4, 9],
    [3, 1, 2, 3, 4, 11],
    [4, 7, 8, 16, 24, 32],
    [5, 8, 16, 23, 24, 32],
    [6, 8, 9, 16, 24, 32],
    [7, 8, 16, 24, 25, 32],
]

tetrominos = [
    [0, 1, 2, 3],  # A
    [1, 1, 8, 9],  # B
    [2, 8, 16, 24],  # C
    [3, 8, 16, 17],  # D
    [4, 8, 16, 15],  # E
    [5, 8, 9, 10],  # F
    [6, 1, 2, 8],  # G
    [7, 8, 9, 17],  # H
    [8, 7, 8, 15],  # I
    [9, 1, 7, 8],  # J
    [10, 1, 9, 10],  # K
    [11, 1, 2, 9],  # L
    [12, 8, 9, 7],  # M
    [13, 8, 9, 16],  # N
    [14, 8, 15, 16],  # O
]

start_time = time()

number_placed = 0
iterations = 0
best_solution = []
best_solution_loc = 0


class HexominoBoard(Board):
    def __init__(self, width, length, debug, margin=True):
        super().__init__(
            width, length, hexominos, margin=margin, unique=True, debug=debug
        )

    def test(self, loc, pattern):
        for shape_loc in self.shapes[pattern][1:]:
            if self.board[loc + shape_loc] is not None:
                return 0
        return 1


class HeptominoBoard(Board):
    def __init__(self, width, length, debug):
        super().__init__(width, length, heptominos, unique=True, debug=debug)


class TetronimoBoard(Board):
    def __init__(self, width, length):
        super().__init__(width, length, tetrominos, unique=False)


def constraint_solution(board_object):
    problem = Problem()
    # heptominos
    number_of_pieces = 76
    width = 28
    length = 19
    # board locations
    variables = [f"row{row}col{col}" for row in range(width) for col in range(length)]
    # pieces
    values = [
        f"piece{piece}part{part}"
        for part in range(7)
        for piece in range(number_of_pieces)
    ]
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
                        if (location + offset) >= len(board):  # piece is off the board
                            return 0

                        other_parts.append(
                            board[location + offset]
                            == f"piece{shape_index}part{part + 1}"
                        )
                    if board[location] == f"piece{shape_index}part0" and all(
                        other_parts
                    ):
                        return 1
            return 0

        problem.addConstraint(piece_constraint, (variables))

    return problem.getSolution()


def place_piece(board_object, loc, piece_index):
    if not board_object.test(loc, piece_index):
        piece_index += 1
        return board_object, loc, piece_index

    board_object.place_on_board(loc=loc, piece_index=piece_index)

    next_loc = board_object.findloc()
    if not next_loc:
        output_to_svg(board_object)
        #  print solution
        print(f"solution: {time() - board_object.start_time}")
    else:
        return board_object, next_loc, 0
    #  remove piece
    board_object.remove_piece_from_board(piece_index, loc)
    piece_index += 1
    return board_object, loc, piece_index


# place a piece in the board; recursive
def place(board_object, nsols):
    piece_index = 3

    global number_placed
    global iterations
    global best_solution_loc
    global best_solution

    iterations += 1
    while (loc := board_object.findloc()) and piece_index < len(board_object.shapes):
        if not board_object.test(loc, piece_index):
            piece_index += 1
            continue
        if iterations % 100000 == 0:
            print(f"{iterations=}")

        board_object.place_on_board(loc=loc, piece_index=piece_index)

        if board_object.debug:
            print(
                f"placing piece [{piece_index}] at square {loc}"
            )  # if the entire board is occupied
            board_object.print_board()
            print(loc, board_object.solution)
        if not board_object.findloc():
            output_to_svg(board_object)
            #  print solution
            if board_object.debug:
                print(f"solution: {time()-board_object.start_time}")
                board_object.print_board()
        else:
            nsols = place(board_object, nsols)
        if best_solution_loc < len(board_object.solution):
            best_solution = board_object.solution
            best_solution_loc = len(board_object.solution)
            board_object.print_board()
            print(
                f"new best solution! {best_solution_loc}  {piece_index=} {iterations=}"
            )

        #  remove piece
        board_object.remove_piece_from_board(piece_index, loc)
        piece_index += 1


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate rectangular packings of a single polyomino shape."
    )
    parser.add_argument(
        "-c", dest="countflag", action="store_true", help="print number of solutions"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="debug",
        action="store_true",
        help="print debugging info",
    )
    parser.add_argument(
        "--csp", dest="use_csp", action="store_true", help="save solution as svg"
    )
    parser.add_argument(
        "--multiprocess",
        dest="use_multi",
        action="store_true",
        help="run multi processes",
    )
    parser.add_argument(
        "--from-string",
        dest="from_string",
        type=str,
        default="",
        help="run multi processes",
    )

    args = parser.parse_args()
    """
    width = 24
    length = 23
    _board = HexominoBoard(width, length, args.debug)
    """
    if args.from_string:
        _board = Board.from_str(
            args.from_string.split(",")[2],
            int(args.from_string.split(",")[0]),
            int(args.from_string.split(",")[1]),
            tetrominos,
        )
        _board.name="tetrominos"
        output_to_svg(_board)
        sys.exit()
    width = 26
    length = 21
    _board = HeptominoBoard(width, length, args.debug)

    rebuild_shapes(_board, margin=not args.use_csp)
    if args.use_csp:
        print(constraint_solution(_board))
    elif args.use_multi:
        # solutions that have already been evaluated
        evaluated = set()
        # initial set - all pieces at loc 0
        start_loc = _board.findloc()
        to_evaluate = [
            (deepcopy(_board), start_loc, piece_index)
            for piece_index in range(len(_board.shapes))
        ]
        num_processes = 4
        pool = Pool(processes=num_processes)
        while to_evaluate:
            eval_set = []
            for _ in range(num_processes):
                if to_evaluate:
                    eval_set.append(to_evaluate.pop())
            multiple_results = []
            for eval_args in eval_set:
                board_hash = eval_args[0].hash(eval_args[2])
                evaluated.add(board_hash)
                multiple_results.append(pool.apply_async(place_piece, eval_args))
            for res in multiple_results:
                result = res.get(timeout=60)
                next_solution_hash = result[0].hash((result[2]))
                if next_solution_hash in evaluated:
                    continue
                if result[2] >= len(result[0].shapes):
                    continue
                if result[2] == 0:
                    to_evaluate += [
                        (deepcopy(result[0]), result[1], piece_index)
                        for piece_index in range(len(result[0].shapes))
                    ]
                    continue
                to_evaluate.append(result)
    else:
        place(_board, nsols=1)
    _board.print_board()

    print("done!")
