#include <sys/types.h> /* for system typedefs, e.g., time_t */
#include <stdlib.h>    /* for malloc(), atoi/f(), rand(), and getopt() */
/* Type definitions */

typedef unsigned long support_t;
typedef unsigned long wordnumber_t;
typedef unsigned long tableindex_t;

#define MAXWORDLEN 10248  /* maximum length of a word, should be
                             at least MAXLINELEN+4 */
struct elem {
  char *key;
  support_t count;
  wordnumber_t number;
  struct cluster *cluster;
  struct elem *next;
};

struct word {
  char *word;
  char variable;
  int head;
  int tail;
  struct word *next;
};

struct relative {
  struct cluster *cluster;
  struct relative *next;
};

struct cluster {
  int wordcount;
  int constants;
  support_t count;
  support_t support;
  char supported;
  struct elem *elem;
  struct relative *children;
  struct relative *parents;
  struct elem **wordptrs;
  struct word *words;
  struct cluster *next;
};

struct inputfile {
  char *name;
  struct inputfile *next;
};

struct templelem {
  char *str;
  int data;
  struct templelem *next;
};

struct slice {
  char *bitvector;
  struct cluster *begin;
  struct slice *next;
};

struct word_freq_stat {
  wordnumber_t ones;
  wordnumber_t twos;
  wordnumber_t fives;
  wordnumber_t tens;
  wordnumber_t twenties;
};

//Function Declaration
void log_msg(char *message);

tableindex_t str2hash(char *string, tableindex_t modulo, tableindex_t h);

int find_words(char *line, char (*words)[MAXWORDLEN]);

tableindex_t create_word_vector(void);

struct elem *add_elem(char *key, struct elem **table, tableindex_t tablesize, tableindex_t seed);

struct elem *find_elem(char *key, struct elem **table, tableindex_t tablesize, tableindex_t seed);

void free_table(struct elem **table, tableindex_t tablesize);

wordnumber_t create_vocabulary(void);

wordnumber_t find_frequent_words(struct word_freq_stat *stat);

tableindex_t create_cluster_vector(void);

wordnumber_t create_cluster_candidates(void);

wordnumber_t find_clusters(void);

void find_common(char *word1, char *word2, int *head, int *tail);

void refine_clusters(void);

void print_clusters(void);

void free_inputfiles(void);

void free_template(void);

void free_slices(void);

void free_clusters(void);

int parse_options(int argc, char **argv);

void print_usage(char *progname);

void mainFunction(int argc, char **argv);

