/*
SLCT version 0.05 - slct
simple logfile clustering tool

Copyright (C) 2003-2007 Risto Vaarandi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

#include <stdio.h>     /* for fopen(), fread(), etc. */
#include <regex.h>     /* for regcomp() and regexec() */
#include <string.h>    /* for strcmp(), strcpy(), etc. */
#include <ctype.h>     /`for isspace() */
#include <unistd.h>    /* for getopt() on some platforms, e.g., Linux */
#include <time.h>      /* for time() and ctime() */
#include "cslct.h"
/* Constants */

#define MAXLINELEN 10240  /* maximum length of a line */
#define MAXWORDLEN 10248  /* maximum length of a word, should be
                             at least MAXLINELEN+4 */
#define MAXWORDS 512      /* maximum number of words in one line
                             (defined value must not exceed 2^16-1) */
#define MAXKEYLEN 20480   /* maximum hash key length in cluster hash table */
#define CLUSTERSEP '\n'   /* separator character used for building
                             hash keys of the cluster hash table */
#define MAXLOGMSGLEN 256  /* maximum log message length */
#define BACKREFCHAR '$'   /* character that starts backreference variables */
#define MAXPARANEXPR 100  /* maximum number of () expressions in regexp */

const char num2str[16] = { '0', '1', '2', '3', '4', '5', '6', '7',
                           '8', '9', 'A', 'B', 'C', 'D', 'E', 'F' };

/* Global variables */

char *DELIM, *FILTER;
regex_t DELIM_REGEX, FILTER_REGEX;

support_t SUPPORT;
double PCTSUPPORT;

char JOIN;
char REFINE;
int BYTEOFFSET;

struct inputfile *INPUTFILES;
char *OUTLIERFILE;

unsigned int INITSEED;

support_t *VECTOR;
tableindex_t VECTORSIZE;
tableindex_t VECTORSEED;

support_t *CLUSTERVECTOR;
tableindex_t CLUSTERVECTORSIZE;
tableindex_t CLUSTERVECTORSEED;

struct elem **WORDTABLE;
tableindex_t WORDTABLESIZE;
tableindex_t WORDTABLESEED;

struct elem **CLUSTERTABLE;
tableindex_t CLUSTERTABLESIZE;
tableindex_t CLUSTERTABLESEED;

struct cluster *CLUSTERS;
struct templelem *TEMPLATE;

struct cluster *POINTERS[MAXWORDS];
struct slice *SLICES[MAXWORDS];

wordnumber_t WORDNUM;
wordnumber_t SLICESIZE;

/* Functions */

void log_msg(char *message)
{
  time_t t;
  char *timestamp;

  t = time(0);
  timestamp = ctime(&t);
  timestamp[strlen(timestamp) - 1] = 0;
  fprintf(stderr, "%s: %s\n", timestamp, message);
}


tableindex_t str2hash(char *string, tableindex_t modulo, tableindex_t h)
{
  int i;

  /* fast string hashing algorithm by M.V.Ramakrishna and Justin Zobel */
  for (i = 0; string[i] != 0; ++i) {
    h = h ^ ((h << 5) + (h >> 2) + string[i]);
  }

  return h % modulo;
}


int find_words(char *line, char (*words)[MAXWORDLEN])
{
  regmatch_t match[MAXPARANEXPR];
  int i, j, linelen, len;
  struct templelem *ptr;
  char *buffer;
  
  if (*line == 0)  { return 0; }
  
  linelen = strlen(line);

  if (BYTEOFFSET >= linelen)  { return 0; }

  if (BYTEOFFSET) {
    line += BYTEOFFSET;
    linelen -= BYTEOFFSET;
  }
  
  if (FILTER) {
 
    if (regexec(&FILTER_REGEX, line, MAXPARANEXPR, match, 0))  { return 0; }
    
    if (TEMPLATE) {
    
      len = 0;
      
      for (ptr = TEMPLATE; ptr; ptr = ptr->next) {
        if (ptr->str) {
          len += ptr->data;
        } else if (!ptr->data) {
          len += linelen;
        } else if (match[ptr->data].rm_so != -1  &&
                   match[ptr->data].rm_eo != -1) {
          len += match[ptr->data].rm_eo - match[ptr->data].rm_so;
        }
      }
      
      i = 0;
      buffer = (char *) malloc(len + 1);
      if (!buffer)  { log_msg("malloc() failed!"); exit(1); }
        
      for (ptr = TEMPLATE; ptr; ptr = ptr->next) {

        if (ptr->str) {
          strncpy(buffer + i, ptr->str, ptr->data);
          i += ptr->data;
        } else if (!ptr->data) {
          strncpy(buffer + i, line, linelen);
          i += linelen;
        } else if (match[ptr->data].rm_so != -1  &&
                   match[ptr->data].rm_eo != -1) {
          len = match[ptr->data].rm_eo - match[ptr->data].rm_so;
          strncpy(buffer + i, line + match[ptr->data].rm_so, len);
          i += len;
        }

      }
      
      buffer[i] = 0;
      line = buffer;

    }
    
  }
    
  for (i = 0; i < MAXWORDS; ++i) {

    if (regexec(&DELIM_REGEX, line, 1, match, 0)) {

      words[i][0] = num2str[((i + 1) >> 12) & 0xF];
      words[i][1] = num2str[((i + 1) >> 8) & 0xF];
      words[i][2] = num2str[((i + 1) >> 4) & 0xF];
      words[i][3] = num2str[(i + 1) & 0xF];

      for (j = 0; line[j] != 0; ++j)  { words[i][j+4] = line[j]; }
      words[i][j+4] = 0;

      break; 

    }

    words[i][0] = num2str[((i + 1) >> 12) & 0xF];
    words[i][1] = num2str[((i + 1) >> 8) & 0xF];
    words[i][2] = num2str[((i + 1) >> 4) & 0xF];
    words[i][3] = num2str[(i + 1) & 0xF];

    for (j = 0; j < match[0].rm_so; ++j)  { words[i][j+4] = line[j]; }
    words[i][j+4] = 0;

    line += match[0].rm_eo;

    if (*line == 0)  { break; }

  }

  if (TEMPLATE)  { free((void *) buffer); }
  
  if (i == MAXWORDS) { return i; }  else { return i+1; }
}


