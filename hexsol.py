# hexsol.py  - a translation of Karl Dahlke's polyomino packing program to python
from argparse import ArgumentParser
from shapely.ops import cascaded_union
from shapely.geometry import MultiPoint, Polygon as ShapelyPolygon
from svgwrite import Drawing
from svgwrite.path import Path
from svgwrite.shapes import Rect, Circle, Polygon

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


def rebuildShapes():
    for shape in shapes:
        for j in range(1, 5):
            k = shape[j]
            k += 3
            r = int(k/8)
            c = k % 8
            c -= 3
            k = w2*r + c
            shape[j] = k

'''
valid positions for the cross
prevents reflections and rotations
But extra code is needed if the width or height is odd
'''
cross_all = [
[12, 17, 22, 27, 32, 37, 42, 47, 0],
[14, 20, 26, 32, 38, 44, 0],
[10, 16, 17, 23, 24, 30, 31, 37, 38, 0],
[11, 18, 19, 26, 27, 34, 35, 0],
[0],
[13,14,23,0]
]

# flip through width and look for asymmetry
def wflip(board):
    for i in range(0, l2):
        for j in range(0, 3):
            d = board[i*w2+j] - board[i*w2+w1-j]
            if not d:
                continue
            return d > 0

def lflip(board):
    for i in range(1, w2):
        for j in range(1, 8):
            d = board[j*w2+i] - board[(l1-j)*w2+i]
            if not d:
                continue
            return d > 0


'''
Horizontal split, only applicable on the standard board.
The count comes out 16, but the top piece, having the cross on its left,
can be reflected vertically,
while the bottom can be reflected or rotated, thus 8 combinations.
There are really only 2 split solutions as follows.

	EEEIIBJJJJ
	EAEIIBGJHH
	AAALIBGGGH
	CALLLBDFGH
	CKKKLBDFFH
	CCCKKDDDFF

	EEEIIBJJJJ
	EAEIIBGJHH
	AAAKIBGGGH
	CALKKBDFGH
	CLLLKBDFFH
	CCCLKDDDFF

'''

def hsplit(board):
    for i in range(1, w1):
        if board[5*w2+i] == board[6*w2+i]:
            return 0
        return 1


# position the cross, and go
def cross(top, nsols):
    place_on_board(piece_index=0, loc=top)
    nsols = place(nsols=nsols)

    remove_piece_from_board(piece_index=0, loc=top)
    return nsols

def print_board_locations():
    for col in range(1, w1):
        for row in range(1, l1):
            print(str(w2 * row + col)+ ",", end="")
        print('')
    print()


def board_index_to_row_col(board_index):
    row = int(board_index / w2)
    col = board_index % w2
    return row, col


def print_board(board):
    for col in range(1, w1):
        for row in range(1, l1):
            piece_num = board[w2 * row + col]
            if piece_num is not None and piece_num < 0:
                raise ValueError(f"got bad character! {piece_num}")
            _char = chr(piece_num+ord('A')) if piece_num is not None else '-'
            print(_char, end="")
        print('')
    print()

def place_on_board(piece_index, loc):
    piece = shapes[piece_index][0]
    used[piece] = True

    board[loc] = piece
    for i in range(1, 5):
        board[loc + shapes[piece_index][i]] = piece
    solution.append((piece_index, loc))

def remove_piece_from_board(piece_index, loc):
    piece = shapes[piece_index][0]
    used[piece] = False
    board[loc] = None
    for i in range(1, 5):
        board[loc + shapes[piece_index][i]] = None
    sol_piece_index, sol_loc = solution.pop()
    # if we didn't remove a copy of that piece from the solution, something bad happened
    assert sol_piece_index == piece_index
    assert sol_loc == loc

