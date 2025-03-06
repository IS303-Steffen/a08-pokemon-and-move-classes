#### Assignment 9
# Pokémon and Move Classes

The purpose of this assignment is to practice the syntax of classes and creating objects. This is an individual assignment, but it is preparation for your next project, “P1 – Pokémon Battle”, which is a group project.

You will create 3 `Pokemon` objects, and 9 `Move` objects. If you’ve never heard of or played Pokémon, they are popular fictional creatures that learn “moves” which are attacks or abilities that they perform. Pokémon and moves have elemental types, like “Fire”, “Water”, “Grass”, and “Normal”. 

In this assignment you will just create the objects (with their attributes and methods), and practice putting the objects in lists and accessing their attributes and methods. However, during the group project, you will have the objects interact with each other in a “battle”. You don’t have to have any prior knowledge of Pokémon to do this assignment and the upcoming project, but it may help you to <a href="https://www.youtube.com/clip/Ugkx_pVqGoZu4Vx3ux5fjGtyF28lin6_e-qW">watch this clip</a> for an idea of what Pokémon interactions are like: 

You will put your code in the `a09_pokemon_and_move_classes.py` file. Do not edit or delete any other files.

## Libraries Required:
- `random`

## Classes Required:
You can write the class names, instance variables, and method names in PascalCase, camelCase, or snake_case (though PascalCase is the convention for class names in Python). The automated tests should recognize any of those choices. I write class names in PascalCase, and method/variable names in snake_case as is the convention for Python.

I list out all the classes here for reference. However, I recommend you just start with the "Logical Flow" section of the instructions and create/update your classes as you go, rather than trying to write all your classes before any of the other logic. But do whatever feels natural to you.


#### Move
- Instance Variables:
  - `move_name` (string)
    - the name of the move
  - `elemental_type` (string)
    - will have value of either “Water”, “Fire”,  “Grass”, or “Normal”
  - `low_attack_points` (int)
    - the lowest number of points that can be generated for the move
  - `high_attack_points` (int)
    - the highest number of points that can be generated for the move
- Methods:
  - `__init__`
    - The constructor / initializer!
  - `get_info`
    - returns a string with the move_name, elemental_type, and the low_attack_points and high_attack_points.
  - `generate_attack_value`
    - returns an int of a randomly generated number between the low_attack_points, and the high_attack_points of the move.