tableindex_t create_word_vector(void)
{
  FILE *file;
  struct inputfile *fileptr;
  char line[MAXLINELEN];
  char words[MAXWORDS][MAXWORDLEN];
  int len, i, wordcount;
  tableindex_t hash, j, oversupport;
  char logstr[MAXLOGMSGLEN];
  support_t linecount;

  linecount = 0;
    
  for (j = 0; j < VECTORSIZE; ++j)  { VECTOR[j] = 0; }

  for (fileptr = INPUTFILES; fileptr; fileptr = fileptr->next) {
  
    if (!(file = fopen(fileptr->name, "r"))) {
      sprintf(logstr, "Can't open inputfile %s", fileptr->name);
      log_msg(logstr);
      continue;
    }

    while (fgets(line, MAXLINELEN, file)) {

      len = strlen(line);
      if (line[len-1] == '\n')  { line[len-1] = 0; }

      wordcount = find_words(line, words);

      for (i = 0; i < wordcount; ++i)  { 

        if (words[i][4] == 0)  { continue; }
        hash = str2hash(words[i], VECTORSIZE, VECTORSEED);
        ++VECTOR[hash];
                  
      }
    
      ++linecount;

    }

    fclose(file);
    
  }

  if (!SUPPORT)  { SUPPORT = linecount * PCTSUPPORT / 100; }
  
  oversupport = 0;
  
  for (j = 0; j < VECTORSIZE; ++j) { 
    if (VECTOR[j] >= SUPPORT)  { ++oversupport; }
  }

  return oversupport;
}


struct elem *add_elem(char *key, struct elem **table, 
                      tableindex_t tablesize, tableindex_t seed)
{
  tableindex_t hash;
  struct elem *ptr, *prev;
  
  hash = str2hash(key, tablesize, seed);

  if (table[hash]) {

    prev = 0;
    ptr = table[hash];
                      
    while (ptr) { 
      if (!strcmp(key, ptr->key))  { break; } 
      prev = ptr;
      ptr = ptr->next;
    }

    if (ptr) {
        
      ++ptr->count; 

      if (prev) {
        prev->next = ptr->next;
        ptr->next = table[hash];
        table[hash] = ptr;
      }
          
    } else {
        
      ptr = (struct elem *) malloc(sizeof(struct elem));
      if (!ptr)  { log_msg("malloc() failed!"); exit(1); }
      
      ptr->key = (char *) malloc(strlen(key) + 1);
      if (!ptr->key)  { log_msg("malloc() failed!"); exit(1); }
      
      strcpy(ptr->key, key);
      ptr->count = 1;
      ptr->next = table[hash];
      table[hash] = ptr;
          
    }
                  
  } else {
             
    ptr = (struct elem *) malloc(sizeof(struct elem));
    if (!ptr)  { log_msg("malloc() failed!"); exit(1); }
    
    ptr->key = (char *) malloc(strlen(key) + 1);
    if (!ptr->key)  { log_msg("malloc() failed!"); exit(1); }
    
    strcpy(ptr->key, key);
    ptr->count = 1;
    ptr->next = 0;
    table[hash] = ptr;
            
  }
  
  return ptr;
}


struct elem *find_elem(char *key, struct elem **table, 
                       tableindex_t tablesize, tableindex_t seed)
{
  tableindex_t hash;
  struct elem *ptr, *prev;
  
  prev = 0;
  hash = str2hash(key, tablesize, seed);

  for (ptr = table[hash]; ptr; ptr = ptr->next) {
    if (!strcmp(key, ptr->key))  { break; } 
    prev = ptr;
  }

  if (ptr && prev) {
    prev->next = ptr->next;
    ptr->next = table[hash];
    table[hash] = ptr;
  }
  
  return ptr;
}


void free_table(struct elem **table, tableindex_t tablesize)
{
  tableindex_t i;
  struct elem *ptr, *next;

  for (i = 0; i < tablesize; ++i) {

    if (!table[i])  { continue; }

    ptr = table[i];

    while (ptr) {

      next = ptr->next;
                
      free((void *) ptr->key);
      free((void *) ptr);

      ptr = next;
      
    }

  }
  
  free((void *) table);
}


wordnumber_t create_vocabulary(void)
{
  FILE *file;
  struct inputfile *fileptr;
  char line[MAXLINELEN];
  char words[MAXWORDS][MAXWORDLEN];
  int len, i, wordcount;
  tableindex_t hash, j;
  char logstr[MAXLOGMSGLEN];
  struct elem *word;
  support_t linecount;
  wordnumber_t number;

  number = 0;  
  linecount = 0;
    
  for (j = 0; j < WORDTABLESIZE; ++j)  { WORDTABLE[j] = 0; }
  
  for (fileptr = INPUTFILES; fileptr; fileptr = fileptr->next) {
  
    if (!(file = fopen(fileptr->name, "r"))) {
      sprintf(logstr, "Can't open inputfile %s", fileptr->name);
      log_msg(logstr);
      continue;
    }
  
    while (fgets(line, MAXLINELEN, file)) {

      len = strlen(line);
      if (line[len-1] == '\n')  { line[len-1] = 0; }

      wordcount = find_words(line, words);

      for (i = 0; i < wordcount; ++i)  { 

        if (words[i][4] == 0)  { continue; }

        if (VECTORSIZE) {
          hash = str2hash(words[i], VECTORSIZE, VECTORSEED);
          if (VECTOR[hash] < SUPPORT)  { continue; }      
        }
      
        word = add_elem(words[i], WORDTABLE, WORDTABLESIZE, WORDTABLESEED);

        if (word->count == 1)  { ++number; }

      }
    
      ++linecount;

    }

    fclose(file);
    
  }
  
  if (!SUPPORT)  { SUPPORT = linecount * PCTSUPPORT / 100; }

  return number;
}


