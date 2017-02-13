import pandas as pd
import os

def similar_games(home_team, opp_team, amount):
	os.chdir("C:\\Users\\Owner\\Desktop\\College 16-17\\FYP\\FYP_python")
	
	data = pd.read_csv("win_percent.csv")
	data = data.set_index('team', drop = False)

	own_value = data['PCT'][opp_team]

	distances = {}
	for index, row in data.iterrows():
		distances[row.team] = abs(row.PCT - own_value)

	similar_opp_teams = sorted(distances, key=distances.get)[0:amount]
	if home_team in similar_opp_teams:
         similar_opp_teams = sorted(distances, key=distances.get)[0:amount + 1]
         similar_opp_teams.remove(home_team)
    
	os.chdir("C:\\Users\\Owner\\Desktop\\College 16-17\\FYP\\FYP_python\\Data")
	files = os.listdir()

	relevant = []
	for file in files:
		if home_team in file:
			for opp in similar_opp_teams:
				if opp in file:
					relevant.append(file)
					break

	return relevant

