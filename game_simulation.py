# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 09:58:05 2017

@author: Owner
"""

import transition_create
import numpy as np
import time, math
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns

import abbreviation_scrape

def trainer(team, opposition, abbs):
    try:
        full_name = abbs[team]
    except:
        full_name = team

    print("Learning {0} Probabilities".format(full_name))
    output = transition_create.create_matrix(team, opposition)
    matrix = output["probs"]
    time = output["times"]
    return matrix, time


def solo_game_sim(team, matrix, times):
    duration = 4*12*60
    state = "jump ball_OFF_nan_nan"
    clock = 0
    home_score = 0
    away_score = 0
    state_count = 0


    while clock < duration:
        state_count += 1
        initial_state = state
        
        form_clock = "{0}:{1}".format(str(math.floor(clock//60)).zfill(2), str(int(clock %60)).zfill(2))
        #print("{0} | {2} : {3} | {1}".format(form_clock, state, str(home_score).zfill(2), str(away_score).zfill(2)))
        
        next_states = matrix.loc[initial_state,:]
        
        # Select a sample of size one from the next state row with those probs
        state = np.random.choice(next_states.index, 1, p= next_states)[0]

        # increase time by sampling from a gamma dist dependent on intial state
        time_mean = times["mean"][initial_state]
        time_var = times["var"][initial_state]
        fit_alpha = times['fit_alpha'][initial_state]
        fit_beta = times['fit_beta'][initial_state]
        fit_loc = times['fit_loc'][initial_state]
        zero_prob = times['zero_prob'][initial_state]
        time_size = (times['n'][initial_state])*(1 - zero_prob)

        if (time_var ==0 or time_mean == 0 or time_size <= 2):
            # If mean or variance is 0 we have a problem so if that occurs
            # then we just take the mean. Mainly Variance is the one that
            # is 0.
            time_taken = time_mean
            
        else:
            # Choose whether or not the entry will be a zero
            coin_flip = np.random.choice([0,1], 1, p=[zero_prob, 1-zero_prob])[0]
            gamma_sample = stats.gamma.rvs(a = fit_alpha, scale = fit_beta, loc = fit_loc, size = 1)[0]
            # With prob 'zero_prob' time taken will be zero, otherwise it will be sampled from the gamma            
            time_taken = gamma_sample*coin_flip 
            
        clock += time_taken
        #time.sleep(0.25)

        # Scoring
        if state == "shot_{0}_2pt_made".format("OPP"):
            away_score += 2
        elif state == "shot_{0}_2pt_made".format(team):
            home_score += 2
        elif state == "shot_{0}_3pt_made".format("OPP"):
            away_score += 3
        elif state == "shot_{0}_3pt_made".format(team):
            home_score += 3
        elif state == "shot_{0}_freethrow_made".format(team):
            home_score += 1
        elif state == "shot_{0}_freethrow_made".format("OPP"):
            away_score += 1

    score_dif = home_score - away_score
    
    return {'score_dif':score_dif,
            'state_count': state_count}


def solo_run_sim(team, n, plots):
    try:
        abbs = abbreviation_scrape.scrape()
    except:
        abbs = {team: team}

    matrix, times = trainer(team = team, opposition = None, abbs = abbs)
    state_count = 0
    score_diffs = []

    print("\nRunning Simulations...")
    for game_numb in range(n):
        #if game_numb%(n/10) == 0:
        #    print(str(round(100*game_numb/n)) + "% Complete")

        game = solo_game_sim(team, matrix, times)
        
        state_count += game['state_count']
        score_diffs.append(game['score_dif'])
    
    mean = np.mean(score_diffs)
    median = np.median(score_diffs)
    std = np.std(score_diffs)
    conf = np.percentile(score_diffs, q = [2.5, 97.5])
    home_win_per = 100*sum(1 for i in score_diffs if i > 0)/n
    away_win_per = 100*sum(1 for i in score_diffs if i < 0)/n
    draw_per = 100*sum(1 for i in score_diffs if i == 0)/n
    
    
    if plots == True:
        
        #plt.hist(score_diffs)
        #plt.title("Score Differences")
        #plt.xlabel("Value")
        #plt.ylabel("Frequency")
        #fig = plt.gcf()
        
        print("\n \nSimulation Results")
        print("Mean Score Difference: {0}".format(mean))
        print("Median Score Difference: {0}".format(median))
        print("Standard Deviation: {0}".format(std))
        print("Confidence Interval for Score Difference: {0}".format(conf))
        print("Home: {0}%, Away: {1}%, Draw: {2}%".format(home_win_per, away_win_per, draw_per))
        print("Sample Size: {0}".format(n))
        print("States: {0}".format(state_count))
    
    return {"H": home_win_per, "A": away_win_per, "D": draw_per}





def game_sim(teams, matrixes, times):
    # Run a game simulation
    duration = 4*12*60
    state = "jump ball_OFF_nan_nan"
    clock = 0
    home_score = 0
    away_score = 0
    index = 0
    current_matrix = matrixes[index]
    current_time = times[index]
    state_count = 0
    no_state_errors = 0

    ##print("\n SIMULATING GAME \n --------------------- \n")
    while clock < duration:
        state_count += 1
        initial_state = state
        
        form_clock = "{0}:{1}".format(str(math.floor(clock//60)).zfill(2), str(int(clock %60)).zfill(2))
        #print("{0} | {2} : {3} | {1}".format(form_clock, state, str(home_score).zfill(2), str(away_score).zfill(2)))
        
        next_states = current_matrix.loc[initial_state,:]
        
        # Select a sample of size one from the next state row with those probs
        state = np.random.choice(next_states.index, 1, p= next_states)[0]

        # increase time by sampling from a gamma dist dependent on intial state
        time_mean = current_time["mean"][initial_state]
        time_var = current_time["var"][initial_state]
        fit_alpha = current_time['fit_alpha'][initial_state]
        fit_beta = current_time['fit_beta'][initial_state]
        fit_loc = current_time['fit_loc'][initial_state]
        zero_prob = current_time['zero_prob'][initial_state]
        time_size = (current_time['n'][initial_state])*(1 - zero_prob)

        if (time_var ==0 or time_mean == 0 or time_size <= 2):
            # If mean or variance is 0 we have a problem so if that occurs
            # then we just take the mean. Mainly Variance is the one that
            # is 0.
            time_taken = time_mean
            
        else:
            # Choose whether or not the entry will be a zero
            coin_flip = np.random.choice([0,1], 1, p=[zero_prob, 1-zero_prob])[0]
            gamma_sample = stats.gamma.rvs(a = fit_alpha, scale = fit_beta, loc = fit_loc, size = 1)[0]
            # With prob 'zero_prob' time taken will be zero, otherwise it will be sampled from the gamma            
            time_taken = gamma_sample*coin_flip        
    
        clock += time_taken

        # Swap to other matrix if state includes OPP
        if "OPP" in state:
            try:
                index = (index + 1)%2
                current_matrix = matrixes[index]
                current_time = times[index]
                state = state.replace("OPP", teams[index])
                # this line throws an error if state not in opp and if it
                # is not it ignores and uses the other matrix
                test_for_state = current_matrix.loc[state,:]
            except:
                no_state_errors += 1
                state = state.replace(teams[index], "OPP")
                index = (index + 1)%2
                current_matrix = matrixes[index]
                current_time = times[index]
                

        # Scoring
        if state == "shot_{0}_2pt_made".format(teams[1]):
            away_score += 2
        elif state == "shot_{0}_2pt_made".format(teams[0]):
            home_score += 2
        elif state == "shot_{0}_3pt_made".format(teams[1]):
            away_score += 3
        elif state == "shot_{0}_3pt_made".format(teams[0]):
            home_score += 3
        elif state == "shot_{0}_freethrow_made".format(teams[0]):
            home_score += 1
        elif state == "shot_{0}_freethrow_made".format(teams[1]):
            away_score += 1

    score_dif = home_score - away_score
    
    return {'score_dif':score_dif,
            'state_count': state_count,
            'no_state_errors': no_state_errors}


def run_sim(home, away, n, plots):
    
    try:
        abbs = abbreviation_scrape.scrape()
    except:
        abbs = {home: home, away: away}
    
    teams = [home, away]

    try:
        home_name = abbs[home]
    except:
        home_name = home
    
    try:
        away_name = abbs[away]
    except:
        away_name = away
    
    
    home_matrix, home_time = trainer(team = teams[0], opposition = teams[1], abbs = abbs)
    away_matrix, away_time = trainer(team = teams[1], opposition = teams[0], abbs = abbs)
    matrixes = [home_matrix, away_matrix]
    times = [home_time, away_time]
    score_diffs = []
    errors = 0
    state_count = 0
    
    print("\nRunning Simulations...")
    tic = time.clock()
    
    for game_numb in range(n):
        if game_numb%(n/10) == 0:
            print(str(round(100*game_numb/n)) + "% Complete")

        game = game_sim(teams, matrixes, times)
        
        state_count += game['state_count']
        errors += game['no_state_errors']
        score_diffs.append(game['score_dif'])
    
    toc = time.clock()
    duration = toc - tic
    time_per_state = duration/state_count
    
    mean = np.mean(score_diffs)
    median = np.median(score_diffs)
    std = np.std(score_diffs)
    conf = np.percentile(score_diffs, q = [2.5, 97.5])
    home_win_per = 100*sum(1 for i in score_diffs if i > 0)/n
    away_win_per = 100*sum(1 for i in score_diffs if i < 0)/n
    draw_per = 100*sum(1 for i in score_diffs if i == 0)/n
    error_percent = round(100*errors/state_count)
    
    
    if plots == True:
                
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=1)
        ax.set_xlabel('Score Difference')
        ax.set_ylabel('Frequency')
        x = np.array(score_diffs)
        sns.kdeplot(x, label = "Density Estimate", ax = ax, color = '#CF91A3')
        sns.distplot(x, kde=False, label = "Histogram", norm_hist = True, ax = ax, hist_kws = {'color' : '#E5BABA'})
        plt.legend()
        
        print("\n \nSimulation Results for Game between {0} & {1}".format(home_name, away_name))
        print("Mean Score Difference: {0}".format(mean))
        print("Median Score Difference: {0}".format(median))
        print("Standard Deviation: {0}".format(std))
        print("Confidence Interval for Score Difference: {0}".format(conf))
        print("Home: {0}%, Away: {1}%, Draw: {2}%".format(home_win_per, away_win_per, draw_per))
        print("Sample Size: {0}".format(n))
        print("States: {0}, No. State Errors: {1} ({2}%)".format(state_count, errors, error_percent))
        print("Time taken: {0}s ({1} States/s)".format(round(duration,2), round(time_per_state, 8)))

    return {"H": home_win_per, "A": away_win_per, "D": draw_per}
    