wordnumber_t find_frequent_words(struct word_freq_stat *stat)
{
  tableindex_t i;
  wordnumber_t number;
  struct elem *ptr, *prev, *next;

  number = 0;

  stat->ones = 0;
  stat->twos = 0;
  stat->fives = 0;
  stat->tens = 0;
  stat->twenties = 0;

  for (i = 0; i < WORDTABLESIZE; ++i) {

    if (!WORDTABLE[i])  { continue; }

    prev = 0;
    ptr = WORDTABLE[i];

    while (ptr) {

      if (ptr->count == 1) { ++stat->ones; }
      if (ptr->count <= 2) { ++stat->twos; }
      if (ptr->count <= 5) { ++stat->fives; }
      if (ptr->count <= 10) { ++stat->tens; }
      if (ptr->count <= 20) { ++stat->twenties; }

      if (ptr->count < SUPPORT) {

        if (prev) { 
          prev->next = ptr->next; 
        } else { 
          WORDTABLE[i] = ptr->next; 
        }

        next = ptr->next;
                
        free((void *) ptr->key);
        free((void *) ptr);

        ptr = next;
        
      } else {

        ptr->number = ++number;
        prev = ptr;
        ptr = ptr->next;
                        
      }
       
    }
    
  }

  return number;
}


tableindex_t create_cluster_vector(void)
{
  FILE *file;
  struct inputfile *fileptr;
  char line[MAXLINELEN];
  char key[MAXKEYLEN];
  char words[MAXWORDS][MAXWORDLEN];
  struct elem *word;
  int len, i, last, wordcount;
  tableindex_t hash, j, oversupport;
  char logstr[MAXLOGMSGLEN];
  
  for (j = 0; j < CLUSTERVECTORSIZE; ++j)  { CLUSTERVECTOR[j] = 0; }

  for (fileptr = INPUTFILES; fileptr; fileptr = fileptr->next) {
  
    if (!(file = fopen(fileptr->name, "r"))) {
      sprintf(logstr, "Can't open inputfile %s", fileptr->name);
      log_msg(logstr);
      continue;
    }
   
    while (fgets(line, MAXLINELEN, file)) {

      len = strlen(line);
      if (line[len-1] == '\n')  { line[len-1] = 0; }

      wordcount = find_words(line, words);

      last = 0;
      *key = 0;
    
      for (i = 0; i < wordcount; ++i) { 

        word = find_elem(words[i], WORDTABLE, WORDTABLESIZE, WORDTABLESEED);
      
        if (words[i][4] != 0  &&  word) {

          strcat(key, words[i]);
          len = strlen(key);
          key[len] = CLUSTERSEP;      
          key[len+1] = 0;

          last = i + 1;

        }

      }

      if (!last)  { continue; }
    
      hash = str2hash(key, CLUSTERVECTORSIZE, CLUSTERVECTORSEED);
      ++CLUSTERVECTOR[hash];
      
    }
    
    fclose(file);
  
  }  
  
  oversupport = 0;
  
  for (j = 0; j < CLUSTERVECTORSIZE; ++j) { 
    if (CLUSTERVECTOR[j] >= SUPPORT)  { ++oversupport; }
  }

  return oversupport;
}


