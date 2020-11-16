import math
import numpy as np
from paillierlib import paillier
from gmpy2 import mpz
from gmpy2 import mpfr
import random
import copy
from tqdm import tqdm
from POIS_deepcrypt.Naiive_Bayes import ArgMax as ARG
#################################################################################################################
#server side functions , all inputs are np arrays


#class_prior_list is a 1-d array of probabilities of classes
#conditional_prob_list is a 2-d array of 1-d lists , A[i][j] is a list of conditional probabilities 
# corresponding to ith class and jth features 

key_pair = paillier.keygen()


def typecast_fl(x):
	return mpfr(x)
def typecast_int(x):
	return mpz(x)	
def paillier_enc(x):
	global key_pair

	return paillier.encrypt( mpz(x) , key_pair.public_key)

def removeFloats( class_prior_list , conditional_prob_list ):

	#print(class_prior_list)
	#print(conditional_prob_list)
	numpy_frexp = np.vectorize( math.frexp )

	significand_list , exponents_list = numpy_frexp( class_prior_list.flatten() )

	min_exponent = min( exponents_list )

	significand_list , exponents_list = numpy_frexp( conditional_prob_list.flatten() )

	min_exponent = min( min_exponent , min( exponents_list ) )

	pwr = 52 - min_exponent

	# #print( pwr )

	Multiplier = mpfr( mpfr(2)**( pwr ) )
	
	numpy_cast = np.vectorize( typecast_fl )
	
	conditional_prob_list = numpy_cast( conditional_prob_list )
	
	class_prior_list = numpy_cast( class_prior_list )

	conditional_prob_list = conditional_prob_list * Multiplier 

	class_prior_list = class_prior_list * Multiplier 

	numpy_cast = np.vectorize( typecast_int )

	conditional_prob_list = numpy_cast( conditional_prob_list )
	
	class_prior_list = numpy_cast( class_prior_list )

	#print(class_prior_list)
	#print(conditional_prob_list)

	return class_prior_list , conditional_prob_list


def encrypt( class_prior_list , conditional_prob_list ):
	numpy_enc = np.vectorize( paillier_enc )	

	l1 = numpy_enc( class_prior_list )
	x,y,z=conditional_prob_list.shape

	#print(x,y,z)
	for i in tqdm(range(x)):
		for j in range(y):
			for k in range(z):
				v=conditional_prob_list[i][j][k]
				conditional_prob_list[i][j][k]=paillier_enc(v)

	return l1,conditional_prob_list

def prepareBayesTables( class_prior_list , conditional_prob_list ):

	class_prior_list , conditional_prob_list  = removeFloats( class_prior_list , conditional_prob_list )


	class_prior_list , conditional_prob_list  = encrypt( class_prior_list , conditional_prob_list )


	l2=conditional_prob_list

	# ###########################################
	# # CHECK IF ENCRYPTION IS CORRECT
	# global key_pair
	# once = 0
	# x,y,z=conditional_prob_list.shape
	# for i in tqdm(range(x)):
	# 	for j in range(y):
	# 		for k in range(z):
	# 			v1 = l1[i][j][k]
	# 			v2 = paillier.decrypt(l2[i][j][k],key_pair.private_key)
	# 			if v1 != v2 and once == 0:
	# 				once = 1
	# 				#print(v1,v2)
	# ###########################################


	return class_prior_list,conditional_prob_list

def fetchTables():

	num_classes = 10
	num_features = 20
	dist_values_feature = 30


	conditional_prob_list = []	
	class_prior_list = []	

	for i in range(num_classes):
		prob = random.uniform(0,1)
		class_prior_list.append( math.log( prob ) )
		class_list = []

		for j in range(num_features):

			num_feat_vals = dist_values_feature 
			flist = []

			for k in range(num_feat_vals):
				prob = random.uniform(0,1)
				flist.append( math.log( prob ) )
			class_list.append(flist)

		conditional_prob_list.append(class_list)		


	class_prior_list = np.array( class_prior_list )		
	conditional_prob_list = np.array( conditional_prob_list )	

	return class_prior_list , conditional_prob_list		


def getProbabilityTables():
	class_prior_list , conditional_prob_list = fetchTables()
	clp_plain , cop_plain = copy.deepcopy(class_prior_list) , copy.deepcopy( conditional_prob_list )
	class_prior_list , conditional_prob_list = prepareBayesTables(class_prior_list,conditional_prob_list)
	return class_prior_list,conditional_prob_list,clp_plain,cop_plain



####################################################################################################################


def gx(x,f):
	global key_pair
	if f:
		return x
	return 	paillier.decrypt(x,key_pair.private_key)

#client side functions

#mapping is a dictionary which tells the index of a value 'x' of the jth feature 
def computeClassProbs( inp_vec , class_prior_list , conditional_prob_list , mapping , flag):
	class_posterior_list = []
	# #print(conditional_prob_list.shape)
	for class_index in range( conditional_prob_list.shape[0] ):

		class_prob = class_prior_list[ class_index ]
		# #print("**********************************************************")	
		# #print(gx(class_prior_list[ class_index ],flag),end='????????')
		for feature_index in range(conditional_prob_list.shape[1]):

			probabilities = conditional_prob_list[ class_index ][ feature_index ]

			feature_value = inp_vec[ feature_index ]

			index = mapping[ feature_index ][ feature_value ]

			class_prob = class_prob + probabilities[ index ] 
			# #print( index , probabilities[ index ] , feature_value )
			# #print( gx(probabilities[ index ],flag) ,end='??????????????????')

		# #print(gx(class_prob,flag))
		# #print("**********************************************************")	
		class_posterior_list.append(class_prob)	

	return np.array( class_posterior_list )	
		

def handle_argmax( inp_vec ):
	#not finished yet
	pass

def getFeatureValues():
	#Random generation
	feature_values = []
	mapping = []
	num_features = 20
	dist_values_feature = 30

	for i in range(num_features):
		mapping.append({})
		values = []
		for j in range(dist_values_feature):
			rand_val = random.randint(0,1000)
			values.append( rand_val )

		feature_values.append(values)

	ind = 0	
	for f_list in feature_values:
		idx = 0	
		for val in f_list:
			mapping[ ind ][ val ] = idx
			idx += 1
		ind += 1	

	return 	feature_values , mapping	


def genInput(mapping):
	#random input generated
	inp=[]
	for values in mapping:
		possible = []
		for key in values:
			possible.append(key)
		inp.append(random.choice(possible))	
	#print("weg",mapping,inp)
	return inp	


def Bayes():
	feature_values,mapping = getFeatureValues()

	inp_vec = genInput(mapping)

	#print(inp_vec,mapping)
	class_prior_list , conditional_prob_list , clp_plain , cop_plain = getProbabilityTables()

	class_posterior_list = computeClassProbs( inp_vec , class_prior_list , conditional_prob_list , mapping ,False)
	
	class_posterior_list_unenc = computeClassProbs( inp_vec , clp_plain , cop_plain , mapping ,True)

	global key_pair
	# for i in range(len(class_posterior_list_unenc)):
	# 	x = class_posterior_list_unenc[ i ]
	# 	y = paillier.decrypt( class_posterior_list[ i ] , key_pair.private_key )
	# 	#print(x,y)

	print("ON UNENCRYPTED DATA BEST CLASS IS:" , np.argmax(class_posterior_list_unenc) + 1)

	
	#print(class_posterior_list_unenc)

	idx = ARG.handler_A(np.array(class_posterior_list),75,key_pair.public_key,key_pair.private_key)
	print("ON ENCRYPTED DATA BEST CLASS IS:" , idx + 1 )

Bayes()


