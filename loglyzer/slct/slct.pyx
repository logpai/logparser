from cpython.string cimport PyString_AsString
from libc.stdlib cimport *
from cslct cimport *
#from cslct import *

def process(input):
	content=input.split()
	length=len(content)
	cdef int c_argc=<int> length
	
	cdef char **c_argv = to_cstring_array(content)
	
	mainFunction(c_argc,c_argv)    #invoke the original C function
	
	free(c_argv)                  #free the allocated memory for argv

cdef char ** to_cstring_array(list_str):
	cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
	for i in xrange(len(list_str)):
		ret[i] = PyString_AsString(list_str[i])
	return ret

