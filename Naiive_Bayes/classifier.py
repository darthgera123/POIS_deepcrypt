import math
import numpy as np
from paillierlib import paillier
from gmpy2 import mpz
import random
import copy
from tqdm import tqdm
#################################################################################################################
#server side functions , all inputs are np arrays


#class_prior_list is a 1-d array of probabilities of classes
#conditional_prob_list is a 2-d array of 1-d lists , A[i][j] is a list of conditional probabilities 
# corresponding to ith class and jth features 

key_pair = paillier.keygen()

def typecast(x):
	return mpz(x)
def paillier_enc(x):
	global key_pair

	return paillier.encrypt( mpz(x) , key_pair.public_key)

def removeFloats( class_prior_list , conditional_prob_list ):

	numpy_frexp = np.vectorize( math.frexp )

	significand_list , exponents_list = numpy_frexp( class_prior_list.flatten() )

	min_exponent = min( exponents_list )

	significand_list , exponents_list = numpy_frexp( conditional_prob_list.flatten() )

	min_exponent = min( min_exponent , min( exponents_list ) )

	Multiplier = mpz( mpz(2)**( mpz(52 - min_exponent ) ) )


	numpy_cast = np.vectorize( typecast )
	
	conditional_prob_list = numpy_cast( conditional_prob_list )
	
	# print(conditional_prob_list)
	class_prior_list = numpy_cast( class_prior_list )

	conditional_prob_list = conditional_prob_list * Multiplier 
	# print(conditional_prob_list)

	class_prior_list = class_prior_list * Multiplier 

	return class_prior_list , conditional_prob_list


def encrypt( class_prior_list , conditional_prob_list ):
	numpy_enc = np.vectorize( paillier_enc )	

	l1 = numpy_enc( class_prior_list )
	x,y,z=conditional_prob_list.shape

	print(x,y,z)
	for i in tqdm(range(x)):
		for j in range(y):
			for k in range(z):
				v=conditional_prob_list[i][j][k]
				conditional_prob_list[i][j][k]=paillier_enc(v)

	return l1,conditional_prob_list

def prepareBayesTables( class_prior_list , conditional_prob_list ):
	class_prior_list , conditional_prob_list  = removeFloats( class_prior_list , conditional_prob_list )

	l1=copy.deepcopy(conditional_prob_list)
	print(l1[0][0][0],"ewg")
	class_prior_list , conditional_prob_list  = encrypt( class_prior_list , conditional_prob_list )

	print(l1[0][0][0],"weg")
	l2=conditional_prob_list
	print(l2[0][0][0])

	############################################
	#CHECK IF ENCRYPTION IS CORRECT
	global key_pair
	once = 0
	x,y,z=conditional_prob_list.shape
	for i in tqdm(range(x)):
		for j in range(y):
			for k in range(z):
				v1 = l1[i][j][k]
				v2 = paillier.decrypt(l2[i][j][k],key_pair.private_key)
				if v1 != v2 and once == 0:
					once = 1
					print(v1,v2)
	############################################


	return class_prior_list,conditional_prob_list

def fetchTables():
	mapping = []
	feature_values = []

	num_classes = 10
	num_features = 30
	dist_values_feature = 20

	for i in range(num_features):

		mapping.append({})
		values = []
		for j in range(dist_values_feature):
			rand_val = random.randint(0,1000)
			values.append( rand_val )

		feature_values.append(values)

	conditional_prob_list = []	
	class_prior_list = []	

	for i in range(num_classes):
		prob = random.uniform(0,1)
		class_prior_list.append( math.log( prob ) )
		class_list = []

		for j in range(num_features):

			num_feat_vals = len( feature_values[ j ] )
			flist = []

			for k in range(num_feat_vals):
				prob = random.uniform(0,1)
				flist.append( math.log( prob ) )
			class_list.append(flist)

		conditional_prob_list.append(class_list)		


	for f_list in feature_values:

		idx = 0	
		for val in f_list:
			mapping[ idx ][ val ] = idx
			idx += 1

	class_prior_list = np.array( class_prior_list )		
	conditional_prob_list = np.array( conditional_prob_list )	

	print(conditional_prob_list)
	return class_prior_list , conditional_prob_list		


def getProbabilityTables():
	class_prior_list , conditional_prob_list = fetchTables()
	class_prior_list , conditional_prob_list = prepareBayesTables(class_prior_list,conditional_prob_list)
	return class_prior_list,conditional_prob_list



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



l1 , l2 = getProbabilityTables()
print(l1,l2)