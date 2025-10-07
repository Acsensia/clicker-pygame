# clicker-pygame
A clicker game developed on Python with the help of Pygame library with the goal of getting a high mark for my uni assignment
- A game centered around clicking on a button on a screen; every click awards the player a certain amount of in-game currency which can then be used to buy certain ‘upgrades’ that can, for example, increase the amount of currency awarded every click, or give the player a certain amount of said currency every second; the end goal of the game is to collect enough currency to unlock all of the ‘special’ locked upgrades, that do not award the player for individually ‘unlocking’ them, but instead give them a certain amount of a special ‘end-game currency’ after all the special upgrades are unlocked; said special currency can be then spent on unlocking additional ‘themes’ for the game’s interface (the default ‘theme’ is centered around grey color, with the ‘unlockable’ ones being lively blue, red and green in color)
- Three levels of difficulty featuring different balancing of in-game currency incomes and expenditures
- Four ‘themes’ for the game’s user interface: one default, three ‘unlockable’ with a special in-game currency
- All the data is serialized (stored locally on disk every time the game is closed and loaded into the game every time it is opened)
- Floating ‘help’ menus that pop up and provide relevant information when the cursor is over a certain area in the game; the menus follow the cursor and dynamically get drawn on the right or the left of the cursor 
depending on its position in relation to the game window’s left and right borders
- Object-oriented approach applied
- An in-game manual present
