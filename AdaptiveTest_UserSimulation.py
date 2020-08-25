# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 20:26:20 2020

Simulation of a threshold measurement test using an adaptive method based on the presentation
of next stimulus based on the posterior probability

The user behaviour is simulated to assess the method's performance

@author: Marina Torrente Rodriguez
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

import random
from PsychometricFunctionClass import PsychometricFunction
from MaxLikelihoodEstimation import MLE_search

# Define user
user_threshold = 0.062
user_slope = 40
lapse_error = 0.01
test_gamma = 0
typef= "Logistic"
PF_user = PsychometricFunction(Alpha=user_threshold, Beta=user_slope,
                               Gamma=test_gamma, Lambda=lapse_error,
                               type_func=typef, inv=True)

# Test parameters
MaxTrials = 30 # After which the test stops
MinTrials = 0.20*MaxTrials # Stimuli intensity for the first number of trials is presented at random 
#StimLevels = np.array([0.01, 0.03, 0.05, 0.07, 0.09, 0.11])
StimLevels = np.linspace(0.01,0.11,10)
Gamma = test_gamma
Lambda = lapse_error
MaxConsecutive = 3

# Initialise test
trials_counter = 0
NumCorrect = np.zeros(len(StimLevels))
Total = np.zeros(len(StimLevels))
stim = []


# Storage variables for progress animation
total = np.zeros([MaxTrials,len(StimLevels)])
numcorrect = np.zeros([MaxTrials,len(StimLevels)])
alpha = []
beta = []

# Trial loop
while (trials_counter < MaxTrials):
    trials_counter += 1

    if trials_counter<= MinTrials:
        # Choose next stimulus intensity randomly
        StimIndex = random.choice(range(len(StimLevels)))

    else:
        
        if ((stim[-MaxConsecutive:-1]-stim[-1]).sum() == 0) & (len(stim) > MaxConsecutive):
            # Choose next stimulus intensity randomly if the same stimilus 
            # has been presented more than 4 consecutive times
            StimIndex = random.choice(range(len(StimLevels)))
        else:            
            # present values by Psi method: 
            # fitting PF taking the estimate PF as the posterior probablity
            results = MLE_search(Gamma, Lambda, typef, StimLevels, NumCorrect, Total)
            alpha.append(results.x[0])
            beta.append(results.x[1])
            
            print("alpha = ", results.x[0], " ; beta = ", results.x[1])
            
            # find stim level closest to alpha and set as current 
            diff = abs(StimLevels-results.x[0])
            StimIndex = np.unravel_index(np.argmin(diff, axis=0), diff.shape)
            
#            # Find a stimulus within the steep region of the PF slope
#            y = PsychometricFunction(Alpha=alpha, Beta=beta,
#                               Gamma=test_gamma, Lambda=lapse_error,
#                               type_func=typef).PF(StimLevels)
#            StimCurrent = random.choice(StimLevels[(y>(Gamma+Lambda)) & (y<1)])
            


    # Current Stimulus level by obtained index
    StimCurrent = StimLevels[StimIndex]
    print("Current stimulus: ",StimCurrent) # Print
    stim.append(StimCurrent)                # Store
    
    # Increment number of total stimuli for the current level
    Total[StimIndex] += 1
        
    # Simulate user response
    # User PF value at current stimulus level
    pCurrent = PF_user.PF(StimCurrent)
    # Record as correct response with a random chance 
    # equal to the velue of the PF at that stimulus level
    if random.random() <= pCurrent:
        NumCorrect[StimIndex] += 1
        
    # Save data for progress animation
    total[trials_counter-1,:] = Total
    numcorrect[trials_counter-1,:] = NumCorrect
        

# Print results
print("End of test!")
print("Simulated threshol:", user_threshold, " ; Measured threshold: ", alpha[-1])
print("Simulated slope:", user_slope, " ; Measured slope: ", beta[-1])

# Plot results
x = np.min(StimLevels)
plt.figure()
PF_user.plot_PF(StimLevels[0],StimLevels[-1],100)
plt.scatter(StimLevels,NumCorrect/Total, s=2*Total, color='b')
PsychometricFunction(Alpha=alpha[-1], Beta=beta[-1],
                     Gamma=Gamma, Lambda=Lambda,
                     type_func=typef, inv=True).plot_PF(StimLevels[0],StimLevels[-1],100)
plt.grid()
plt.ylabel("Probability of Correct Response")
plt.xlabel("Stimulus Intensity")
plt.legend(["Simulated User PF", "Measured Behaviour", "Estimate User PF"])
plt.ylim(-0.1,1.1)

# Plot summary of stimuli level presented
plt.figure()
plt.plot(np.linspace(1,MaxTrials,MaxTrials), stim,'o-')
plt.plot([0, MaxTrials],[user_threshold,user_threshold])
plt.xlabel("# Trial")
plt.ylabel("Stimulus Level")
    
    
# Animation
xdata = np.linspace(StimLevels[0],StimLevels[-1],100)
ydata = PsychometricFunction(Alpha=user_threshold, Beta=user_slope,
                     Gamma=Gamma, Lambda=Lambda, type_func=typef).PF(xdata)
fig, ax = plt.subplots()
us, = ax.plot(xdata, ydata, 'm-', label='Simulated User PF')
sc, = ax.plot([], [], 'bo', label='Measured Behaviour')
ln, = ax.plot([], [], 'b-', label='Estimated User PF')
# Trial number count annotation
str_ann = '0/' + str(MaxTrials)
xpos_ann = (np.max(StimLevels)-np.min(StimLevels))/10
ypos_ann = 0.1
annotation = plt.annotate(str_ann, xy=(xpos_ann,ypos_ann),
                          xytext=(StimLevels[-2],0.1),
                          color='b')


# Set initial display parameters
def init():
    # Axes limits
    ax.set_xlim(np.min(StimLevels), np.max(StimLevels))
    ax.set_ylim(0, 1)
    return sc, ln, annotation,

# Define update function for each frame of the animation
def update(frame):
    # Measured points update
    sc.set_data(StimLevels, numcorrect[frame,:]/total[frame,:])
    
    # Estimate PF update
    xdata = np.linspace(StimLevels[0],StimLevels[-1],100)
    ydata = PsychometricFunction(Alpha=alpha[frame], Beta=beta[frame],
                         Gamma=Gamma, Lambda=Lambda, type_func=typef).PF(xdata)
    ln.set_data(xdata,ydata)
    
    # Trial number count annottaion update
    str_ann = str(frame) + '/' + str(MaxTrials)
    annotation.set_text(str_ann)

    return sc, ln, annotation,

# Define animation function
ani = animation.FuncAnimation(fig, func=update, frames=len(total),
                    init_func=init, interval=100, blit=True, repeat= False)

# Set figure labels
plt.xlabel("Stimulus levels")
plt.ylabel("Probability of Correct Response")
plt.legend()

# Show animation
plt.show()