wordnumber_t create_cluster_candidates(void)
{
  FILE *file;
  struct inputfile *fileptr;
  char line[MAXLINELEN];
  char key[MAXKEYLEN];
  char words[MAXWORDS][MAXWORDLEN];
  struct elem *pointers[MAXWORDS];
  int len, i, last, wordcount, constants, l;
  tableindex_t hash, j;
  struct elem *word, *elem;
  struct cluster *ptr, *end;
  struct slice *slice, *prev;
  char logstr[MAXLOGMSGLEN], match;
  wordnumber_t clustercount, bitvecsize, k, m, offset;
  char offset2;

  for (i = 0; i < MAXWORDS; ++i)  { POINTERS[i] = 0; SLICES[i] = 0; }  
  for (j = 0; j < CLUSTERTABLESIZE; ++j)  { CLUSTERTABLE[j] = 0; }

  CLUSTERS = 0;
  clustercount = 0;
    
  for (fileptr = INPUTFILES; fileptr; fileptr = fileptr->next) {
  
    if (!(file = fopen(fileptr->name, "r"))) {
      sprintf(logstr, "Can't open inputfile %s", fileptr->name);
      log_msg(logstr);
      continue;
    }
   
    while (fgets(line, MAXLINELEN, file)) {

      len = strlen(line);
      if (line[len-1] == '\n')  { line[len-1] = 0; }

      wordcount = find_words(line, words);

      last = 0;
      *key = 0;
      constants = 0;
          
      for (i = 0; i < wordcount; ++i) { 

        word = find_elem(words[i], WORDTABLE, WORDTABLESIZE, WORDTABLESEED);
      
        if (words[i][4] != 0  &&  word) {

          strcat(key, words[i]);
          len = strlen(key);
          key[len] = CLUSTERSEP;      
          key[len+1] = 0;

          last = i + 1;
          pointers[i] = word;
          ++constants;
          
        } else { pointers[i] = 0; }

      }

      if (!last)  { continue; }

      if (CLUSTERVECTORSIZE) {
        hash = str2hash(key, CLUSTERVECTORSIZE, CLUSTERVECTORSEED);
        if (CLUSTERVECTOR[hash] < SUPPORT)  { continue; }      
      }
    
      elem = add_elem(key, CLUSTERTABLE, CLUSTERTABLESIZE, CLUSTERTABLESEED);

      if (elem->count > 1)  { continue; }
 
      ptr = (struct cluster *) malloc(sizeof(struct cluster));
      if (!ptr)  { log_msg("malloc() failed!"); exit(1); }

      if (POINTERS[constants-1]) {
        ptr->next = POINTERS[constants-1];
        POINTERS[constants-1] = ptr;
      } else {
	ptr->next = 0;
        POINTERS[constants-1] = ptr;
      }

      ptr->support = 0;
      ptr->supported = 0;
      ptr->children = 0;
      ptr->parents = 0;

      ptr->wordcount = last;
      ptr->words = 0;

      ptr->constants = constants;
                    
      ptr->elem = elem;
      elem->cluster = ptr;
    
      ptr->wordptrs = (struct elem **) malloc(last * sizeof(struct elem *));

      for (i = 0; i < last; ++i)  { ptr->wordptrs[i] = pointers[i]; }

      ++clustercount;
            
    }

    fclose(file);
    
  }

  if (JOIN) {
    prev = 0;
    bitvecsize = (WORDNUM - 1) / 8 + 1;
    if (!SLICESIZE)  { SLICESIZE = clustercount / 100 + 1; }
  }
  
  for (i = 0; i < MAXWORDS; ++i) {

    if (!POINTERS[i])  { continue; }

    if (JOIN) {
    
      k = 0;
        
      for (ptr = POINTERS[i]; ptr; ptr = ptr->next) {

        if (!(k % SLICESIZE)) {

          if (SLICES[i]) {
            slice->next = (struct slice *) malloc(sizeof(struct slice));
            slice = slice->next;
          } else {
            SLICES[i] = (struct slice *) malloc(sizeof(struct slice));
            slice = SLICES[i];
            if (prev)  { prev->next = slice; }
          }

          slice->bitvector = (char *) malloc(bitvecsize);
          for (m = 0; m < bitvecsize; ++m)  { slice->bitvector[m] = 0; }
          slice->begin = ptr;
          slice->next = 0;
          prev = slice;
        }

        for (l = 0; l < ptr->wordcount; ++l) {
          if (!ptr->wordptrs[l]) { continue; }
          offset = (ptr->wordptrs[l]->number - 1) / 8;
          offset2 = (ptr->wordptrs[l]->number - 1) % 8;
          slice->bitvector[offset] |= (1 << offset2);
        }

        ++k;
      }
      
    }
    
    if (CLUSTERS) { end->next = POINTERS[i]; } 
      else { CLUSTERS = POINTERS[i]; }

    for (end = POINTERS[i]; end->next; end = end->next);
  }

  for (ptr = CLUSTERS; ptr; ptr = ptr->next) {
    ptr->count = ptr->elem->count;
  }
                                  
  return clustercount;  
}


wordnumber_t find_clusters(void)
{
  struct cluster *ptr1, *ptr2;
  struct word *ptr3;
  struct relative *child, *parent;
  struct slice *slice;
  int i, wordcount;
  wordnumber_t clustercount, offset;
  char match, offset2;

  for (ptr1 = CLUSTERS; ptr1; ptr1 = ptr1->next) {
  
    ptr1->parents = (struct relative *) malloc(sizeof(struct relative));
    if (!ptr1->parents)  { log_msg("malloc() failed!"); exit(1); }
    ptr1->parents->cluster = ptr1;
    ptr1->parents->next = 0;
    
    ptr1->children = (struct relative *) malloc(sizeof(struct relative));
    if (!ptr1->children)  { log_msg("malloc() failed!"); exit(1); }
    ptr1->children->cluster = ptr1;
    ptr1->children->next = 0;
    
    ptr1->support = ptr1->count;
    
  }

  if (JOIN) {

    for (ptr1 = CLUSTERS; ptr1; ptr1 = ptr1->next) {

      child = ptr1->children;
      for (i = ptr1->constants; !POINTERS[i] && i < MAXWORDS; ++i);
      if (i == MAXWORDS) { continue; }
      
      slice = SLICES[i];
      ptr2 = POINTERS[i];
                    
      while (ptr2) {
      
        wordcount = ptr1->wordcount;    
        match = 1;

        if (slice  &&  slice->begin == ptr2) {
        
          for (i = 0; i < wordcount; ++i) {
          
            if (!ptr1->wordptrs[i])  { continue; }
            offset = (ptr1->wordptrs[i]->number - 1) / 8;
            offset2 = (ptr1->wordptrs[i]->number - 1) % 8;
            
            if (!(slice->bitvector[offset] & (1 << offset2))) {
              match = 0;
              break;
            }
          }
          
          slice = slice->next;
          
          if (!match) {
            if (slice) {
              ptr2 = slice->begin;
              continue;
            } else { 
              break; 
            }
          }

        }
        
        if (ptr1->wordcount > ptr2->wordcount) { 
          ptr2 = ptr2->next; 
          continue; 
        }

        match = 1;

        for (i = 0; i < wordcount; ++i) {

          if (!ptr1->wordptrs[i])  { continue; }
          
          if (!ptr2->wordptrs[i]  ||
               ptr1->wordptrs[i]->number != ptr2->wordptrs[i]->number) {
            match = 0;
            break;
          }
        }

        if (match) { 

          child->next = (struct relative *) malloc(sizeof(struct relative));
          if (!child->next)  { log_msg("malloc() failed!"); exit(1); }
          child = child->next;
        
          child->cluster = ptr2;
          child->next = 0;
        
          for (parent = ptr2->parents; parent->next; parent = parent->next);
          parent->next = (struct relative *) malloc(sizeof(struct relative));
          if (!parent->next)  { log_msg("malloc() failed!"); exit(1); }
          parent = parent->next;
        
          parent->cluster = ptr1;
          parent->next = 0;
        
          ptr1->support += ptr2->count; 
        
        }
        
        ptr2 = ptr2->next;
        
      }
      
    }
    
  }

  clustercount = 0;

  for (ptr1 = CLUSTERS; ptr1; ptr1 = ptr1->next) {
  
    if (ptr1->support >= SUPPORT) {

      ptr3 = 0;

      for (i = 0; i < ptr1->wordcount; ++i) {

        if (ptr3) {
          ptr3->next = (struct word *) malloc(sizeof(struct word));
          if (!ptr3->next)  { log_msg("malloc() failed!"); exit(1); }
          ptr3 = ptr3->next;
        } else {
          ptr1->words = (struct word *) malloc(sizeof(struct word)); 
          if (!ptr1->words)  { log_msg("malloc() failed!"); exit(1); }
          ptr3 = ptr1->words;
        }

        if (ptr1->wordptrs[i]) {
          ptr3->word = ptr1->wordptrs[i]->key + 4;
          ptr3->variable = 0;
        } else { 
          ptr3->word = 0;
          ptr3->variable = 1;
        }
      
      }

      ptr3->next = 0;
    
      for (child = ptr1->children; child; child = child->next) {
         child->cluster->supported = 1;
      }
      
      ++clustercount;
      
    }
  
    free((void *) ptr1->wordptrs);
      
  }

  return clustercount;
}


