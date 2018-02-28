#terrain:
#each cell is a quarter kilometer both directions
#terrain = (fuel_remaining {measured in sets of 5 minutes,ignition_time)

#chaparral - ignites in 5 mins - can repeat roughly every 10 years
#denseForest - ignites in 15 mins
#lake - will not ignite - 0 fuel?
#canyon -  ignites 2 in 5 mins

chaparral = (288,1);
canyon = (144,0.5);
dense_forest = (8064,3); #burns for 28 days
lake = (0,0);