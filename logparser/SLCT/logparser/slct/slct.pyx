from cpython.string cimport PyString_AsString
from libc.stdlib cimport *
from cslct cimport *

def extract(loglines, para):
	support=para['supportThreshold']
	datapath=para['dataPath']+para['dataName']
	parajTF=para['para_j']
	input=''
	if parajTF:
		input+='./slct -j -o '+'outliers.log -r -s '+str(support)+' '+loglines
	else:
		input+='./slct -o '+'outliers.log -r -s '+str(support)+' '+loglines

	print(input)
	content=input.split()
	length=len(content)
	cdef int c_argc=<int> length
	
	cdef char **c_argv = to_cstring_array(content)
	
	mainFunction(c_argc,c_argv)    #invoke the original C function
	del input
	free(c_argv)                  #free the allocated memory for argv

cdef char ** to_cstring_array(list_str):
	cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
	for i in xrange(len(list_str)):
		ret[i] = PyString_AsString(list_str[i])
	return ret

#########
#inputcmd="./slct -s 4 ../access_140901.log ../access_140803.log" 