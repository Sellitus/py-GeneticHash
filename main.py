
import random
import hashlib
import time
import multiprocessing as mp
import ctypes
import string

# Import user config variables from config.py
from config import *



#
# Helper functions
# These are used as support, but aren't direct GA-specific functions.
#

def toHash(string):
  hex = hashlib.sha1(str(string)).hexdigest()
  return hex

def toBinary(hex):
  binary = bin(int(hex, 16))[2:].zfill(160)
  return binary

def spinTheRNG():
  random.seed(hashlib.sha1(str((numCores * random.randrange(1,1000,1)) + time.time())).hexdigest())
  random.seed(hashlib.sha512(str((numCores * random.randrange(1,1000,1)) + time.time())).hexdigest())


def weighted_choice(items):
  """
  Chooses a random element from items, where items is a list of tuples in
  the form (item, weight). weight determines the probability of choosing its
  respective item. Note: this function is borrowed from ActiveState Recipes.
  """
  weight_total = sum((item[1] for item in items))
  n = random.uniform(0, weight_total)
  for item, weight in items:
    if n < weight:
      return item
    n = n - weight
  return item

def random_char(minAsciiValue, maxAsciiValue):
  """
  Return a random character between ASCII 32 and 126 (i.e. spaces, symbols,
  letters, and digits). All characters returned will be nicely printable.
  """
  return chr(int(random.randrange(minAsciiValue, maxAsciiValue, 1)))

def random_population(popSize, origSize, minAsciiValue, maxAsciiValue):
  """
  Return a list of popSize individuals, each randomly generated via iterating
  DNA_SIZE times to generate a string of random characters with random_char().
  """
  pop = []
  for i in xrange(popSize):
    dna = ""
    for c in xrange(origSize):
      dna += random_char(minAsciiValue, maxAsciiValue)
    pop.append(dna)
  return pop

#
# GA functions
# These make up the bulk of the actual GA algorithm.
#

#
#
# Kept as example
# DO NOT USE
def fitness_original(dna, hashHex, hashSize):
  """
  For each gene in the DNA, this function calculates the difference between
  it and the character in the same position in the OPTIMAL string. These values
  are summed and then returned.
  """
  fitness = 0
  for c in xrange(hashSize):
    fitness += abs(ord(dna[c]) - ord(hashHex[c]))
  return fitness
# DO NOT USE
#
#

# Hamming distance fitness function
def fitness(dna,hashBinary):

  dna = toHash(dna)
  dna = toBinary(dna)

  #[dna, HASH_BIN] = makeBinaryEven(dna,HASH_BINARY)

  """Calculate the Hamming distance between two bit strings"""
  assert len(dna) == len(hashBinary)
  count,z = 0,int(dna,2)^int(hashBinary,2)
  while z:
      count += 1
      z &= z-1
  return count

def mutate(dna, origSize, mutationChance, minAsciiValue, maxAsciiValue):
  """
  For each gene in the DNA, there is a 1/mutation_chance chance that it will be
  switched out with a random character. This ensures diversity in the
  population, and ensures that is difficult to get stuck in local minima.
  """
  dna_out = ""
  for c in xrange(origSize):
    if int(random.random()*mutationChance) == 1:
      dna_out += random_char(minAsciiValue, maxAsciiValue)
    else:
      dna_out += dna[c]
  return dna_out

def crossover(dna1, dna2, origSize):
  """
  Slices both dna1 and dna2 into two parts at a random index within their
  length and merges them. Both keep their initial sublist up to the crossover
  index, but their ends are swapped.
  """
  pos = int(random.random()*origSize)
  return (dna1[:pos]+dna2[pos:], dna2[:pos]+dna1[pos:])

def apocalypse(population, numSurvivingPop, origSize, popSize, minAsciiValue, maxAsciiValue):
  """
  Same as random_population() but passes in the top numSurvivingPop of the previous population to the newest one.
  """

  pop = []
  for i in xrange(popSize-numSurvivingPop):
    dna = ""
    for c in xrange(origSize):
      dna += random_char(minAsciiValue, maxAsciiValue)
    pop.append(dna)
  for i in xrange(numSurvivingPop):
    pop.append(population[i])
  return pop