#### Pokemon
>Note: name your class `Pokemon` without an accent, instead of `Pokémon`. Sorry to the purists :(
- Instance Variables:
  - `name` (string)
    - the Pokemon’s name
  - `elemental_type` (string)
    - will have value of either “Water”, “Fire”, or “Grass”
  - `hit_points` (integer)
    - represents the health of the pokemon
- Methods:
  - `__init__`
    - The constructor / initializer!
  - `get_info`
    - returns a string with the name, elemental_type and hit_points
  - `heal`
    - adds 15 hit points to `hit_points` and prints out a message with the new number of hit_points. Shouldn't return anything.


## Logical Flow:
Note, this program won't store any user input. You'll hardcode all of the values provided in the instructions. This takes some time to write out, but will make it much quicker to run (instead of typing in inputs each run), and you will reuse all the objects you type out in the upcoming project.

### Part 1: Creating Move objects

Moves represent actions that a Pokémon can take. They have a name (like “Tackle”), an elemental type (like “Normal” or “Fire”) that describes the move, as well as a range of damage values that the move can do. For example, a move might do somewhere between 5 and 15 points of damage, so you need to store lower and upper bounds for that.

- Create a Move class
  - Create the constructor with parameters for `self`, `move_name`, `elemental_type`, `low_attack_points`, and `high_attack_points`.
  - Create a method called `get_info` with just `self` as a parameter. It returns a string that includes all of its variables.
    - `<move name> (Type: <move elemental type>): <low attack points> to <high attack points> Attack Points`
    - For example, for the move Tackle, that is a Normal type with attack points between 5 and 20, the returned string should look like:
      - `Tackle (Type: Normal): 5 to 20`
  - Create a method called `generate_attack_value`, with just `self` as a parameter. It will generate a random number between the `low_attack_points` and `high_attack_points` (inclusive on both ends) and return that value.
- Create 9 `Move` objects.
  - Call the constructor 9 times to store 9 different `Move` objects in 9 different variables. The values that you can pass into the constructor are given in each row in the table below. The Move Name and Elemental Type must be as shown in the table, but you can put different values for the attack points if you'd like:

  - | Move Name      | Elemental Type | Low Attack Points | High Attack Points |
    |----------------|----------------|-------------------|--------------------|
    | Tackle         | Normal         | 5                 | 20                 |
    | Quick Attack   | Normal         | 6                 | 25                 |
    | Slash          | Normal         | 10                | 30                 |
    | Flamethrower   | Fire           | 5                 | 30                 |
    | Ember          | Fire           | 10                | 20                 |
    | Water Gun      | Water          | 5                 | 15                 |
    | Hydro Pump     | Water          | 20                | 25                 |
    | Vine Whip      | Grass          | 10                | 25                 |
    | Solar Beam     | Grass          | 18                | 27                 |

- Create a list that stores each of the 9 objects in it.
- Do a for loop that runs 3 times, and in each iteration, do the following:
  - Randomly select a `Move` object from the list you created
  - Print out the result of the `get_info` method of the randomly selected object.
  - Print out `Generated attack value: ` and then the returned value from running the `generate_attack_value` method on the randomly selected object.
  - Then delete the move from the list of moves. This ensures that you won't randomly select the same move twice. If you randomly select the same move twice, the automated tests won't pass.
- After finishing the loop, to add a pause in your program, add this line of code:
  - `input(“Press enter to continue...)`
  - The above code doesn’t store anything, but it makes your program pause until you press enter (or return) on your keyboard. We’ll use the above code more in the future project, but put it here just to get familiar with it. 

### Part 2: Creating Pokémon objects

`Pokemon` objects represent a fictional creature that has a name, an elemental type, and hit points, which is basically a health indicator. A `Pokemon` faints when its hit points reach 0.

- Create a `Pokemon` class
> Note: conventionally, any classes you write go at the top of the Python file. You can put the `Pokemon` class below the other code you wrote to make `Move` objects (and it will still work) but that isn’t how most Python code is usually organized. You can do whatever you want though.
  - Create the constructor with parameters for `self`, `name`, `elemental_type`, and `hit_points`
  - Create a method called `get_info` that returns the `name`, `elemental_type`, and `hit_points` in a string.
    - `<Pokemon name> - Type: <elemental type> - Hit Points: <hit points>`
  - For example for a water type pokemon called Squirtle with 65 hit points the returned string would look like:
    - Squirtle – Type: Water – Hit Points: 65`
  - Create a method called `heal` with just `self` as a parameter. It increases the current value of `hit_points` by 15 and prints out a message with the Pokémon’s `name` and what their new value of `hit_points` are. It should print out the message directly in the method, and not return anything.
    - For example, if Squirtle had 65 hit points and the heal method was run on it, it would print:
      - `Squirtle has been healed to 80 hit points.`
- Create 3 `Pokemon` objects
  - Call the constructor 3 times to create 3 different `Pokemon` objects stored in 3 different variables. The values that you can pass into the constructor are given in each row in the table below:

  - | Name        | Elemental Type | Hit Points |
    |-------------|----------------|------------|
    | Bulbasaur   | Grass          | 60         |
    | Charmander  | Fire           | 55         |
    | Squirtle    | Water          | 65         |

- Call the `get_info` method on the object storing the Charmander Pokémon and print out the result
- Then call the heal method on the same Charmander object
- Then call the get_info method on the same Charmander object again and print out the result (you should see that the hit_points have increased)
- Put the 3 `Pokemon` objects into a list
- Loop through the list and print out the result of `get_info` on each `Pokemon` object in the list.

## Example Output:

Note the specific moves that print out will be different each time the program is run since you are randomly selecting them from a list:

```
Flamethrower (Type: Fire): 5 to 30 Attack Points
Generated attack value: 21
Tackle (Type: Normal): 5 to 20 Attack Points
Generated attack value: 14
Vine Whip (Type: Grass): 10 to 25 Attack Points
Generated attack value: 11
Press enter to continue...
Charmander - Type: Fire - Hit Points: 55
Charmander has been healed to 70 hit points.
Charmander - Type: Fire - Hit Points: 70
Bulbasaur - Type: Grass - Hit Points: 60
Charmander - Type: Fire - Hit Points: 70
Squirtle - Type: Water - Hit Points: 65
```

## Grading Rubric
See the Rubric.md file. Remember to right click and select "Open Preview" to see it formatted so it is readable.

