import lib.stddraw as stddraw  # used for displaying the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import lib.color as color  # used for coloring the game grid

# A class for modeling the game grid
class GameGrid:
   # A constructor for creating the game grid based on the given arguments
   def __init__(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create a tile matrix to store the tiles locked on the game grid
      self.tile_matrix = np.full((grid_h, grid_w), None)
      # create the tetromino that is currently being moved on the game grid
      self.current_tetromino = None
      # the game_over flag shows whether the game is over or not
      self.game_over = False
      # set the color used for the empty grid cells
      self.empty_cell_color = color.EMPTY_CELL
      # set the colors used for the grid lines and the grid boundaries
      self.line_color = color.LINE_COLOR
      self.boundary_color = color.BOUNDRY_COLOR
      # thickness values used for the grid lines and the grid boundaries
      self.line_thickness = 0.006
      self.box_thickness = 0.010
      # score counter
      self.score = 0

   # A method for displaying the game grid
   def display(self):
      # clear the background to empty_cell_color
      stddraw.clear(self.empty_cell_color)
      # draw the game grid
      self.draw_grid()
      # draw the current/active tetromino if it is not None
      # (the case when the game grid is updated)
      if self.current_tetromino is not None:
         self.current_tetromino.draw()
      # draw a box around the game grid
      self.draw_boundaries()
      #! Score for testing purposes for merge
      stddraw.setFontSize(20)
      stddraw.setPenColor(color.BLACK)
      stddraw.text(0.8, self.grid_height - 1, f"SCORE: {self.score}")
      # show the resulting drawing with a pause duration = 250 ms
      stddraw.show(250)

   # A method for drawing the cells and the lines of the game grid
   def draw_grid(self):
      # for each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # if the current grid cell is occupied by a tile
            if self.tile_matrix[row][col] is not None:
               # draw this tile
               self.tile_matrix[row][col].draw(Point(col, row))
      # draw the inner lines of the game grid
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      # x and y ranges for the game grid
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method for drawing the boundaries around the game grid
   def draw_boundaries(self):
      # draw a bounding box around the game grid as a rectangle
      stddraw.setPenColor(self.boundary_color)  # using boundary_color
      # set the pen radius as box_thickness (half of this thickness is visible
      # for the bounding box as its lines lie on the boundaries of the canvas)
      stddraw.setPenRadius(self.box_thickness)
      # the coordinates of the bottom left corner of the game grid
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method used checking whether the grid cell with the given row and column
   # indexes is occupied by a tile or not (i.e., empty)
   def is_occupied(self, row, col):
      # considering the newly entered tetrominoes to the game grid that may
      # have tiles with position.y >= grid_height
      if not self.is_inside(row, col):
         return False  # the cell is not occupied as it is outside the grid
      # the cell is occupied by a tile if it is not None
      return self.tile_matrix[row][col] is not None

   # A method for checking whether the cell with the given row and col indexes
   # is inside the game grid or not
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height:
         return False
      if col < 0 or col >= self.grid_width:
         return False
      return True
   
   # Mergin tiles
   def merge_tiles(self):
      gained = 0
      H, W = self.grid_height, self.grid_width
      for col in range(W):
         row = 0
         while row < H - 1:
            bot = self.tile_matrix[row][col]
            top = self.tile_matrix[row+1][col]
            if bot and top and bot.number == top.number:
               bot.number *= 2
               bot.update_color()
               gained += bot.number
               # remove the above tile and collapse
               self.tile_matrix[row+1][col] = None
               for rr in range(row+2, H):
                  self.tile_matrix[rr-1][col] = self.tile_matrix[rr][col]
                  self.tile_matrix[H-1][col] = None
            else:
               row += 1
      self.score += gained
      return gained

   # Clearing full rows
   def clear_full_rows(self):
      # remove any completely filled rows, shift above down
      gained = 0
      H, W = self.grid_height, self.grid_width
      new_rows = []
      for r in range(H):
         row = self.tile_matrix[r]
         if all(cell is not None for cell in row):
            for cell in row:
               gained += cell.number
         else:
            new_rows.append(row)
      # add empty rows at top
      for _ in range(H - len(new_rows)):
         new_rows.insert(0, [None]*W)
      self.tile_matrix = np.array(new_rows)
      self.score += gained
      return gained

   # Handling free tiles (deleting free tiles)
   def handle_free_tiles(self):
      H, W = self.grid_height, self.grid_width
      # flood‑fill from bottom row
      visited = [[False]*W for _ in range(H)]
      stack = []
      for c in range(W):
         if self.tile_matrix[0][c]:
            visited[0][c] = True
            stack.append((0, c))
         while stack:
            r, c = stack.pop()
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
               rr, cc = r+dr, c+dc
               if 0 <= rr < H and 0 <= cc < W and not visited[rr][cc] and self.tile_matrix[rr][cc]:
                  visited[rr][cc] = True
                  stack.append((rr, cc))
      # remove unvisited (free) tiles
      gained = 0
      for r in range(H):
         for c in range(W):
            if self.tile_matrix[r][c] and not visited[r][c]:
               gained += self.tile_matrix[r][c].number
               self.tile_matrix[r][c] = None
      self.score += gained
      return gained

   # A method that locks the tiles of a landed tetromino on the grid checking
   # if the game is over due to having any tile above the topmost grid row.
   # (This method returns True when the game is over and False otherwise.)
   def update_grid(self, tiles_to_lock, blc_position):
      # necessary for the display method to stop displaying the tetromino
      self.current_tetromino = None
      # lock the tiles of the current tetromino (tiles_to_lock) on the grid
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            # place each tile (occupied cell) onto the game grid
            if tiles_to_lock[row][col] is not None:
               # compute the position of the tile on the game grid
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.tile_matrix[pos.y][pos.x] = tiles_to_lock[row][col]
               # the game is over if any placed tile is above the game grid
               else:
                  self.game_over = True
      # return the value of the game_over flag
      return self.game_over
