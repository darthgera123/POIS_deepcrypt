def get_bits(n, l):
	bits = []
	for i in range(l):
		bits.append(n & 1)
		n = n >> 1
	return bits

def faster(x,y,md=None):
	if md == None:
		return pow(x, y)

	res = 1
	x = x%md
	while y > 0: 
		if y%2 != 0 : 
			res = (res*x)%md 
		y = int(y/2) 
		x = (x*x)%md

	return res