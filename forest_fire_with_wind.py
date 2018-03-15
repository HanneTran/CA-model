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
    fuel_reserves[canyon] = 2
    fuel_reserves[forest] = 10

    NW, N, NE, W, E, SW, S, SE = neighbourstates
    wind_fire = (N == 1)|(E == 1) & (NE == 1) | (W == 1) & (NW == 1)
    off_wind = (SE==1)|(S==1)|(SW==1)

    #different wind_fire variables to alow us to consider wind coming from other directions
    # if current state is off_fire (0), and it has neighbours upwind or 2 iterations of down wind
    # then it changes to on-fire (1).
    chap_with_wind = chaparral & wind_fire
    chap_no_wind = chaparral & off_wind
    chap_ignition[chap_with_wind] -= 2
    chap_ignition[chap_no_wind] -= 1
    chap_to_fire = (chap_ignition<=1)

    #sets canyon on fire once burning neighbour
    canyon_to_fire = canyon & (wind_fire|off_wind)

    #will tick down forest and then set on fire so not instant ignition
    forest_with_wind = forest & wind_fire
    forest_ignition[forest_with_wind] -= 2
    forest_no_wind = forest & off_wind
    forest_ignition[forest_no_wind] -= 1
    forest_to_fire = (forest_ignition<=0)


    #check how much fuel cell has left and burns out once none left
    current_fire = (grid == 1)
    fuel_reserves[current_fire] -= 1
    burn_out = (fuel_reserves == 0)

    # Set cells to 1 when cell catches fire
    grid[chap_to_fire | canyon_to_fire | forest_to_fire] = 1
    # Set cells to 2 where cell is burned
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
    forest_ignition.fill(8)

    #sets default fuel for chaparral and other states can be adjusted later
    fuel_reserves = np.zeros(config.grid_dims)
    fuel_reserves.fill(10)

    # Create grid object using parameters from config + transition function
    #added forest_ignition and fuel_reserves as arguements
    grid = Grid2D(config, (transition_function, forest_ignition, fuel_reserves, chap_ignition))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
