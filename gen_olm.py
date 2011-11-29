from random import random, choice
from types import StringType
from math import floor
from time import time

def gen_sentence():
	return gen_group()

operators = [">>" , "<<" , "+" , "-" , "*" , "/" , "^" , "%" , "&" , "|"]
def gen_operator():
	return choice(operators)


small_prob_to = .9
#Only generate between 1 and 4096 for an arbitrary reason
def gen_const():
	small_prob = random()
	#We want a larger chance of generating smaller numbers for bitshifting
	if small_prob < small_prob_to:
		ret_val = random() * 15 + 1
	else:
		ret_val = random() * 1023 + 1

	return str(int(ret_val))

def gen_var():
	return "t"

def gen_group():
	left_prob = random()

	#We put everything in lists so we can concatenate everything together
	#Everything except groups will not be a list after concatenation
	#Since the group is a list of lists
	if left_prob < .4:
		left = [gen_group()]
	elif left_prob > .4 and left_prob < .8:
		left = [gen_var()]
	else:
		left = [gen_const()]

	operator = [gen_operator()]

	right_prob = random()

	if right_prob < .5:
		right = [gen_group()]
	elif right_prob > .5 and right_prob < .7:
		right = [gen_var()]
	else:
		right = [gen_const()]

	return ["("] + left + operator + right + [")"]

def is_operator(m):
	return m in operators

def is_const(m):
	return m > '0' and m < '4096'

def is_var(m):
	return m == 't'

def is_paren(m):
	return m == "(" or m == ")"

def mutate(sentence):
	m_index = int(floor(random() * len(sentence)))
	m = sentence[m_index]

	#We don't want to mutate a parenthesis
	while is_paren(m):
		m_index = int(floor(random() * len(sentence)))
		m = sentence[m_index]

	mutate_group_prob = random()
	
	if is_operator(m):
		#If our mutation is an operator
		#We can only replace with another operator
		new_m = gen_operator()
	elif is_const(m):
		#If our selected mutation is a constant
		if mutate_group_prob < .2:
			new_m = gen_group()
		elif mutate_group_prob > .2 and  mutate_group_prob < .3:
			new_m = gen_var()
		else:
			new_m = gen_const()
	elif is_var(m):
		#If our selected mutation is a variable (ie t)
		if mutate_group_prob < .3:
			new_m = gen_group()
		elif mutate_group_prob > .3 and mutate_group_prob < .4:
			new_m = gen_const()
		else:
			new_m = gen_var()
	else:
		#We've selected a subgroup to mutate, we either replace
		#or mutate the subgroup
		if mutate_group_prob < .5:
			new_m = mutate(m)
		else:	
			new_m = gen_group()
	
	sentence[m_index] = new_m
	return sentence

#Splices two parents together
def crossover(s_1 , s_2):
	#Since the sentences are tree like structures,
	#We just need to take the left branch of one and put it together
	#With the right brancg of two, and vice versa
	child_1 = s_1[:2] + s_2[2:]
	child_2 = s_2[:2] + s_1[2:]
	return [child_1 , child_2]

#Concatenates to sentences
def add(s_1 , s_2):
	#Need to generate a new operate to put between them
	operator = [gen_operator()]

	#We need to put each group into a list to preserve the tree
	if not is_const(s_1) and not is_var(s_1):
		s_1 = [s_1]
	
	if not is_const(s_2) and not is_var(s_2):
		s_2 = [s_2]

	child = ['('] + s_1 + operator + s_2 + [')']

	return child

#Recursively flattens a list
def flatten(l):
	ret = []
	for val in l:
		#If its a string, we're done flattening
		if isinstance(val , StringType):
			ret.append(val)
		else:
			ret.extend(flatten(val))
	
	return ret


#8000 cycles per second times seconds recorded
values_to = 8000 * 10
max_time = 3

def gen_values(s):
	values = [0] * values_to
	
 	start_time = time()
	for t in range(values_to):
		try:
			#Evaluate the string
			val = eval(s)
			#Mod with 256 to turn it into a character
			#This is probably where the discrepency between putchar()
			#and this implementation occurs
			values[t] = int(abs(val) % 256)
		except ValueError:
			#Probably a negative shift value, ignore
			values[t] = 0
		except ZeroDivisionError:
			#Dividing by zero, ignore
			values[t] = 0
		except OverflowError:
			#Value is larger than a 32 bit integer
			#We could probably do something else here
			values[t] = 0
		
		#If we go over time, we want to ignore this string
		if time() > start_time + max_time:
			return [0] * values_to

	return values

def check_cycles(s):
	cycles_count = 0
	num_cycles = 1


	for i in range(1 , len(s)):

		#This will select all values over the cycle we are looking for
		slices = s[::i]

		#We take the slices, remove the first value and put it at the end
		#So, [1 , 2 , 3] becomes [2 , 3 , 1]
		shift_slices = slices[:]
		h = slices[:1]
		del shift_slices[:1]
		shift_slices.extend(h)
		
		#Essentially a zipWith with subtraction
		#We subtract each element of one list with the element with the same index in the other
		diff = map(int.__sub__ , slices , shift_slices)

		#Take the abs of each element
		diff = map(lambda x: abs(x) , slices)

		#Take the sum
		diff_sum = sum(diff)

		#Right now we only check if each element in the list is the same
		#ie diff is 0, however we could change this if we wanted leeway 
		#in cycles
		if diff_sum == 0:
			#We subtract the number of cycles because a set with cycle 1 with have
			#cycles at 2 , 3 , 4 etc, so we need to take care of sets with a large 
			#number of cycles, and count them less
			#We add i, because we want sets with complex cycles, ie ones with large periods
			cycles_count += i - num_cycles
			num_cycles += 1

	return cycles_count