void find_common(char *word1, char *word2, int *head, int *tail)
{
  int i, p1, p2;

  for (i = 0; i < *head && word1[i] && word2[i]; ++i) {
    if (word1[i] != word2[i])  { break; }
  }
  
  *head = i;
  
  p1 = strlen(word1) - 1;
  p2 = strlen(word2) - 1;
  
  if (p1 < p2) { i = p1; } else { i = p2; }

  while (p1 >= *tail  &&  i >= 0) {
  
    if (word1[p1] != word2[p2])  { break; }

    --i;    
    --p1;
    --p2;
    
  }
  
  *tail = p1 + 1;
}


void refine_clusters(void)
{
  FILE *file, *outliers;
  struct inputfile *fileptr;
  char line[MAXLINELEN];
  char key[MAXKEYLEN];
  char words[MAXWORDS][MAXWORDLEN];
  int len, i, temp, wordcount;
  struct elem *word, *elem;
  struct cluster *ptr;
  struct word *ptr2, *next, *prev;
  struct relative *parent;
  char logstr[MAXLOGMSGLEN];
  //============================
  int count=0;
  //============================
  if (OUTLIERFILE  &&  !(outliers = fopen(OUTLIERFILE, "w"))) {
    sprintf(logstr, "Can't open outliers file %s", OUTLIERFILE);
    log_msg(logstr);
    exit(1);
  }
  
  for (ptr = CLUSTERS; ptr; ptr = ptr->next)  { ptr->wordcount = -1; }
  
  for (fileptr = INPUTFILES; fileptr; fileptr = fileptr->next) {

    if (!(file = fopen(fileptr->name, "r"))) {
      sprintf(logstr, "Can't open inputfile %s", fileptr->name);
      log_msg(logstr);
      continue;
    }
    
    while (fgets(line, MAXLINELEN, file)) {
       
	count++;
 	//============================
      len = strlen(line);
      if (line[len-1] == '\n')  { line[len-1] = 0; }

      wordcount = find_words(line, words);

      *key = 0;
    
      for (i = 0; i < wordcount; ++i) { 

        word = find_elem(words[i], WORDTABLE, WORDTABLESIZE, WORDTABLESEED);
      
        if (words[i][4] != 0  &&  word) {
          strcat(key, words[i]);
          len = strlen(key);
          key[len] = CLUSTERSEP;      
          key[len+1] = 0;
        }

      }

      if (*key == 0) {
        if (OUTLIERFILE  &&  wordcount) 
		{
//============================
 fprintf(outliers, "%d\t", count); 
//============================
fprintf(outliers, "%s\n", line);
              }
        continue;
      }
    
      elem = find_elem(key, CLUSTERTABLE, CLUSTERTABLESIZE, CLUSTERTABLESEED);

      if (!elem  ||  !elem->cluster->supported) { 
        if (OUTLIERFILE)  {
//============================
 fprintf(outliers, "%d\t", count); 
//============================
 fprintf(outliers, "%s\n", line); }
        continue; 
      }

      for (parent = elem->cluster->parents; parent; parent = parent->next) {

        ptr = parent->cluster;
      
        if (ptr->support < SUPPORT)  { continue; }
        
        if (ptr->wordcount == -1) {
        
          ptr->wordcount = wordcount;
          temp = wordcount;
          i = 0;
                
          for (ptr2 = ptr->words; ptr2; ptr2 = ptr2->next) {

            if (ptr2->variable) {
              len = strlen(words[i]+4);
              ptr2->word = (char *) malloc(len + 1);
              if (!ptr2->word)  { log_msg("malloc() failed!"); exit(1); }
              strcpy(ptr2->word, words[i]+4);
              ptr2->head = len;
              ptr2->tail = 0;
            }
          
            prev = ptr2;
            --temp;
            ++i;
        
          }

          ptr2 = prev;
        
          while (temp > 0) {

            ptr2->next = (struct word *) malloc(sizeof(struct word));
            if (!ptr2->next)  { log_msg("malloc() failed!"); exit(1); }
            ptr2 = ptr2->next;
         
            ptr2->variable = 1;
           
            len = strlen(words[i]+4);
            ptr2->word = (char *) malloc(len + 1);
            if (!ptr2->word)  { log_msg("malloc() failed!"); exit(1); }
            strcpy(ptr2->word, words[i]+4);
            ptr2->head = len;
            ptr2->tail = 0;

            --temp;    
            ++i;
            
          }

          ptr2->next = 0;    
   
        } else {
    
          if (wordcount < ptr->wordcount) {

            ptr->wordcount = wordcount;
            i = 1;
          
            for (ptr2 = ptr->words; ptr2; ptr2 = ptr2->next) {
              if (i == wordcount)  { break; }  else { ++i; }
            }
          
            next = ptr2->next;
            ptr2->next = 0;
            ptr2 = next;
          
            while (ptr2) {
              next = ptr2->next;
              free((void *) ptr2->word);
              free((void *) ptr2);
              ptr2 = next;
            }
          
          }        
        
          i = 0;
        
          for (ptr2 = ptr->words; ptr2; ptr2 = ptr2->next) {

            if (ptr2->variable  &&  ptr2->word) { 
          
              find_common(ptr2->word, words[i]+4, &ptr2->head, &ptr2->tail);
            
              if (ptr2->head >= ptr2->tail) {
                free((void *) ptr2->word);
                ptr2->word = 0;
              }
            
            }
          
            ++i;
          
          }
        
        }
      
      }
    
    }
    
    fclose(file);    
  }

  if (OUTLIERFILE)  { fclose(outliers); }
}


