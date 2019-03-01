# block_dude

<b>Nate's Block Dude Clone</b><br>
This is a direct clone of the classic TI-84+ Silver Edition class time burner, Block Dude. The goal was to create a simple
computer implementation of the game that allows for speedrunning the game. Currently levels 1 thru 3 are available, more to come.

The game times your run and shows you your final time in seconds when finished.

<b>Controls</b><br>
JIKL on the keyboard functions as the arrow keys:

  J: Left<br>
  L: Right<br>
  K: Pick up/drop block<br>
  I: Jump<br>

<b>Data Structure</b><br>
A short rundown on the organization of the game, for those interested:

The levels are stored as 2-D arrays, parsed at runtime from .bdl files ("Block Dude Level"). The level files 
use a coordinate system based on the blocks of each level, not screen pixels. Each level file contains:<br>


<b>Header:</b> The first line of the file contains three 2-byte data sections (Level ID, width, height), surrounded by the % sign.<br>
The game uses the header to initialize the level storage arrays.<br>
<b>Blocks:</b> Every other line of the file is a new block, containing three 2-byte sections: Block ID, x-coordinate, y-coordinate<br>
<b>Block IDs:</b><br>
0: Air<br>
1: Brick<br>
2: Player<br>
3: Wood (movable block)<br>
4: Door<br>

The rest of the level not specified in the file is filled with air.

Note: The level.bdl file <i>must</i> specify the player's location and the exit door location.
