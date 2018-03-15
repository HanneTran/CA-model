# Name: NAME
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils
import numpy as np

def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "2D test"
    config.dimensions = 2
    config.num_generations = 500
    # STATES
    # 0: chaparral (set as background)
    # 1: fire
    # 2: burned area
    # 3: dense forest
    # 4: lake
    # 5: canyon
    config.states = (0,1,2,3,4,5)
    #terrain = (burn time, ignition time)
    #chaparral = (288,1);
    #canyon = (144,0.5);
    #dense_forest = (8064,3); #burns for 28 days
    #lake = (0,0);
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(1,1,0),(1,0.2,0.2), (0,0,0), (0,0.5,0), (0,1,1), (0.5,0.5,0.5)]
    config.grid_dims = (200, 200)
    #Where i started
    config.initial_grid = np.full((200,200), 0)
    for x in range (70,120):
     for y in range (120,160):
      config.initial_grid[y][x] = 3
    for x in range (20,70):
     for y in range (40,70):
      config.initial_grid[y][x] = 4
    for x in range (140,160):
     for y in range (15,140):
      config.initial_grid[y][x] = 5
    #set the fire to automatically starting
    config.initial_grid[0][0] = 1
    config.initial_grid[0][199] = 1
    config.wrap = False #should solve the problem with fire starting at all 4 corners

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config

#added forest_ignition and fuel_reserves as arguements
def transition_function(grid, neighbourstates, neighbourcounts, chap_ignition, forest_ignition, fuel_reserves):
    """Function to apply the transition rules
    and return the new grid"""

    # off-fire = state == 0/3/4/5 (depends on terrain), on-fire = state == 1, burned = state == 2
    # create boolean arrays for each terrain type (that can catch fire)
    chaparral = (grid == 0)
    forest = (grid==3)
    canyon = (grid==5)

    #Update fuel reserve for uncommon types of terrain (saves on having multiple fuel arrays)
    fuel_reserves[canyon] = 4
    fuel_reserves[forest] = 20

    # if current state is off_fire (0), and it has one or more on-fire neighbours,
    # then it changes to on-fire (1).
    on_fire_neighbour = (neighbourcounts[1] > 0)

    #sets canyon on fire once burning neighbour
    canyon_to_fire = canyon & (neighbourcounts[1]>0)

    #makes it so that chaparral ignites every second tick that it is neighboured by fire
    chap_to_fire = chaparral & on_fire_neighbour
    chap_ignition[chap_to_fire]-=1

    #will tick down forest and then set on fire so not instant ignition
    forest_catching_fire = forest & on_fire_neighbour
    forest_ignition[forest_catching_fire] -=1

    #checks if any of terrain types have ignited
    caught_fire = (forest_ignition==0)|(chap_ignition==0)|canyon_to_fire

    #check how much fuel cell has left and burns out once none left
    current_fire = (grid == 1)
    fuel_reserves[current_fire] -= 1
    burn_out = (fuel_reserves == 0)

    # Set cells to 1 when cell catches on fire
    grid[caught_fire] = 1
    # Set cells to 2 when cell has burned out
    grid[burn_out] = 2
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    #sets default num of ticks for chaparral and forest to ignite
    chap_ignition = np.zeros(config.grid_dims)
    chap_ignition.fill(2)
    forest_ignition = np.zeros(config.grid_dims)
    forest_ignition.fill(6)

    #sets default fuel for chaparral and other states can be adjusted later
    fuel_reserves = np.zeros(config.grid_dims)
    fuel_reserves.fill(10)

    # Create grid object using parameters from config + transition function
    #added forest_ignition and fuel_reserves as arguements
    grid = Grid2D(config, (transition_function, chap_ignition, forest_ignition, fuel_reserves))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