# place a piece in the board; recursive
def place(nsols):
    # find best location
    loc = findloc()
    if not loc:
        return # square that no piece fits into

    piece_index = 1
    while piece_index < len(shapes):
        piece_type = shapes[piece_index][0]
        if not test(loc, piece_index):
            piece_index += 1
            continue

        # some checks for symmetry for odd dimensions
        if loc == 21 and args.width == 3 and piece_type == 8:
            piece_index += 1
            continue

        #  place the piece
        piece = shapes[piece_index][0]


        place_on_board(loc=loc, piece_index=piece_index)
        if args.debug:
            print(f"placing piece {piece}[{piece_index}] at square {loc}, used {sum(used)}")

        if all(used):
            if (wcenter and wflip(board)) or (lcenter and lflip(board)) or (ocenter and board[13] > board[31]):
                #  skip this one
                pass
            else:
                nsols += 1
                if args.svg:
                    output_to_svg(nsols)
                #  print solution
                if args.dispflag:
                    print(f"solution {nsols}: ")
                    print_board(board)
        else:
            nsols = place(nsols)
        #  remove piece
        remove_piece_from_board(piece_index, loc)
        piece_index += 1
    return nsols
#  place


def findloc():
    for i in range(w2+1, w2*l1-1):
        if board[i] is None:
            return i
    raise ValueError("Could not find a location!") #  should never happen

def output_to_svg(sol):
    square_size = 40
    margin = 4
    filename = f"w{args.width}sol{sol}.svg"
    drawing = Drawing(filename)
    colors = [
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod"
    ]
    for piece_index, loc in solution:
        piece_type = shapes[piece_index][0]
        polygons = []
        for square_loc in [0]+ shapes[piece_index][1:]:
            board_loc = loc + square_loc
            row, col = board_index_to_row_col(board_loc)
            rect_points = []
            rect_points.append((square_size * row, square_size * col))
            rect_points.append((square_size * (row + 1), square_size * col))
            rect_points.append((square_size * (row + 1), square_size * (col + 1)))
            rect_points.append((square_size * row, square_size * (col + 1)))
            polygons.append(ShapelyPolygon(rect_points))
        polygon = cascaded_union(polygons)
        piece_points = polygon.buffer(-margin).exterior.coords
        d = f"M {piece_points[0][0]} {piece_points[0][1]} "
        for x,y in piece_points[1:]:
            d += f"L {x} {y} "
        drawing.add(Path(d=d, fill=colors[piece_type % len(colors)]))
    drawing.save(pretty=2)

def test(loc, pattern):
    piece = shapes[pattern][0]
    if used[piece]:
        return 0
    b = board[loc:]
    for shape_loc in shapes[pattern][1:]:
        if b[shape_loc] is not None:
            return 0
    return 1


if __name__ == "__main__":
    parser = ArgumentParser(description='Generate rectangular packings of polyominos.')
    parser.add_argument(dest='width', type=int, help="the board width", default=0)
    parser.add_argument('-d', dest='dispflag', action='store_true', help='print all board solutions')
    parser.add_argument('-c', dest='countflag', action='store_true',
                        help='print number of solutions')
    parser.add_argument('-v', '--verbose', dest='debug', action='store_true',
                        help='print debugging info')
    parser.add_argument('-s', dest='svg', action='store_true', help='save solution as svg')

    args = parser.parse_args()
    l = 8 if args.width == 8 else int(60 / args.width)
    l1 = l + 1
    w1 = args.width + 1
    l2 = l + 2
    w2 = args.width + 2
    board = [None for i in range(0, 5 * 22)]
    used = [False for i in range(0, 12)]
    for i in range(0, w2):
        board[i] = -1
        board[w2*l1+i] = -1

    for i in range(0, l2):
        board[w2*i] = -1
        board[w2*i+w1] = -1

    if args.width == 8:
        board[10*5+5] = 26
        board[10*4+5] = 26
        board[10*4+4] = 26
        board[10*5+4] = 26

    # scale the location of the shapes based on the board width
    rebuildShapes()
    cross_pos = cross_all[args.width-3]

    nsols = 0

    i = 0
    if args.debug:
        print(f"{len(cross_pos)} positions for the + piece")

    solution = []
    # only for debugging
    while cross_pos[i]:
        # args.width = 3 handled in place()
        lcenter = wcenter = ocenter = 0
        if args.width == 4 and i == 5:
            lcenter = 1
        if args.width == 5 and not (i&1):
            wcenter = 1
        if args.width == 8 and i == 2:
            ocenter = 1
        cross(top=cross_pos[i], nsols=nsols)
        i += 1


    if args.countflag:
        print(f"{nsols} solutions\n")