#
#
#
# Main function (split off for threading)
#
#
#
#
def threadedMain(coreNum, sharedString, sharedFitness, popSize, mutationChance):

  # Seed el RNG
  spinTheRNG()

  population = random_population(popSize, origSize, minAsciiValue, maxAsciiValue)

  # Keeps track of the best fitness rating
  bestFitness = 99999

  # Keeps track of the last fitness rating for comparison
  lastBestFitness = ''
  # Keeps count of fitness value repetitions for mutation chance increaser
  mutationRepeatCount = 0
  # Counters for number of generations and interval
  generation = 0
  interval = 0
  # Simulate all of the generations.
  while True != False:
    generation = generation + 1
    interval = interval + 1

    # If the shared string has a better fitness rating than the current, place the best string into the population
    if sharedFitness.value < bestFitness and lastBestFitness != sharedString.value:
      population[popThreadedInsertPosition] = sharedString.value
      lastBestFitness = sharedString.value
      if generation > printInterval:
        print "CIVILIZATION " + str(coreNum) + ": added the " + str(sharedString.value) + " alien DNA from a distant colony!"


    if interval == printInterval:
      print "CIVILIZATION " + str(coreNum) + ": Generation " + str(generation) + "  -  Top String: \'" + str(population[0]) + "\'   -  Best Fitness: " + str(bestFitness) + "  -  Hash: " + toHash(population)
      interval = 0

      if bestFitness == lastBestFitness:
        if mutationChance > mutationMinChance:
          mutationRepeatCount = mutationRepeatCount + 1
          if mutationRepeatCount >= mutationMaxRepetitions:
            mutationRepeatCount = 0

            mutationChance = mutationChance - mutationReductionAmount
            if coreNum == 1:
              print '   ---All Civilization\'s DNA Mutation Chance Increased To: ' + str((1.0/float(mutationChance)) * 100.0) + '%  From: ' + str((1.0/float(mutationChance+mutationReductionAmount)) * 100.0) + '% ---   '

        elif popSize <= popMaxSize:
          mutationRepeatCount = mutationRepeatCount + 1
          if mutationRepeatCount >= mutationMaxRepetitions:
            mutationRepeatCount = 0

            popSize = popSize + popSizeIncrease
            if popSize > popMaxSize:
              print "   ---" + str(printInterval) + " More Generations Before Nuclear War---   "
            else:
              print '   ---Civilization ' + str(coreNum) + ' Population Increased By: ' + str(popSizeIncrease) + ' To: ' + str(popSize) + '---   '


        else:
          population = apocalypse(population, numSurvivingPop, origSize, popSize, minAsciiValue, maxAsciiValue)
          mutationChance = mutationChanceOrig
          populationSize = popSize

          print '   ---The Ever-Fabled Civilization ' + str(coreNum) + ' Apocalypose Hath Come---   '
          print '   ---' + str(numSurvivingPop) + ' OF ' + str(populationSize) + ' PEOPLE SURVIVED THE APOCALYPSE---   '
          print '   ---CONGRATULATIONS TO THOSE ' + str(numSurvivingPop) + ' WHO SURVIVED THE PURGE!---   '
          print '   ---YOU ARE THE ONLY ONES WHO WILL BE REMEMBERED---   '
          print '   ---YOU MAKE OUR GENE POOL PROUD---   '

      else:
        mutationRepeatCount = 0

      lastBestFitness = bestFitness



    weighted_population = []

    # Add individuals and their respective fitness levels to the weighted
    # population list. This will be used to pull out individuals via certain
    # probabilities during the selection phase. Then, reset the population list
    # so we can repopulate it after selection.
    for individual in population:
      fitness_val = fitness(individual,hashBinary)

      if fitness_val < bestFitness:
        bestFitness = fitness_val
        if sharedString.value != individual:
          sharedString.value = individual
          sharedFitness.value = fitness_val
          if generation > printInterval:
            print "CIVILIZATION " + str(coreNum) + ": sent their superior DNA: '" + str(population[0]) + "' with fitness: " + str(fitness_val) + " into outer space randomly, hoping it will help other colonies in the universe evolve further..."

      # Generate the (individual,fitness) pair, taking in account whether or
      # not we will accidently divide by zero.
      if fitness_val == 0:
        pair = (individual, 1.0)
      else:
        pair = (individual, 1.0/fitness_val)

      weighted_population.append(pair)

    population = []

    # Select two random individuals, based on their fitness probabilites, cross
    # their genes over at a random point, mutate them, and add them back to the
    # population for the next iteration.
    for _ in xrange(popSize/2):
      # Selection
      ind1 = weighted_choice(weighted_population)
      ind2 = weighted_choice(weighted_population)

      # Crossover
      ind1, ind2 = crossover(ind1, ind2, origSize)

      # Mutate and add back into the population.
      population.append(mutate(ind1, origSize, mutationChance, minAsciiValue, maxAsciiValue))
      population.append(mutate(ind2, origSize, mutationChance, minAsciiValue, maxAsciiValue))

    if population[0] == ORIGINAL:
      print "    ---CIVILIZATION " + str(coreNum) + " EVOLVED ENOUGH TO CRACK THE CODE---    "
      print "Generation: " + generation
      print "Original String: " + ORIGINAL
      print "Original Hash: " + HASH
      print "    ------------    "
      print "Cracked String: " + population[0]
      print "Cracked Hash: " + toHash(population[0])
      print "    ---CIVILIZATION " + str(coreNum) + " EVOLVED ENOUGH TO CRACK THE CODE---    "
      exit(0)

  # Display the highest-ranked string after all generations have been iterated
  # over. This will be the closest string to the OPTIMAL string, meaning it
  # will have the smallest fitness value. Finally, exit the program.
  fittest_string = population[0]
  minimum_fitness = fitness(population[0],hashBinary)

  for individual in population:
    ind_fitness = fitness(individual,hashBinary)
    if ind_fitness <= minimum_fitness:
      fittest_string = individual
      minimum_fitness = ind_fitness

  print "CIVILIZATION " + str(coreNum) + ": Fittest String: %s" % fittest_string
  exit(0)



#
#
# Main driver
# Generate a population and simulate GENERATIONS generations.
#
#


if __name__ == "__main__":

  print "SETUP: Starting..."
  # Seed the RNG
  spinTheRNG()

  # Sleep for a sec for fun
  time.sleep(random.randrange(1,3,1))

  print "SETUP: Complete!"

  q = mp.Queue()
  hashProcesses = {}

  sharedString = mp.Array(ctypes.c_char, "tempstart")
  sharedFitness = mp.Value('i', 999999)

  print " --- Birthing Each Civilization --- "
  for i in range(numCores):
      coreNum = i+1;
      hashProcesses[i] = mp.Process(target=threadedMain, args=(coreNum, sharedString, sharedFitness, popSize, mutationChance))
      hashProcesses[i].start()
      print "CIVILIZATION " + str(coreNum) + ": Has Created Life"
      time.sleep(random.randrange(0,3,1))


