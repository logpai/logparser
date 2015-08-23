cdef extern from "cslct.h":
	ctypedef unsigned long support_t
	
	ctypedef unsigned long wordnumber_t

	ctypedef unsigned long tableindex_t
	
	ctypedef struct word_freq_stat:
		wordnumber_t ones
		wordnumber_t twos
		wordnumber_t fives
		wordnumber_t tens
		wordnumber_t twenties	
	ctypedef struct cluster:
		int wordcount
		int constants
		support_t count
		support_t support
		char supported
		elem *elem
		relative *children
		relative *parents
		elem **wordptrs
		word *words
		cluster *next
	ctypedef struct elem:
		char *key
		support_t count
		wordnumber_t number
		cluster *cluster
		elem *next
	ctypedef struct word:
		char *word
		char variable
		int head
		int tail
		word *next
	ctypedef struct relative:
		cluster *cluster
		relative *next
	ctypedef struct inputfile:
		char *name
		inputfile *next
	ctypedef struct templelem:
		char *str
		int data
		templelem *next
	ctypedef struct slice:
		char *bitvector
		cluster *begin
		slice *next
	

	void log_msg(char *message)

	tableindex_t str2hash(char *string, tableindex_t modulo, tableindex_t h)

	int find_words(char *line, char (*words))

	tableindex_t create_word_vector()

	elem *add_elem(char *key, elem **table, tableindex_t tablesize, tableindex_t seed)

	elem *find_elem(char *key, elem **table, tableindex_t tablesize, tableindex_t seed)

	void free_table(elem **table, tableindex_t tablesize)

	wordnumber_t create_vocabulary()

	wordnumber_t find_frequent_words(word_freq_stat *stat)

	tableindex_t create_cluster_vector()

	wordnumber_t create_cluster_candidates()

	wordnumber_t find_clusters()

	void find_common(char *word1, char *word2, int *head, int *tail)

	void refine_clusters()

	void print_clusters()

	void free_inputfiles()

	void free_template()

	void free_slices()

	void free_clusters()

	int parse_options(int argc, char **argv)
	
	void print_usage(char *progname)

	void mainFunction(int argc, char **argv)
