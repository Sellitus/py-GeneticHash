import hashlib

def toHash(string):
  hex = hashlib.sha1(str(string)).hexdigest()
  return hex

def toBinary(hex):
  binary = bin(int(hex, 16))[2:].zfill(160)
  return binary

#
# Variables
# Setup optimal string and GA input variables.
#

# Necessary for MAIN function
numCores    = 6
popSize     = 200

# For threadedMain
popSizeOrig     = popSize
popMaxSize      = popSize * 5
popSizeIncrease = 200
# Position to insert from the top (0) position in the core's current population.
popThreadedInsertPosition = popSize / 10    # 10% from the top of the population rating for (popSize / 10).

printInterval = 2000   # Prints every # generations

mutationChance = 6            # Chance to mutate is 1 / (value). Default: 100
mutationChanceOrig = mutationChance # Keeps the original to revert after the apocalypse
mutationMinChance = 2         # Minimum chance the mutation chance can be reduced to.
mutationReductionAmount = 1   # Reduces the mutationChance by this amount if there is no improvement for a period of time
mutationMaxRepetitions = 3    # Number of repetitions allowed until a reduction in mutationChane occurs

numSurvivingPop = 3

ORIGINAL     = "password"
origSize     = len(ORIGINAL)

HASH         = toHash(ORIGINAL)
hashBinary   = toBinary(HASH)
hashSize     = len(HASH)

minAsciiValue = 0
maxAsciiValue = 255
