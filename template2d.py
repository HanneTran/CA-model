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
    config.grid_dims = (50,50)

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts):
    """Function to apply the transition rules
    and return the new grid"""
    # off-fire = state == 0, on-fire = state == 1, burned = state == 2
    # create boolean array for off-fire and on-fire rules
    # if 8 off-fire neighbours and is off-fire -> off-fire
    off_fire_cells = (grid == 0) # cells currently not on fire
    eight_off_neighbours = (neighbourcounts[0] == 8)
    stays_off_fire = off_fire_cells & eight_off_neighbours

    # if current state is off_fire (0), and it has one or more on-fire neighbours,
    # then it changes to on-fire (1).
    on_fire_neighbour = (neighbourcounts[1] > 0)
    to_on_fire = off_fire_cells & on_fire_neighbour

    # currently state on-fire
    current_fire = (grid == 1)
    """decaygrid[current_fire] -= 1

    decayed_to_zero = (decaygrid == 0)
    grid[decayed_to_zero] = 0 """

    burned = (grid == 2) #black cells
    eight_burn = (neighbourcounts[1] > 6)
    to_burned = current_fire & eight_burn # if current cell is on-fire and has 8 on-fire neighbours
    burned_neighbour = (neighbourcounts[2] > 0)

    one_or_more_neighbour_to_burn = (neighbourcounts[1] > 0) & burned_neighbour
    to_burned2 = current_fire & one_or_more_neighbour_to_burn

    # Set all cells to 0 (off-fire)
    #grid[:, :] = 0
    # Set cells to 0 where cell is off-fire
    grid[stays_off_fire] = 0
    # Set cells to 1 where cell is on fire
    grid[to_on_fire | current_fire] = 1
    # Set cells to 2 where cell is burned
    grid[to_burned | to_burned2] = 2
    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])
    #decaygrid = np.zeros(config.grid_dims)
    #decaygrid.fill(2)
    # Create grid object using parameters from config + transition function
    grid = Grid2D(config, transition_function)

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