void print_clusters(void)
{
  char logstr[MAXWORDLEN] = "";
  char temp[300];
  char buffer[MAXWORDLEN];
  FILE *outputfile = fopen("slct_templates.txt", "w");
  struct cluster *ptr;
  struct word *ptr2;
  if (outputfile == NULL){
   sprintf(logstr, "Can't open templates file");
   log_msg(logstr);
   exit(1);
  }
  for (ptr = CLUSTERS; ptr; ptr = ptr->next) {

    if (ptr->support < SUPPORT) { continue; }
    
    for (ptr2 = ptr->words; ptr2; ptr2 = ptr2->next) 
    {
      if (ptr2->variable) 
      { 
        if (ptr2->word)
         {
          if (ptr2->tail >= ptr2->head) 
          {
            strncpy(buffer, ptr2->word, ptr2->head);
            buffer[ptr2->head] = 0;
            sprintf(temp, "%s<*>%s ", buffer, ptr2->word + ptr2->tail);
            strcat(logstr, temp);
          } 
          else
          {
            sprintf(temp,"%s ", ptr2->word);    
            strcat(logstr, temp);
          }
        } 
        else
        { 
           sprintf(temp, "<*> ");
           strcat(logstr, temp);
        }
      }
      else { 
           sprintf(temp,"%s ", ptr2->word);
           strcat(logstr, temp);
      }
    }
    fprintf(outputfile,"%s\n", logstr);
    //fprintf(outputfile, "\nSupport: %lu\n\n", ptr->support);
    memset(&logstr[0], 0, sizeof(logstr));
  }
  logstr[0] = '\0';
  fclose(outputfile);
}


//Original print_cluster
// void print_clusters(void)
// {
//   char buffer[MAXWORDLEN];
//   struct cluster *ptr;
//   struct word *ptr2;

//   for (ptr = CLUSTERS; ptr; ptr = ptr->next) {

//     if (ptr->support < SUPPORT)  { continue; }
    
//     for (ptr2 = ptr->words; ptr2; ptr2 = ptr2->next) {

//       if (ptr2->variable) { 

//         if (ptr2->word) {

//           if (ptr2->tail >= ptr2->head) {
//             strncpy(buffer, ptr2->word, ptr2->head);
//             buffer[ptr2->head] = 0;
//             printf("%s*%s ", buffer, ptr2->word + ptr2->tail);
//           } else {
//             printf("%s ", ptr2->word);
//           }

//         } else { printf("* ");}

//       } else { printf("%s ", ptr2->word);}
    
//     }
    
//     printf("\nSupport: %lu\n\n", ptr->support);
    
//   }
// }


void free_inputfiles(void)
{
  struct inputfile *ptr, *next;

  ptr = INPUTFILES;

  while (ptr) {
    next = ptr->next;
    free((void *) ptr->name);
    free((void *) ptr);
    ptr = next;
  }
}


void free_template(void)
{
  struct templelem *ptr, *next;

  ptr = TEMPLATE;

  while (ptr) {
    next = ptr->next;
    free((void *) ptr->str);
    free((void *) ptr);
    ptr = next;
  }
}


void free_slices(void)
{
  struct slice *slice, *next;
  int i;
  
  for (i = 0; i < MAXWORDS; ++i) {
    if (SLICES[i])  { break; }
  }

  if (i == MAXWORDS)  { return; }

  slice = SLICES[i];
      
  while (slice) {
    next = slice->next;
    free((void *) slice->bitvector);
    free((void *) slice);
    slice = next;      
  }
}


void free_clusters(void)
{
  struct cluster *cluster;
  struct relative *relative;
  struct word *word;
  void *next;
  
  cluster = CLUSTERS;
  
  while (cluster) {
  
    relative = cluster->parents;
    
    while (relative) {
      next = relative->next;
      free ((void *) relative);
      relative = next;
    }
    
    relative = cluster->children;
    
    while (relative) {
      next = relative->next;
      free ((void *) relative);
      relative = next;
    }
    
    word = cluster->words;

    while (word) {
      next = word->next;
      if (word->variable  &&  word->word)  { free ((void *) word->word); } 
      free ((void *) word);
      word = next;
    }
    
    next = cluster->next;
    free((void *) cluster);
    cluster = next;
    
  }
  
}


