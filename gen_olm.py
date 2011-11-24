from random import random, choice
from types import StringType
from math import floor

def gen_sentence():
	return gen_group()

operators = [">>" , "<<" , "+" , "-" , "*" , "/" , "^" , "%" , "&" , "|"]
def gen_operator():
	return choice(operators)

#Only generate between 1 and 4096 for an arbitrary reason
def gen_const():
	return str(int(random() * 4095 + 1))

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
		new_m = gen_operator()
	elif is_const(m):
		if mutate_group_prob < .2:
			new_m = gen_group()
		elif mutate_group_prob > .2 and  mutate_group_prob < .3:
			new_m = gen_var()
		else:
			new_m = gen_const()
	elif is_var(m):
		if mutate_group_prob < .3:
			new_m = gen_group()
		elif mutate_group_prob > .3 and mutate_group_prob < .3:
			new_m = gen_const()
		else:
			new_m = gen_var()
	else:
		if mutate_group_prob < .5:
			new_m = mutate(m)
		else:	
			new_m = gen_group()
	
	sentence[m_index] = new_m
	return sentence

def flatten(l):
	ret = []
	for val in l:
		if isinstance(val , StringType):
			ret.append(val)
		else:
			ret.extend(flatten(val))
	
	return ret

for i in range(10):
	s = gen_sentence()
	print "orig " , s
	m = mutate(s)
	print "mutate " , m
