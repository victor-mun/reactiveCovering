from matplotlib import pyplot as plt
import numpy as np
import json

stage = 4
fileName = "data4"


# Import the data
dataFile = open('data/{0}.json'.format(fileName))  
data = json.load(dataFile)

# Load data
obsRequests = data['ObservationRequests']
fixedPassCost = data['fixedPassCost']
minVisiDuration = data['minVisiDuration']
aois = data['AOIs']
accesses = data['Accesses']
referenceDate = data['referenceDate']
passCostPerTimeUnit = data['passCostPerTimeUnit']
goals = data['Goals']
satPasses = data['Passes']

# Lengths of lists
nAois = len(aois)
nObsRequests = len(obsRequests)
nPasses = len(satPasses)
nGoals = len(goals)

alphaVect = np.linspace(0, 1, 21)
print(alphaVect)
qualityVect = []
costVect = []

for alpha in alphaVect:



    # Import the solution
    if stage == 4:
        solutionFile = open("mySolutionStage4{0}Alpha{1}.json".format(fileName, int(alpha*100)))  
    else:
        solutionFile = open("mySolutionStage{0}{1}.json".format(stage,fileName))  
    solution = json.load(solutionFile)

    # Reading of the solution
    bookings = solution["Bookings"]
    selectedPassIds = []
    tStart = [0] * nPasses
    tEnd = [0] * nPasses
    for i in range(len(bookings)):
        selectedPassIds.append(bookings[i]['passId'])
        tStart[bookings[i]['passId']] = bookings[i]['bookingStart']
        tEnd[bookings[i]['passId']] = bookings[i]['bookingEnd']

    # Computation of the total cost
    timeUses = [tEnd[id] - tStart[id] for id in selectedPassIds]
    totalCost = len(selectedPassIds)*data['fixedPassCost'] + sum(timeUses)*data['passCostPerTimeUnit']

    # Computation of the quality of the covering: It is defined as the relation of the 
    # requests covered over the total amount of requests
    quality = 0
    for aoiId in range(nAois):
        aux = 0
        for goalId in range(nGoals):
            for step in range(goals[goalId]['nSteps']):
                obsReqId = aoiId + nAois*aux + step + (goals[goalId]['nSteps'] - 1)*aoiId
                requestStart = step*goals[goalId]['duStep']
                requestEnd = step*goals[goalId]['duStep'] + goals[goalId]['rctHorizon']
                for passId in selectedPassIds:
                    if any(accessIdObsReq in satPasses[passId]['accessIds'] for accessIdObsReq in obsRequests[obsReqId]['accessIds']):
                        #if (requestStart<=satPasses[passId]['end']-30) and (requestEnd>=satPasses[passId]['start']+30):
                        if (requestStart<=tEnd[passId]-30) and (requestEnd>=tStart[passId]+30):
                            quality +=1
                            break
            aux += goals[goalId]['nSteps']
            
    quality /= nObsRequests

    qualityVect.append(1 - quality)
    costVect.append(totalCost)
    # Presentation of the results
    print("Total cost of the covering: {0}".format(totalCost))
    print("Quality of the covering: {0}".format(quality))

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(qualityVect, costVect)
ax.set_xlabel('1-Quality')
ax.set_ylabel('Cost')
plt.title('')
plt.grid(True)

plt.show()