def mean_diff(s):
	mean = s[0]
	mean_diff = 0
	
	#For each value, calculate the diff from the mean
	#Then recalculate the mean
	for i in s:
		mean_diff = mean_diff + abs(i - mean)
		mean = (mean + i) / 2

	return mean_diff

def fitness(s):
	#Generate the values of the sentence
	values = gen_values(s)

	#See how many cycles we have
	cycles = check_cycles(values)

	#Calculate the sum of the difference from the mean
	mean_diff_sum = mean_diff(values)

	fitness = cycles
	
	#Need to scale the mean differences
	fitness += mean_diff_sum / 100

	#Longer sentences tend to be more complicated
	fitness *= len(s)

	#TODO: Implement the number of values which are listenable
	#listenable_num = listenable(values)

	return fitness

cutoff = 10
def perform_cutoff(s_list):
	#Just pick the top 10
	top = s_list[:cutoff]
	return top

mutate_prob_to = .01
def perform_mutate(s_list):
	for i in range(len(s_list)):
		#This is the actual sentence
		s = s_list[i][0]

		mutate_prob = random()

		#We only mutate a small percentage of the time
		if mutate_prob < mutate_prob_to:
			s_list[i][0] = mutate(s)
	
	return s_list

#Performs crossover on the list
def perform_crossover(s_list):
	#We need a copy of this list to remove things from
	copy_s_list = s_list[:]
	ret_s_list = []
	while len(copy_s_list) > 0:
		
		#Pick two random parents
		first = choice(copy_s_list)
		copy_s_list.remove(first)
		second = choice(copy_s_list)
		copy_s_list.remove(second)

		#Create the pair of children from crossover
		children = crossover(first[0] , second[0])
		

		#Add them to the list if they are not already in it
		child_one = [children[0] , 0]
		if child_one not in s_list:
			ret_s_list.append(child_one)
		
		child_two = [children[1] , 0]
		if child_two not in s_list:
			ret_s_list.append(child_two)
	
	return ret_s_list

#Takes the top parents and combines them together
def perform_add(s_list):
	ret_s_list = []
	copy_s_list = s_list[:]
	#We'll be removing pairs of parents from s_list
	while len(copy_s_list) > 0:

		#Pick a random pair of parents and remove them from the list
		left = choice(copy_s_list)
		copy_s_list.remove(left)
		right = choice(copy_s_list)
		copy_s_list.remove(right)

		#Combine parents and create a new fitness pair
		comb = [add(left[0] , right[0]) , 0]

		#Add the fitness pair to our return value
		ret_s_list.append(comb)

	return ret_s_list


total_s = 30
#Generate sentences until we have the desired number (30)
def perform_replace(s_list):
	while len(s_list) < total_s:
		s = gen_sentence()
		#Create a new fitness pair
		s_add = [s , 0]
		#We don't want to have two of the same sentences in the list
		if s_add not in s_list:
			s_list.append(s_add)
	
	return s_list

def perform_fitness(s_list):
	for s in s_list:
		#The join statement flattens the tree and turns it into a string
		s[1] = fitness(" ".join(flatten(s[0])))
	
	return s_list

iterations = 1000
def perform(init_s_list):
	s_list = init_s_list
	for i in range(iterations):
		
		#Sort in descending order based on the fitness (s[1])
		sorted_s_list = sorted(s_list, key = lambda s: s[1] , reverse=True)
		
		print "\n------------------------------------------------------------"
		print "Iteration " , i
		for s in sorted_s_list:
			print "Fitness " , s[1]
			print " ".join(flatten(s[0])) , "\n"

		print "\n"
		
		top = perform_cutoff(sorted_s_list)

		#Creates children by crossing top parents
		crossover_children = perform_crossover(top)

		#Creates children from combining the top parents
		add_children = perform_add(top)

		#Mutate the top performers
		#top = perform_mutate(top)
		
		#Add the crossover children in
		top.extend(crossover_children)
		#Add the combined children in
		top.extend(add_children)

		#Fill up the list with randomly generated sentences
		replaced = perform_replace(top)

		#Calculate the fitness for all sentences
		s_list = perform_fitness(replaced)

#Initialize our list, possibly with known good patterns
#Our list is a list of pairs of sentences and fitnesses
init_s_list = [[['(' , 't' ,  '>>' ,  '4' , ')'] , 0] , [['(' , ['(' , 't' , '<<' , '7' , ')'] , '%' , ['(' , 't' , '>>' , '11' , ')'] , ')'] , 0]]
#Fill up our list
init_s_list = perform_replace(init_s_list)
#Calculate our initial fitness
init_s_list = perform_fitness(init_s_list)
#Perform the genetic algorithm
perform(init_s_list)
