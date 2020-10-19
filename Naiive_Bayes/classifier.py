import math
import numpy as np
from paillierlib import paillier

#################################################################################################################
#server side functions , all inputs are np arrays


#class_prior_list is a 1-d array of probabilities of classes
#conditional_prob_list is a 2-d array of 1-d lists , A[i][j] is a list of conditional probabilities 
# corresponding to ith class and jth features 

def removeFloats( class_prior_list , conditional_prob_list )
	numpy_frexp = np.vectorize( math.frexp )
	significand_list , exponents_list = numpy_frexp( class_prior_list.flatten() )
	min_exponent = min( exponents_list )
	significand_list , exponents_list = numpy_frexp( conditional_prob_list.flatten() )
	min_exponent = min( min_exponent , min( exponents_list ) )
	Multiplier = 2**( 52 - min_exponent )
	conditional_prob_list = conditional_prob_list * Multiplier
	class_prior_list = class_prior_list * Multiplier
	return class_prior_list , conditional_prob_list

def encrypt( class_prior_list , conditional_prob_list ):
	numpy_paillier = np.vectorize()
	return numpy_paillier( class_prior_list ) , numpy_paillier( conditional_prob_list )

def prepareBayesTables( class_prior_list , conditional_prob_list ):
	class_prior_list , conditional_prob_list  = removeFloats( class_prior_list , conditional_prob_list )
	class_prior_list , conditional_prob_list  = encrypt( class_prior_list , conditional_prob_list )
	return class_prior_list,conditional_prob_list

def getProbabilityTables():
	# either random generation or some other way to generate probability tables
	pass

####################################################################################################################

#client side functions

#mapping is a dictionary which tells the index of a value 'x' of the jth feature 
def computeClassProbs( input_vector , class_prior_list , conditional_prob_list , mapping):
	class_posterior_list = []
	for class_index in conditional_prob_list.shape[0]:
		class_prob = class_prior_list[ class_index ]
		for feature_index in conditional_prob_list.shape[1]:
			probabilities = conditional_prob_list[ class_index ][ feature_index ]
			feature_value = input_vector[ feature_index ]
			index = mapping[ feature_index ][ feature_value ]
			#below step equivalent to product in normal domain
			class_prob += class_prob , probabilities[ index ] 
		class_posterior_list.append(class_prob)	
	return np.array( class_posterior_list )	
		

def handle_argmax( input_vector ):
	#not finished yet
	pass

#client gets its final result from here , inputs of this function are taken through some client front connected to server
def RunBayesClassification( input_vector , class_prior_list , conditional_prob_list , mapping ):
	class_posterior_list = computeClassProbs( input_vector , class_prior_list , conditional_prob_list , mapping )
	best_class = handle_argmax( class_posterior_list )
	return best_class