int parse_options(int argc, char **argv)
{
  extern char *optarg;
  extern int optind;
  int c, i, start, len;
  struct templelem *template;
  struct inputfile *ptr;
  char *addr;
  while ((c = getopt(argc, argv, "b:c:d:f:g:i:jo:rs:t:v:w:z:")) != -1) {
    switch(c) { 
    case 'b':
      BYTEOFFSET = atoi(optarg);
      break;
    case 'c':
      CLUSTERTABLESIZE = atoi(optarg);
      break;
    case 'd':
      DELIM = (char *) malloc(strlen(optarg) + 1);
      if (!DELIM)  { log_msg("malloc() failed!"); exit(1); }
      strcpy(DELIM, optarg);
      break;
    case 'f':
      FILTER = (char *) malloc(strlen(optarg) + 1);
      if (!FILTER)  { log_msg("malloc() failed!"); exit(1); }
      strcpy(FILTER, optarg);
      break;
    case 'g':
      SLICESIZE = atoi(optarg);
      break;
    case 'i':
      INITSEED = atoi(optarg);
      break;
    case 'j':
      JOIN = 1;
      break;
    case 'o':
      OUTLIERFILE = (char *) malloc(strlen(optarg) + 1);
      if (!OUTLIERFILE)  { log_msg("malloc() failed!"); exit(1); }
      strcpy(OUTLIERFILE, optarg);
      break;
    case 'r':
      REFINE = 1;
      break;
    case 's':
      if (optarg[strlen(optarg) - 1] == '%') { 
        PCTSUPPORT = atof(optarg); 
      } else { 
        SUPPORT = atoi(optarg);
      }
      break;
    case 't':
      i = 0;
      while (optarg[i]) {
        if (TEMPLATE) {
          template->next = (struct templelem *) malloc(sizeof(struct templelem));
          if (!template->next)  { log_msg("malloc() failed!"); exit(1); }
          template = template->next;
        } else {
          TEMPLATE = (struct templelem *) malloc(sizeof(struct templelem));
          if (!TEMPLATE)  { log_msg("malloc() failed!"); exit(1); }
          template = TEMPLATE;
        }
        if (optarg[i] != BACKREFCHAR) {
          start = i;
          while (optarg[i] && optarg[i] != BACKREFCHAR)  { ++i; }
          len = i - start;
          template->str = (char *) malloc(len + 1);
          if (!template->str)  { log_msg("malloc() failed!"); exit(1); }
          strncpy(template->str, optarg + start, len);
          template->str[len] = 0;
          template->data = len;
        } else {
          template->str = 0;
          template->data = (int) strtol(optarg + i + 1, &addr, 10);
          i = addr - optarg;
        }
        template->next = 0;
      }
      break;
    case 'v':
      VECTORSIZE = atoi(optarg);
      break;
    case 'w':
      WORDTABLESIZE = atoi(optarg);
      break;
    case 'z':
      CLUSTERVECTORSIZE = atoi(optarg);
      break;
    case '?':
      return 0;
    }
    
  }
  
  if (optind < argc) {
    INPUTFILES = (struct inputfile *) malloc(sizeof(struct inputfile));
    if (!INPUTFILES)  { log_msg("malloc() failed!"); exit(1); }
    ptr = INPUTFILES;
    
    while (optind < argc) {
      ptr->name = (char *) malloc(strlen(argv[optind]) + 1);
      if (!ptr->name)  { log_msg("malloc() failed!"); exit(1); }
      strcpy(ptr->name, argv[optind]);
      if (++optind == argc)  { break; }
      ptr->next = (struct inputfile *) malloc(sizeof(struct inputfile));
      if (!ptr->next)  { log_msg("malloc() failed!"); exit(1); }
      ptr = ptr->next;
    }
    
    ptr->next = 0;

  }
  optind=0;
  return 1;
}


void print_usage(char *progname) {
  fprintf(stderr, "\n");
  fprintf(stderr, "SLCT version 0.05, Copyright (C) 2003-2007 Risto Vaarandi\n");
  fprintf(stderr, "Usage: %s [-b <byte offset>] [-c <clustertable size>]\n", 
                  progname);
  fprintf(stderr, "[-d <regexp>] [-f <regexp>] [-g <slice size>] [-i <seed>] [-j]\n");
  fprintf(stderr, "[-o <outliers file>] [-r] [-t <template>] [-v <wordvector size>]\n");
  fprintf(stderr, "[-w <wordtable size>] [-z <clustervector size>] -s <support>\n"); 
  fprintf(stderr, "<input files>\n");
}

