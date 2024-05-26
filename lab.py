"""
6.101 Lab 7:
Six Double-Oh Mines
"""
#!/usr/bin/env python3

import typing
import doctest

import time
# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION

def get_neighbors_2d(nrows, ncolumns, row, col):
    """
    gets coordinates (row, col) of neighbors of a given position
    omits out of range neighbors
    """
    for r in range(row-1, row+2):
        for c in range(col-1, col+2):
            if 0 <= r < nrows and 0 <= c < ncolumns:
                if r != row or c != col:
                    yield (r, c)


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing',
    ...         'num_hidden': 4}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing',
    ...         'num_hidden': 4}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))



def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    out = ""
    locations = render_2d_locations(game, all_visible)
    for row in locations[0:-1]:
        # all rows except the last
        out += "".join(row) + "\n"
    out += "".join(locations[-1]) # last row
    return out


# N-D IMPLEMENTATION

def get_neighbors_nd(dimensions, pos):
    """
    returns the neighbors of the given position on an nd board
    omits out of range neighbors
    """
    neighbors = set()
    directions = [-1, 0, 1]
    if len(dimensions) == 1:
        for d in directions:
            new_pos = pos[0] + d
            if new_pos in range(dimensions[0]):
                neighbors.add((new_pos,))
    else:
        # first_positions = {(pos[0] + d,) for d in directions}
        first_positions = get_neighbors_nd((dimensions[0],), (pos[0],))
        rest_positions = get_neighbors_nd(dimensions[1:], pos[1:])
        # print(f"{first_positions=}, {rest_positions=}")
        for pos_1 in first_positions:
            for pos_rest in rest_positions:
                neighbors.add(pos_1 + pos_rest)
    return neighbors


def set_object_nd(board, pos, obj):
    """
    sets the object at the given position on the board
    """
    if len(pos) == 1:
        board[pos[0]] = obj
    else:
        set_object_nd(board[pos[0]], pos[1:], obj)


def get_info_nd(board, pos):
    """
    gets the object at the given position on the board
    """
    if len(pos) == 1:
        return board[pos[0]]
    return get_info_nd(board[pos[0]], pos[1:])


def new_board(dimensions, item):
    """
    initializes a board with the given dimensions and fill with "item"
    """
    if len(dimensions) == 1:
        out = [item] * dimensions[0]
    else:
        out = []
        for _ in range(dimensions[0]):
            out.append(new_board(dimensions[1:], item))
    return out

def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    # generate a new board and fill locations with 0
    board, visible = new_board(dimensions, 0), new_board(dimensions, False)

    # set mines and update the counts at adjacent locations
    for mine in mines:
        set_object_nd(board, mine, ".")
        for adj_pos in get_neighbors_nd(dimensions, mine):
            neighbor = get_info_nd(board, adj_pos)
            if neighbor != ".":
                set_object_nd(board, adj_pos, neighbor + 1)

    return {
        "dimensions": dimensions,
        "board": board,
        "visible": visible,
        "state": "ongoing"
    }


def count_objects(board, dimensions, obj):
    """
    counts the total number of a given object in a board
    """
    count = 0
    if len(dimensions) == 1:
        for item in board:
            if item == obj:
                count += 1
    else:
        for i in range(dimensions[0]):
            count += count_objects(board[i], dimensions[1:], obj)
    return count


def victory_check_nd(game):
    """
    Returns True if the game has been won, False otherwise
    """
    if not game.get("num_hidden"):
        num_hidden = count_objects(game["visible"], game["dimensions"], False)
        num_mines = count_objects(game["board"], game["dimensions"], ".")
        game["num_hidden"] = num_hidden - num_mines
    else:
        game["num_hidden"] -= 1

    if game["num_hidden"] == 0:
        return True
    return False


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game["state"] != "ongoing" or get_info_nd(game["visible"], coordinates):
        return 0 # no change

    # get the item at the given coordinates
    this_item = get_info_nd(game["board"], coordinates)

    # reveal the current location
    set_object_nd(game["visible"], coordinates, True)

    # if a mine is revealed, change the state to "defeat"
    if this_item == ".":
        game["state"] = "defeat"
        return 1

    # check for victory
    if victory_check_nd(game):
        game["state"] = "victory"
        return 1

    # if any neighboring squares are mines, only reveal the current square
    if this_item != 0:
        return 1

    # otherwise, recursively reveal neighbors
    neighbors = get_neighbors_nd(game["dimensions"], coordinates)
    squares_revealed = 1
    for adj_pos in neighbors:
        squares_revealed += dig_nd(game, adj_pos)

    return squares_revealed


def render(board, visible, dimensions, all_visible=False):
    """
    Recursively renders an nd board
    """
    out = []
    if len(dimensions) == 1: # base case
        if all_visible: # show all locations on the board
            for val in board:
                out.append(" " if val == 0 else str(val))
        else: # replace hidden locations with "_"
            for val, is_visible in zip(board, visible):
                if is_visible:
                    out.append(" " if val == 0 else str(val))
                else:
                    out.append("_")
    else: # recursive case
        for i in range(dimensions[0]):
            out.append(render(board[i], visible[i], dimensions[1:], all_visible))
    return out


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    return render(game["board"], game["visible"], game["dimensions"], all_visible)




if __name__ == "__main__":
    print("-----------------------------------------------------------------------------------------")
    print("Welcome to Mines!")
    print("\nTo play the 2D version, run server_2d.py")
    print("To play ND HyperMines, run server_nd.py")
    print("\nAfter running your chosen server file, please navigate to http://localhost:6101 in your browser to start the game. Enjoy!")
    print("-----------------------------------------------------------------------------------------")
