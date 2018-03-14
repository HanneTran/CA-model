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
    #chaparral = (288,1);
    #canyon = (144,0.5);
    #dense_forest = (8064,3); #burns for 28 days
    #lake = (0,0); #possible glitch - if system thinks instantaneously on fire and spread to adjacents
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(1,1,0),(1,0.2,0.2), (0,0,0), (0,0.5,0), (0,1,1), (0.5,0.5,0.5)]
    config.grid_dims = (200, 200)
    ##Where i started
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
def transition_function(grid, neighbourstates, neighbourcounts, forest_ignition, fuel_reserves):
    """Function to apply the transition rules
    and return the new grid"""
    # off-fire = state == 0, on-fire = state == 1, burned = state == 2
    # create boolean array for off-fire and on-fire rules
    # if 8 off-fire neighbours and is off-fire -> off-fire
    off_fire_cells = (grid == 0) # cells currently not on fire
    eight_off_neighbours = (neighbourcounts[0] == 8)
    stays_off_fire = off_fire_cells & eight_off_neighbours
    forest_ignition1 = (grid == 3) & (neighbourcounts[1] > 0)
    forest_ignition2 = forest_ignition1 & (neighbourcounts[1] > 0)
    forest_ignition3 = forest_ignition2 & (neighbourcounts[1] > 0)


    forest = (grid==3)
    canyon = (grid==5)

    fuel_reserves[canyon] = 2
    fuel_reserves[forest] = 10

    NW, N, NE, W, E, SW, S, SE = neighbourstates
    wind_fire = (N == 1)|(E == 1) & (SE == 1) | (W == 1) & (SW == 1)
    # if current state is off_fire (0), and it has one or more on-fire neighbours,
    # then it changes to on-fire (1).
    on_fire_neighbour = (neighbourcounts[1] > 0)
    to_on_fire = off_fire_cells & on_fire_neighbour & wind_fire

    # currently state on-fire
    current_fire = (grid == 1)
    """decaygrid[current_fire] -= 1
    decayed_to_zero = (decaygrid == 0)
    grid[decayed_to_zero] = 0 """

    """
    previous code to switch cells from on fire to burnt

    burned = (grid == 2) #black cells
    eight_burn = (neighbourcounts[1] > 6)
    to_burned = current_fire & eight_burn # if current cell is on-fire and has 8 on-fire neighbours
    burned_neighbour = (neighbourcounts[2] > 0)

    one_or_more_neighbour_to_burn = (neighbourcounts[1] > 0) & burned_neighbour
    to_burned2 = current_fire & one_or_more_neighbour_to_burn
    """

    #check how much fuel cell has left and burns out once none left
    fuel_reserves[current_fire] -= 1
    burn_out = (fuel_reserves == 0)

    #sets canyon on fire once burning neighbour
    canyon_to_fire = canyon & (neighbourcounts[1]>0)
    #lower function needs to be added to ignite two canyon cells in one tick
    #canyon_collateral =

    #will tick down forest and then set on fire so not instant ignition
    forest_fire = (neighbourcounts[1] > 0)
    catching_fire = forest & forest_fire
    forest_ignition[catching_fire] -= 1
    caught_fire = (forest_ignition==0)

    # Set all cells to 0 (off-fire)
    #grid[:, :] = 0
    # Set cells to 0 where cell is off-fire
    grid[stays_off_fire] = 0
    # Set cells to 1 where cell is on fire
    grid[to_on_fire | current_fire | forest_ignition3] = 1
    # Set cells to 2 where cell is burned
    #outdated: grid[to_burned | to_burned2] = 2
    grid[burn_out] = 2
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])
    #sets default num of ticks for forest to ignite
    forest_ignition = np.zeros(config.grid_dims)
    forest_ignition.fill(3)

    #sets default fuel for chaparral and other states can be adjusted later
    fuel_reserves = np.zeros(config.grid_dims)
    fuel_reserves.fill(5)

    # Create grid object using parameters from config + transition function
    #added forest_ignition and fuel_reserves as arguements
    grid = Grid2D(config, (transition_function, forest_ignition, fuel_reserves))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
