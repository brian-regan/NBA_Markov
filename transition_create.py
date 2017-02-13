# -*- coding: utf-8 -*-
"""
FYP Basketball Markov Chains Project
"""

import os
import pandas as pd
import numpy as np
import lookup_func
import scipy.stats as stats
#import seaborn as sns
#import matplotlib.pyplot as plt


# Some Functions

def transition_definer(row, colnames):
    row.index = colnames
    team = str(row.team)
    etype = str(row.etype)
    atype = str(row.type)
    result = str(row.result)
    period = row.period
    clock = row.time
    
    
    if((etype == 'shot') & (atype != '3pt')): atype = '2pt'
    if((etype == 'foul') | (etype == 'violation')): etype = 'foul.vio'; atype = 'foul.vio'
    if(etype == 'timeout'): atype = "timeout"
    if(etype == "free throw"): etype = 'shot'; atype = 'freethrow'
    if(etype == 'rebound'): atype = 'rebound'
    
    output = "_".join([etype, team, atype, result])
    
    time_split = clock.split(":")
    secs_rem = 60*int(time_split[0]) + int(time_split[1])
    time = 12*60*(period - 1) +  12*60 - secs_rem
    
    return(
           pd.Series(dict(state= output, time = time))
           )

def file_looper(team, name, transitions, time_dict):
    # read game
    try:
        dat = pd.read_csv(name)
        # Replace opposition with "OPP"
        dat['team'] = ["OPP" if x not in (team, "OFF") else x for x in dat.team]
    except:
        print("Error, file {0} not correctly formatted".format(name))
        return "Er"
    
    
    
    # Clean to return list of all states
    colnames = dat.columns.values.tolist()
    states = dat.apply(transition_definer, colnames = colnames, axis = 1)
    
    # Group data by state and get counts
    counts = states.groupby(by = ['state']).size()
    counts.to_frame()
    counts.columns = ['state', 'count']
    
    # Make transition and time matrix
    unique_states = states.state.unique()
    
    for i in range(len(states.index) - 1):
        initial = states.state[i]
        final = states.state[i + 1]
        key = (initial, final)
        
        time_dif = states.time[i + 1] - states.time[i]
        
        if key in transitions:
            transitions[key] += 1
        else:
            transitions[key] = 1
        
        if initial in time_dict:
            time_dict[initial].append(time_dif)
        else:
            time_dict[initial] = [time_dif]

    return({"transitions": transitions, 
    "unique_states": unique_states, 
    "time_dict": time_dict})
    
######



def create_matrix(team, opposition):

    if opposition != None:
        team_files = lookup_func.similar_games(home_team = team, opp_team = opposition, amount = 3)
    else:
        os.chdir("C:\\Users\\Owner\\Desktop\\College 16-17\\FYP\\FYP_python\\Data")
        files = os.listdir()
        team_files = [file for file in files if team in file]
    

    numb_files = len(team_files)
    print("Training on {0} games".format(numb_files))
    
    # Loop over files
    counter = 0
    transitions = {}
    time_dict = {}
    all_states = set()
    for file in team_files:
        output = file_looper(team, file, transitions, time_dict)
        
        if output != "Er":
            transitions = output["transitions"]
            time_dict = output["time_dict"]
            all_states.update(output["unique_states"])
        
        
        counter += 1
        if counter%10 == 0:
            completed = str(round(100*counter/numb_files, 2))
            #print(completed + "% Complete")



    
    
    transitions_DF = pd.DataFrame(0, index= all_states, columns= all_states)
    transition_times = pd.DataFrame(0.0, index= all_states, columns= ["mean", "var", "n", 'fit_alpha', "fit_loc", "fit_beta", "zero_prob"])
    
    for key in transitions:
        transitions_DF[key[1]][key[0]] = transitions[key]

    for key in time_dict:
        transition_times["mean"][key] = np.mean(time_dict[key])
        transition_times["var"][key] = np.var(time_dict[key])
        transition_times['n'][key] = len(time_dict[key])
        
        # Get non-zero data and fit a gamma distribution
        # Fix location at 0 as it is not moved along the x-axis
        all_data = time_dict[key]
        non_zero_data = list(filter(lambda a: a > 0, all_data))
        fit = stats.gamma.fit(non_zero_data, floc=0)
        zero_prob = 1 - len(non_zero_data)/len(all_data)
        
        transition_times['fit_alpha'][key] = fit[0]
        transition_times['fit_loc'][key] = fit[1]
        transition_times['fit_beta'][key] = fit[2]
        transition_times['zero_prob'][key] = zero_prob
        

    
    normalised = transitions_DF.div(transitions_DF.sum(axis=1), axis=0)
    
    #bx = plt.axes()
    #b = sns.heatmap(transitions_DF, ax = bx)
    
    #ax = plt.axes()
    #a= sns.heatmap(normalised, ax = ax)
    

    return  {"probs": normalised, 
    "times": transition_times, 
    "time_dict" : time_dict,
    "transitions_DF": transitions_DF}

 
