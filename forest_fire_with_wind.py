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
    config.num_generations = 800
    # STATES
    # 0: chaparral (set as background)
    # 1: fire
    # 2: burned area
    # 3: dense forest
    # 4: lake
    # 5: canyon
    # 6: town
    # 7: fire breaks
    config.states = (0,1,2,3,4,5,6,7)
    #terrain = (ignition_time, burn_time)
    #chaparral = (2,43);
    #canyon = (1,2);
    #dense_forest = (6,403); #burns for month (approximated to 28 days)
    #lake = (0,0);
    #town
    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(1,1,0),(1,0.2,0.2), (0,0,0), (0,0.5,0), (0,1,1), (0.5,0.5,0.5),(0,0.1,1),(0.4,0.4,0.2)]
    config.grid_dims = (200, 200)

    config.initial_grid = np.full((200,200), 0)
    """for x in range (15,19):
     for y in range (160,200):
      config.initial_grid[y][x] = 4"""
    for x in range (70,120):
     for y in range (120,160):
      config.initial_grid[y][x] = 3
    for x in range (20,70):
     for y in range (40,70):
      config.initial_grid[y][x] = 4
    for x in range (140,160):
     for y in range (15,140):
      config.initial_grid[y][x] = 5
    for x in range (0,15):
     for y in range (190,200):
      config.initial_grid[y][x] = 6
   #set the fire to automatically starting
    #config.initial_grid[0][0] = 1
    config.initial_grid[0][199] = 1
    #When dealing with south winds
    #config.initial_grid[1][0] = 1
    #config.initial_grid[1][199] = 1
    #config.initial_grid[2][0] = 1
    #config.initial_grid[2][199] = 1

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
def transition_function(grid, neighbourstates, neighbourcounts, chap_ignition, forest_ignition, fuel_reserves, wind_fire):
    """Function to apply the transition rules
    and return the new grid"""

    # off-fire = state == 0/3/4/5 (depends on terrain), on-fire = state == 1, burned = state == 2
    # create boolean arrays for each terrain type (that can catch fire)
    chaparral = (grid == 0)
    forest = (grid==3)
    canyon = (grid==5)

    #Update fuel reserve for uncommon types of terrain (saves on having multiple fuel arrays)
    fuel_reserves[canyon] = 2
    fuel_reserves[forest] = 403

    NW, N, NE, W, E, SW, S, SE = neighbourstates
    burning = neighbourcounts[1]
    four_neighbours = (neighbourcounts[1] >= 4)
    one_neighbour = ((neighbourcounts[1] > 0) & (neighbourcounts[1] < 4))
    no_neighbours = (neighbourcounts[1] == 0)
    #north winds
    directions = (N == 1)
    #east winds
    #directions = (E == 1)
    #south winds
    #directions = (S == 1)
    #west winds
    #directions = (W == 1)
    wind_fire[four_neighbours] += 0.6
    wind_fire[directions] += 0.45
    wind_fire[one_neighbour] += 0.30



    #different wind_fire variables to alow us to consider wind coming from other directions
    # if current state is off_fire (0), and it has neighbours upwind or 2 iterations of down wind
    # then it changes to on-fire (1).
    chap_with_wind = chaparral & (wind_fire > 0.70)
    chap_ignition[chap_with_wind] -= 1
    chap_to_fire = (chap_ignition<=0)

    #sets canyon on fire once burning neighbour
    canyon_to_fire = canyon & (one_neighbour)

    #will tick down forest and then set on fire so not instant ignition
    forest_with_wind = forest & (wind_fire > 0.85)
    forest_ignition[forest_with_wind] -= 1
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
    forest_ignition.fill(6)
    wind_fire = np.zeros(config.grid_dims)
    wind_fire.fill(0)

    #sets default fuel for chaparral and other states can be adjusted later
    fuel_reserves = np.zeros(config.grid_dims)
    fuel_reserves.fill(43)

    # Create grid object using parameters from config + transition function
    #added forest_ignition and fuel_reserves as arguements
    grid = Grid2D(config, (transition_function, chap_ignition, forest_ignition, fuel_reserves, wind_fire))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
