from random import random, choice

def gen_sentence():
	return gen_group()

operators = [">>" , "<<" , "+" , "-" , "*" , "/" , "^" , "%" , "&" , "|"]
def gen_operator():
	return [choice(operators)]

#Only generate between 1 and 4096 for an arbitrary reason
def gen_const():
	return [str(int(random() * 4095 + 1))]

def gen_group():
	left_prob = random()

	#Blah blah don't use magic numbers	
	if left_prob < .4:
		left = gen_group()
	elif left_prob > .4 and left_prob < .9:
		left = ["t"]
	else:
		left = gen_const()

	operator = gen_operator()

	right_prob = random()

	if right_prob < .5:
		right = gen_group()
	elif right_prob > .5 and right_prob < .7:
		right = ["t"]
	else:
		right = gen_const()

	return ["("] + left + operator + right + [")"]

print gen_sentence()