int main(int argc, char **argv)
{
  char logstr[MAXLOGMSGLEN];
  tableindex_t effect; 
  wordnumber_t number;
  struct templelem *ptr;
  struct word_freq_stat infrequent_words;

  /* Default values for commandline options */

  BYTEOFFSET = 0;
  CLUSTERTABLESIZE = 0;
  DELIM = 0;
  FILTER = 0;
  INITSEED = 1;
  JOIN = 0;
  OUTLIERFILE = 0;
  PCTSUPPORT = 0;
  REFINE = 0;
  SLICESIZE = 0;
  SUPPORT = 0;
  TEMPLATE = 0;
  VECTORSIZE = 0;
  WORDTABLESIZE = 100000;
  
  INPUTFILES = 0;

  /* Parse commandline options */
  if (!parse_options(argc, argv)) {
    print_usage(argv[0]);
    exit(1);
  }

  if (!INPUTFILES) {
    fprintf(stderr, "No input files specified\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (BYTEOFFSET < 0) {
    fprintf(stderr, 
      "'-b' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (CLUSTERTABLESIZE < 0) {
    fprintf(stderr, 
      "'-c' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (DELIM) {  
    if (regcomp(&DELIM_REGEX, DELIM, REG_EXTENDED)) {
      fprintf(stderr, 
        "Bad regular expression given with '-d' option\n", DELIM);
      print_usage(argv[0]);
      exit(1);
    }
  } else { 
    regcomp(&DELIM_REGEX, "[ \t]+", REG_EXTENDED);
  }
    
  if (FILTER  &&  regcomp(&FILTER_REGEX, FILTER, REG_EXTENDED)) {
    fprintf(stderr, 
      "Bad regular expression given with '-f' option\n", FILTER);
    print_usage(argv[0]);
    exit(1);
  }
  
  if (INITSEED < 0) {
    fprintf(stderr,
      "'-i' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (SLICESIZE < 0) {
    fprintf(stderr, 
      "'-g' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (SUPPORT <= 0  &&  PCTSUPPORT <=0) {  
  printf("%d is SUPPORT %d is PCTSUPPORT\n", SUPPORT,PCTSUPPORT);
    fprintf(stderr,"'-s' option requires a positive number as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  for (ptr = TEMPLATE; ptr; ptr = ptr->next) {
    if (!ptr->str  &&  (ptr->data < 0 || ptr->data > MAXPARANEXPR - 1)) {
      fprintf(stderr, 
        "'-t' option requires backreference variables to be in range $0..$%d\n",
        MAXPARANEXPR - 1);
      print_usage(argv[0]);
      exit(1);
    }
  }

  if (VECTORSIZE < 0) {
    fprintf(stderr, 
      "'-v' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (WORDTABLESIZE <= 0) {
    fprintf(stderr, 
      "'-w' option requires a positive number as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (CLUSTERVECTORSIZE < 0) {
    fprintf(stderr, 
      "'-z' option requires a positive number or zero as parameter\n");
    print_usage(argv[0]);
    exit(1);
  }

  if (JOIN && CLUSTERVECTORSIZE) {
    fprintf(stderr, 
      "'-j' and '-z' options can't be used together\n");
    print_usage(argv[0]);
    exit(1);
  }
  
  /* Do the work */

  log_msg("Starting...");

  srand(INITSEED);
  VECTORSEED = rand();
  CLUSTERVECTORSEED = rand();
  WORDTABLESEED = rand();
  CLUSTERTABLESEED = rand();
  
  if (VECTORSIZE) {
    log_msg("Creating the word summary vector...");
    VECTOR = (unsigned long *) malloc(sizeof(unsigned long) * VECTORSIZE);
    if (!VECTOR)  { log_msg("malloc() failed!"); exit(1); }
    effect = create_word_vector();
    sprintf(logstr, "%llu slots in the word summary vector >= support threshold", 
                    (unsigned long long) effect);
    log_msg(logstr);
  }

  log_msg("Creating vocabulary...");
  WORDTABLE = (struct elem **) malloc(sizeof(struct elem *) * WORDTABLESIZE);
  if (!WORDTABLE)  { log_msg("malloc() failed!"); exit(1); }
  number = create_vocabulary();
  sprintf(logstr, "%llu words inserted into the vocabulary", 
                  (unsigned long long) number);
  log_msg(logstr);
  
  if (VECTORSIZE)  { free((void *) VECTOR); }
  
  log_msg("Finding frequent words from the vocabulary...");
  WORDNUM = find_frequent_words(&infrequent_words);
  sprintf(logstr, "%llu frequent words found", (unsigned long long) WORDNUM);
  log_msg(logstr);  

  sprintf(logstr, "%llu words in vocabulary occurring 1 time", 
		  (unsigned long long) infrequent_words.ones);
  log_msg(logstr);  
  sprintf(logstr, "%llu words in vocabulary occurring 2 times or less", 
		  (unsigned long long) infrequent_words.twos);
  log_msg(logstr);  
  sprintf(logstr, "%llu words in vocabulary occurring 5 times or less", 
		  (unsigned long long) infrequent_words.fives);
  log_msg(logstr);  
  sprintf(logstr, "%llu words in vocabulary occurring 10 times or less", 
		  (unsigned long long) infrequent_words.tens);
  log_msg(logstr);  
  sprintf(logstr, "%llu words in vocabulary occurring 20 times or less", 
		  (unsigned long long) infrequent_words.twenties);
  log_msg(logstr);  

  if (WORDNUM) {

    if (CLUSTERVECTORSIZE) {
      log_msg("Creating the cluster summary vector...");
      CLUSTERVECTOR = 
      (unsigned long *) malloc(sizeof(unsigned long) * CLUSTERVECTORSIZE);
      if (!CLUSTERVECTOR)  { log_msg("malloc() failed!"); exit(1); }
      effect = create_cluster_vector();
      sprintf(logstr, "%llu slots in the cluster summary vector >= support threshold", 
                      (unsigned long long) effect);
      log_msg(logstr);
    }

    log_msg("Finding cluster candidates...");
    if (!CLUSTERTABLESIZE)  { CLUSTERTABLESIZE = 100 * WORDNUM; }
    CLUSTERTABLE = 
    (struct elem **) malloc(sizeof(struct elem *) * CLUSTERTABLESIZE);
    if (!CLUSTERTABLE)  { log_msg("malloc() failed!"); exit(1); }
    number = create_cluster_candidates();
    sprintf(logstr, "%llu cluster candidates found", 
                    (unsigned long long) number);
    log_msg(logstr);  

    if (CLUSTERVECTORSIZE)  { free((void *) CLUSTERVECTOR); }
    
    log_msg("Finding clusters from the set of candidates...");
    number = find_clusters();
    sprintf(logstr, "%llu clusters found", (unsigned long long) number);
    log_msg(logstr);  

    if (number) {
      if (REFINE) {
        log_msg("Refining cluster descriptions and finding outliers...");
        refine_clusters();
      }
      print_clusters();
    }
  
  }
  
  log_msg("Analysis complete.");

  free_table(WORDTABLE, WORDTABLESIZE);
  free_table(CLUSTERTABLE, CLUSTERTABLESIZE);
  
  free_inputfiles();
  free_template();
  free_slices();
  free_clusters();
  
  regfree(&DELIM_REGEX);
  if (FILTER)  { regfree(&FILTER_REGEX); }

  if (DELIM)  { free((void *) DELIM); }
  if (FILTER)  { free((void *) FILTER); }
  if (OUTLIERFILE)  { free((void *) OUTLIERFILE); }

  exit(0);
}

