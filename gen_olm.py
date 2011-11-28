from random import random, choice
from types import StringType
from math import floor
from time import time

def gen_sentence():
	return gen_group()

operators = [">>" , "<<" , "+" , "-" , "*" , "/" , "^" , "%" , "&" , "|"]
def gen_operator():
	return choice(operators)

#Only generate between 1 and 4096 for an arbitrary reason
def gen_const():
	return str(int(random() * 15 + 1))

def gen_var():
	return "t"

def gen_group():
	left_prob = random()

	#Blah blah don't use magic numbers	
	if left_prob < .4:
		left = [gen_group()]
	elif left_prob > .4 and left_prob < .9:
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

def crossover(s_1 , s_2):
	
	print "s_1 " , s_1 , s_1[:2]
	print "s_2 " , s_2 , s_2[2:]
	child_1 = s_1[:2] + s_2[2:]
	child_2 = s_2[:2] + s_1[2:]
	return [child_1 , child_2]

def add(s_1 , s_2):
	operator = [gen_operator()]

	child = ['('] + s_1 + operator + s_2 + [')']

	return child

#Recursively flattens a list
def flatten(l):
	ret = []
	for val in l:
		if isinstance(val , StringType):
			ret.append(val)
		else:
			ret.extend(flatten(val))
	
	return ret


values_to = 65536

def gen_values(s):
	values = [0] * values_to
	
 	start_time = time()
	for t in range(values_to):
		try:
			val = eval(s)
			values[t] = int(abs(val) % 255)
		except ValueError:
			values[t] = 0
		except ZeroDivisionError:
			values[t] = 0
		except OverflowError:
			values[t] = 0
		
		if time() > start_time + 2:
			return [0] * values_to

	return values

def check_cycles(s):
	cycles_count = 0
	for i in range(1 , len(s) / 4):
		slices = s[::i]
		shift_slices = slices[:]
		h = slices[:1]
		del shift_slices[:1]
		shift_slices.extend(h)
		diff = map(int.__sub__ , slices , shift_slices)
		diff = map(lambda x: x * x , slices)
		diff_sum = sum(diff)
		if diff_sum == 0:
			if i < 100:
				print "Cycle less than 1000"
				return 0
			else:
				cycles_count += 1

	return cycles_count

def mean_diff(s):
	mean = s[0]
	mean_diff = 0

	for i in s:
		mean_diff = mean_diff + abs(i - mean)
		mean = (mean + i) / 2

	return mean_diff

def fitness(s):
	print "Fitness " , s
	values = gen_values(s)
	#print values

	cycles = check_cycles(values)
	print "Cycles " , cycles

	mean_diff_sum = mean_diff(values)
	print "Mean Diff " , mean_diff_sum

	fitness = 0

	fitness += (cycles * 1000)
	
	if mean_diff_sum > 4000 and mean_diff_sum < 2500000:
		fitness += mean_diff_sum / 100

	fitness += len(s)

	#listenable_num = listenable(values)

	return fitness

cutoff = 10
def perform_cutoff(s_list):
	top = s_list[:cutoff]
	return top

mutate_prob_to = .01
def perform_mutate(s_list):
	for i in range(len(s_list)):
		s = s_list[i][0]

		mutate_prob = random()

		if mutate_prob < mutate_prob_to:
			s_list[i][0] = mutate(s)
	
	return s_list

def perform_crossover(s_list):
	copy_s_list = s_list[:]
	ret_s_list = []
	while len(copy_s_list) > 0:
		print len(copy_s_list)
		first = choice(copy_s_list)
		copy_s_list.remove(first)
		second = choice(copy_s_list)
		copy_s_list.remove(second)
		children = crossover(first[0] , second[0])
		
		child_one = [children[0] , 0]
		if child_one not in s_list:
			print "Child not found"
			
			print child_one
			print s_list
			print "\n"
			ret_s_list.append(child_one)
		
		child_two = [children[1] , 0]
		if child_two not in s_list:
			ret_s_list.append(child_two)
	
	return ret_s_list

def perform_add(s_list):
	ret_s_list = []
	while len(s_list) > 0:
		left = choice(s_list)
		s_list.remove(left)
		right = choice(s_list)
		s_list.remove(right)

		print "Left " , left[0]
		print "Right " , right[0]
		comb = [add(left[0] , right[0]) , 0]

		print "Comb " , comb[0]
		ret_s_list.append(comb)

	return ret_s_list

total_s = 30
def perform_replace(s_list):
	while len(s_list) < total_s:
		s = gen_sentence()
		s_add = [s , 0]
		if s_add not in s_list:
			s_list.append(s_add)
	
	return s_list

def perform_fitness(s_list):
	for s in s_list:
		s[1] = fitness(" ".join(flatten(s[0])))
	
	return s_list

iterations = 10000
def perform(init_s_list):
	s_list = init_s_list
	for i in range(iterations):
		
		sorted_s_list = sorted(s_list, key = lambda s: s[1] , reverse=True)
		print "Iteration " , i
		#print "Curr list\n" , sorted_s_list , "\n"
		for s in sorted_s_list:
			print "Fitness " , s[1]
			print " ".join(flatten(s[0])) , "\n"

		print "\n"
		
		top = perform_cutoff(sorted_s_list)
		print "top " , top
		children = perform_crossover(top)
		print "children " , children
		#print "top " , top
		add_children = perform_add(top)
		print "add children " , add_children
		#mutate_top = perform_mutate(top)
		
		top.extend(children)
		top.extend(add_children)
		print "modified " , top

		replaced = perform_replace(top)
		s_list = perform_fitness(replaced)

#init_s_list = [[['(' , 't' ,  '>>' ,  '4' , ')'] , 0]]
init_s_list = []
init_s_list = perform_replace(init_s_list)
print init_s_list
init_s_list = perform_fitness(init_s_list)
print init_s_list

perform(init_s_list)
