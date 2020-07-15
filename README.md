# Snake Project

This project uses object oriented programming in python with the Pygame module in order to build a Snake game which can be played by humans or by various algorithms I have implemented. For more information, visit INSERT_LINK_HERE

### Algorithm Snakes

The **Algorithm_Snakes.py** file allows for 3 different versions of the snake game to be played. The following options are available and can be accessed by changing the `algorithm_type` attribute in `main()` to each respective value:
1. The human-controlled snake allows for a human player to play a standard snake game using the arrow keys on the keyboard. The goal is to each as many apples as possible without dying by running into the walls or your own snake.
2. The shortest-path snake calculates only one move at a time, simply moving in the direction that will take it fastest towards the apple and ignoring both the walls and its own body. As a result, this algorithm is fast but often results in quick death of the snake.
3. The BFS snake will perform a Breadth First Search for a path from its current location to the apple. This will always generate the shortest currently possible path from the snake's location to the apple. If no path is found, the snake continues moving in its current direction. Since this algorithm checks all possible paths, it runs much slower, but snakes live much longer.

### NEAT Snakes

The **NEAT_Snakes.py** file uses the NEAT-Python module in order to generate a genetic evolving Neural Network for snakes to learn how to play the Snake game. The snakes are given the following two sets of information:
1. A list containing whether the snake seen a wall or itself in the tiles to its immediate left, forward, or right tiles. This information allows the snake to determine the directions in which it can safely move.
2. A list containing whether the snake can see an apple in the forward, left, or right directions relative to its current head position. This information allows the snake to determine how food can be reached.
Each snake is then incentivized to live as long as possible, move in the direction of the food, and eat food. 

### Requirements

The required modules across both files are:
1. `pygame`
2. `neat-python`
3. `math`
4. `random`
5. `sys`
6. `os`
