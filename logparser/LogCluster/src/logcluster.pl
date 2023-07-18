#!/usr/bin/perl -w
#
# LogCluster 0.09 - logcluster.pl
# Copyright (C) 2015-2017 Risto Vaarandi
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

package main::LogCluster;

sub compile_func {

  my($code) = $_[0];
  my($ret, $error);

  $ret = eval $code;

  if ($@) {
    $error = $@;
    chomp $error;
    return (0, $error);
  } elsif (ref($ret) ne "CODE") {
    return (0, "eval did not return a code reference");
  } else {
    return (1, $ret);
  }
}


package main;

use strict;

no warnings 'recursion';

use vars qw(
  $USAGE
  $aggrsup
  $ansicoloravail
  %candidates
  %clusters
  $color
  $color1
  $color2
  $csize
  @csketch
  $debug
  $facility
  $fpat
  %fword_deps
  %fwords
  %gwords
  $help
  $ifile
  %ifiles
  @inputfilepat
  @inputfiles
  $lcfunc
  $lcfuncptr
  $lfilter
  $lineregexp
  $outlierfile
  %outlierpat
  $progname
  $ptree
  $ptreesize
  $readdump
  $readwords
  $rsupport
  $searchregexp
  $separator
  $sepregexp
  $support
  $syslogavail
  $syslogopen
  $template
  $totalinputlines
  $version
  $wcfunc
  $wcfuncptr
  @weightfunction
  $weightf
  $wfileint
  $wfilter
  $wfreq
  $wildcard
  $wordregexp
  $wordsonly
  $wreplace
  $writedump
  $writewords
  $wsearch
  $wsize
  @wsketch
  $wweight
);

use Getopt::Long;
use Digest::MD5 qw(md5);
use Storable;

$ansicoloravail = eval { require Term::ANSIColor };
$syslogavail = eval { require Sys::Syslog };


######################### Functions #########################

# This function logs the message given with parameter2,..,parameterN to
# syslog, using the level parameter1. The message is also written to stderr.

sub log_msg {

  my($level) = shift(@_);
  my($msg) = join(" ", @_);

  print STDERR scalar(localtime()), ": $msg\n";
  if ($syslogopen) { Sys::Syslog::syslog($level, $msg); }
}

# This function compiles the function given with parameter1, returning
# a function pointer if the compilation is successful, and undef otherwise

sub compile_func_wrapper {

  my($code) = $_[0];
  my($ok, $value);

  ($ok, $value) = main::LogCluster::compile_func($code);
  if ($ok) { return $value; }
  log_msg("err", "Failed to compile the code '$code':", $value);
  return undef;
}

# This function hashes the string given with parameter1 to an integer
# in the range (0...$wsize-1) and returns the integer. The $wsize integer
# can be set with the --wsize command line option.

sub hash_string {
  return unpack('L', md5($_[0])) % $wsize;
}

# This function hashes the candidate ID given with parameter1 to an integer
# in the range (0...$csize-1) and returns the integer. The $csize integer
# can be set with the --csize command line option.

sub hash_candidate {
  return unpack('L', md5($_[0])) % $csize;
}

# This function matches the line given with parameter1 with a regular
# expression $lineregexp (the expression can be set with the --lfilter
# command line option). If the $template string is defined (can be set
# with the --template command line option), the line is converted
# according to $template (match variables in $template are substituted
# with values from regular expression match, and the resulting string
# replaces the line). If the regular expression $lineregexp does not match
# the line, 0 is returned, otherwise the line (or converted line, if
# --template option has been given) is returned.
# If the --lfilter option has not been given but --lcfunc option is
# present, the Perl function given with --lcfunc is used for matching
# and converting the line. If the function returns 'undef', line is
# regarded non-matching, otherwise the value returned by the function
# replaces the original line.
# If neither --lfilter nor --lcfunc option has been given, the line
# is returned without a trailing newline.

sub process_line {

  my($line) = $_[0];
  my(%matches, @matches, $match, $i);

  chomp($line);

  if (defined($lfilter)) {

    if (!defined($template)) {
      if ($line =~ /$lineregexp/) { return $line; } else { return undef; }
    }

    if (@matches = ($line =~ /$lineregexp/)) {
      %matches = %+;
      $matches{"0"} = $line;
      $i = 1;
      foreach $match (@matches) { $matches{$i++} = $match; }
      $line = $template;
      $line =~ s/\$(?:\$|(\d+)|\{(\d+)\}|\+\{(\w+)\})/
               !defined($+)?'$':(defined($matches{$+})?$matches{$+}:'')/egx;
      return $line;
    }

    return undef;

  } elsif (defined($lcfunc)) {

    $line = eval { $lcfuncptr->($line) };
    return $line;

  } else {
    return $line;
  }
}

# This function opens input file and returns a file handle for opened
# file; if the open fails, the function will call exit(1)

sub open_input_file {

  my($file) = $_[0];
  my($handle);

  if ($file eq "-") {
    if (!open($handle, "<&STDIN")) {
      log_msg("err", "Can't dup standard input: $!");
      exit(1);
    }
  } elsif (!open($handle, $file)) {
    log_msg("err", "Can't open input file $file: $!");
    exit(1);
  }

  return $handle;
}

# This function makes a pass over the data set and builds the sketch
# @wsketch which is used for finding frequent words. The sketch contains
# $wsize counters ($wsize can be set with --wsize command line option).

sub build_word_sketch {

  my($index, $ifile, $line, $word, $word2, $i, $fh);
  my(@words, @words2, %words);

  for ($index = 0; $index < $wsize; ++$index) { $wsketch[$index] = 0; }

  $i = 0;

  foreach $ifile (@inputfiles) {

    $fh = open_input_file($ifile);

    while (<$fh>) {
      $line = process_line($_);
      if (!defined($line)) { next; }
      ++$i;
      @words = split(/$sepregexp/, $line);
      %words = map { $_ => 1 } @words;
      @words = keys %words;
      foreach $word (@words) {
        $index = hash_string($word);
        ++$wsketch[$index];
        if (defined($wfilter) && $word =~ /$wordregexp/) {
          $word =~ s/$searchregexp/$wreplace/g;
          $index = hash_string($word);
          ++$wsketch[$index];
        } elsif (defined($wcfunc)) {
          @words2 = eval { $wcfuncptr->($word) };
          foreach $word2 (@words2) {
            if (!defined($word2)) { next; }
            $index = hash_string($word2);
            ++$wsketch[$index];
          }
        }
      }
    }

    close($fh);
  }

  if (!defined($support)) {
    $support = int($rsupport * $i / 100);
    log_msg("info", "Total $i lines read from input sources, using absolute support $support (relative support $rsupport percent)");
  }

  $i = 0;
  for ($index = 0; $index < $wsize; ++$index) {
    if ($wsketch[$index] >= $support) { ++$i; }
  }

  log_msg("info", "Word sketch successfully built, $i buckets >= $support");
}

# This function makes a pass over the data set, finds frequent words and
# stores them to %fwords hash table. The function returns the total number
# of lines in input file(s).

sub find_frequent_words {

  my($ifile, $line, $word, $word2, $index, $i, $fh);
  my(@words, @words2, %words);

  $i = 0;

  foreach $ifile (@inputfiles) {

    $fh = open_input_file($ifile);

    while (<$fh>) {
      $line = process_line($_);
      if (!defined($line)) { next; }
      ++$i;
      @words = split(/$sepregexp/, $line);
      %words = map { $_ => 1 } @words;
      @words = keys %words;
      if (defined($wsize)) {
        foreach $word (@words) {
          $index = hash_string($word);
          if ($wsketch[$index] >= $support) { ++$fwords{$word}; }
          if (defined($wfilter) && $word =~ /$wordregexp/) {
            $word =~ s/$searchregexp/$wreplace/g;
            $index = hash_string($word);
            if ($wsketch[$index] >= $support) { ++$fwords{$word}; }
          } elsif (defined($wcfunc)) {
            @words2 = eval { $wcfuncptr->($word) };
            foreach $word2 (@words2) {
              if (!defined($word2)) { next; }
              $index = hash_string($word2);
              if ($wsketch[$index] >= $support) { ++$fwords{$word2}; }
            }
          }
        }
      } else {
        foreach $word (@words) {
          ++$fwords{$word};
          if (defined($wfilter) && $word =~ /$wordregexp/) {
            $word =~ s/$searchregexp/$wreplace/g;
            ++$fwords{$word};
          } elsif (defined($wcfunc)) {
            @words2 = eval { $wcfuncptr->($word) };
            foreach $word2 (@words2) {
              if (!defined($word2)) { next; }
              ++$fwords{$word2};
            }
          }
        }
      }
    }

    close($fh);
  }

  if (!defined($support)) {
    $support = int($rsupport * $i / 100);
    log_msg("info", "Total $i lines read from input sources, using absolute support $support (relative support $rsupport percent)");
  }

  foreach $word (keys %fwords) {
    if ($fwords{$word} < $support) { delete $fwords{$word}; }
  }

  if ($debug) {
    foreach $word (sort { $fwords{$b} <=> $fwords{$a} } keys %fwords) {
      log_msg("debug", "Frequent word: $word -- occurs in",
                       $fwords{$word}, "lines");
    }
  }

  log_msg("info", "Total number of frequent words:", scalar(keys %fwords));

  return $i;
}

# This function reads frequent words from a text file without making a pass
# over the data set, and stores them to %fwords hash table.

sub read_frequent_words {

  my($ref);

  if (defined($wfileint)) {

    $ref = retrieve($readwords);
    %fwords = %{$ref->{"FrequentWords"}};

  } else {

    if (!open(WORDFILE, $readwords)) {
      log_msg("err", "Can't open word file $readwords: $!");
      exit(1);
    }

    while (<WORDFILE>) {
      chomp;
      $fwords{$_} = 1;
    }

    close(WORDFILE);
  }

  log_msg("info", "Total number of frequent words:", scalar(keys %fwords),
                  "(read from $readwords)");
}

# This function writes frequent words (%fwords hash table) and their
# relative supports into a file.

sub write_frequent_words {

  my($lines) = $_[0];
  my(%rsupports, $word);

  if (defined($wfileint)) {

    if ($lines) {
      foreach $word (keys %fwords) {
        $rsupports{$word} = $fwords{$word} / $lines;
      }
    }

    store({ "FrequentWords" => \%fwords,
            "RelativeSupports" => \%rsupports }, $writewords);

  } else {

    if (!open(WORDFILE, ">$writewords")) {
      log_msg("err", "Can't open word file $writewords: $!");
      exit(1);
    }

    foreach $word (keys %fwords) { print WORDFILE "$word\n"; }

    close(WORDFILE);
  }

  log_msg("info", scalar(keys %fwords),
                  "frequent words written to $writewords");
}

# This function makes a pass over the data set and builds the sketch
# @csketch which is used for finding frequent candidates. The sketch contains
# $csize counters ($csize can be set with --csize command line option).

sub build_candidate_sketch {

  my($ifile, $line, $word, $word2, $candidate, $index, $i, $fh);
  my(@words, @words2, @candidate);

  for ($index = 0; $index < $csize; ++$index) { $csketch[$index] = 0; }

  $i = 0;

  foreach $ifile (@inputfiles) {

    $fh = open_input_file($ifile);

    while (<$fh>) {

      $line = process_line($_);
      if (!defined($line)) { next; }

      ++$i;

      @words = split(/$sepregexp/, $line);
      @candidate = ();

      foreach $word (@words) {
        if (exists($fwords{$word})) {
          push @candidate, $word;
        } elsif (defined($wfilter) && $word =~ /$wordregexp/) {
          $word =~ s/$searchregexp/$wreplace/g;
          if (exists($fwords{$word})) {
            push @candidate, $word;
          }
        } elsif (defined($wcfunc)) {
          @words2 = eval { $wcfuncptr->($word) };
          foreach $word2 (@words2) {
            if (!defined($word2)) { next; }
            if (exists($fwords{$word2})) {
              push @candidate, $word2;
              last;
            }
          }
        }
      }

      if (scalar(@candidate)) {
        $candidate = join("\n", @candidate);
        $index = hash_candidate($candidate);
        ++$csketch[$index];
      }
    }

    close($fh);
  }

  # if support has not been identified yet (e.g., frequent words were loaded
  # from file), calculate the support

  if (!defined($support)) {
    $support = int($rsupport * $i / 100);
    log_msg("info", "Total $i lines read from input sources, using absolute support $support (relative support $rsupport percent)");
  }

  $i = 0;
  for ($index = 0; $index < $csize; ++$index) {
    if ($csketch[$index] >= $support) { ++$i; }
  }

  log_msg("info", "Candidate sketch successfully built, $i buckets >= $support");
}

# This function logs the description for candidate parameter1.

sub print_candidate {

  my($candidate) = $_[0];
  my($i, $msg);

  $msg = "Cluster candidate with support " .
         $candidates{$candidate}->{"Count"} . ": ";

  for ($i = 0; $i < $candidates{$candidate}->{"WordCount"}; ++$i) {
    if ($candidates{$candidate}->{"Vars"}->[$i]->[1] > 0) {
      $msg .= "*{" . $candidates{$candidate}->{"Vars"}->[$i]->[0] . "," .
                     $candidates{$candidate}->{"Vars"}->[$i]->[1] . "} ";
    }
    $msg .= $candidates{$candidate}->{"Words"}->[$i] . " ";
  }

  if ($candidates{$candidate}->{"Vars"}->[$i]->[1] > 0) {
      $msg .= "*{" . $candidates{$candidate}->{"Vars"}->[$i]->[0] . "," .
              $candidates{$candidate}->{"Vars"}->[$i]->[1] . "}";
  }

  log_msg("debug", $msg);
}

# This function makes a pass over the data set, identifies cluster candidates
# and stores them to %candidates hash table. If the --wweight command line
# option has been provided, dependencies between frequent words are also
# identified during the data pass and stored to %fword_deps hash table.

sub find_candidates {

  my($ifile, $line, $word, $word2, $varnum, $candidate, $index, $total, $i);
  my(@words, @words2, %words, @candidate, @vars, $linecount, $fh, $n);

  $linecount = 0;

  foreach $ifile (@inputfiles) {

    $fh = open_input_file($ifile);

    while (<$fh>) {

      $line = process_line($_);
      if (!defined($line)) { next; }

      ++$linecount;

      @words = split(/$sepregexp/, $line);
      @candidate = ();
      @vars = ();
      $varnum = 0;

      foreach $word (@words) {
        if (exists($fwords{$word})) {
          push @candidate, $word;
          push @vars, $varnum;
          $varnum = 0;
        } elsif (defined($wfilter) && $word =~ /$wordregexp/) {
          $word =~ s/$searchregexp/$wreplace/g;
          if (exists($fwords{$word})) {
            push @candidate, $word;
            push @vars, $varnum;
            $varnum = 0;
          } else {
            ++$varnum;
          }
        } elsif (defined($wcfunc)) {
          @words2 = eval { $wcfuncptr->($word) };
          $i = 0;
          foreach $word2 (@words2) {
            if (!defined($word2)) { next; }
            if (exists($fwords{$word2})) {
              push @candidate, $word2;
              push @vars, $varnum;
              $varnum = 0;
              $i = 1;
              last;
            }
          }
          if (!$i) { ++$varnum; }
        } else {
          ++$varnum;
        }
      }
      push @vars, $varnum;

      if (scalar(@candidate)) {

        $candidate = join("\n", @candidate);

        # if the candidate sketch has been created previously, check the
        # sketch bucket that corresponds to the candidate, and if it is
        # smaller than support threshold, don't consider the candidate

        if (defined($csize)) {
          $index = hash_candidate($candidate);
          if ($csketch[$index] < $support) { next; }
        }

        # if --wweight option was given, store word dependency information
        # (word co-occurrence counts) to %fword_deps

        if (defined($wweight)) {
          %words = map { $_ => 1 } @candidate;
          @words = keys %words;
          foreach $word (@words) {
            foreach $word2 (@words) { ++$fword_deps{$word}->{$word2}; }
          }
        }

        # if the given candidate already exists, increase its support and
        # adjust its wildcard information, otherwise create a new candidate

        if (!exists($candidates{$candidate})) {
          $candidates{$candidate} = {};
          $candidates{$candidate}->{"Words"} = [ @candidate ];
          $candidates{$candidate}->{"WordCount"} = scalar(@candidate);
          $candidates{$candidate}->{"Vars"} = [];
          $candidates{$candidate}->{"Lines"} = [];
          push @{$candidates{$candidate}->{Lines}}, $linecount;
          for $varnum (@vars) {
            push @{$candidates{$candidate}->{"Vars"}}, [ $varnum, $varnum];
          }
          $candidates{$candidate}->{"Count"} = 1;
        } else {
          $total = scalar(@vars);
          for ($index = 0; $index < $total; ++$index) {
            if ($candidates{$candidate}->{"Vars"}->[$index]->[0]
                > $vars[$index]) {
              $candidates{$candidate}->{"Vars"}->[$index]->[0] = $vars[$index];
            }
            elsif ($candidates{$candidate}->{"Vars"}->[$index]->[1]
                   < $vars[$index]) {
              $candidates{$candidate}->{"Vars"}->[$index]->[1] = $vars[$index];
            }
          }
          push @{$candidates{$candidate}->{Lines}}, $linecount;
          ++$candidates{$candidate}->{"Count"};
        }
      }
    }

    close($fh);
  }

  # if support has not been identified yet (e.g., frequent words were loaded
  # from file), calculate the support

  if (!defined($support)) {
    $support = int($rsupport * $linecount / 100);
    log_msg("info", "Total $linecount lines read from input sources, using absolute support $support (relative support $rsupport percent)");
  }

  # If --wweight option was given, convert word dependency information
  # (word co-occurrence counts) into range 0..1.

  if (defined($wweight)) {

    $i = 0;

    foreach $word (keys %fwords) {

      # since %fwords hash can be initialized with frequent words loaded
      # from file, %fword_deps might not contain information for a frequent
      # word if it has not been observed in input file

      if (!exists($fword_deps{$word})) { next; }

      # Note that $fword_deps{$word}->{$word} equals to the occurrence count
      # of $word. Since %fwords hash can be initialized with frequent words
      # loaded from file, $fword_deps{$word}->{$word} is used in calculations
      # instead of $fwords{$word}.

      $n = $fword_deps{$word}->{$word};

      # convert word dependency information into range 0..1

      foreach $word2 (keys %{$fword_deps{$word}}) {
        $fword_deps{$word}->{$word2} /= $n;
        ++$i;
        if ($debug) {
          log_msg("debug", "Dependency $word -> $word2:",
                           $fword_deps{$word}->{$word2});
        }
      }
    }
    log_msg("info", "Total number of frequent word dependencies:", $i);
  }

  if ($debug) {
    foreach $candidate (sort { $candidates{$b}->{"Count"} <=>
                               $candidates{$a}->{"Count"} } keys %candidates) {
      print_candidate($candidate);
    }
  }

  log_msg("info", "Total number of candidates:", scalar(keys %candidates));
}

# This function finds frequent candidates by removing candidates with
# insufficient support from the %candidates hash table.

sub find_frequent_candidates {

  my($candidate);

  foreach $candidate (keys %candidates) {
    if ($candidates{$candidate}->{"Count"} < $support) {
      delete $candidates{$candidate};
    }
  }

  log_msg("info", "Total number of frequent candidates:",
                   scalar(keys %candidates));
}

# This function inserts a candidate into the prefix tree

sub insert_into_prefix_tree {

  my($node, $cand, $i) = @_;
  my($label);

  if ($i == $candidates{$cand}->{"WordCount"}) {
    $label = $candidates{$cand}->{"Vars"}->[$i]->[0] . "\n" .
             $candidates{$cand}->{"Vars"}->[$i]->[1];
  } else {
    $label = $candidates{$cand}->{"Vars"}->[$i]->[0] . "\n" .
             $candidates{$cand}->{"Vars"}->[$i]->[1] . "\n" .
             $candidates{$cand}->{"Words"}->[$i];
  }

  if (!exists($node->{"Children"}->{$label})) {
    $node->{"Children"}->{$label} = {};
    $node = $node->{"Children"}->{$label};
    $node->{"Min"} = $candidates{$cand}->{"Vars"}->[$i]->[0];
    $node->{"Max"} = $candidates{$cand}->{"Vars"}->[$i]->[1];

    if ($i < $candidates{$cand}->{"WordCount"}) {
      $node->{"Children"} = {};
      $node->{"Word"} = $candidates{$cand}->{"Words"}->[$i];
    } else {
      $node->{"Candidate"} = $cand;
    }
    ++$ptreesize;

  } else {
    $node = $node->{"Children"}->{$label};
  }

  if ($i < $candidates{$cand}->{"WordCount"}) {
    insert_into_prefix_tree($node, $cand, $i + 1);
  }
}

# This function arranges all candidates into the prefix tree data structure,
# in order to facilitate fast matching between candidates

sub build_prefix_tree {

  my($cand);

  $ptree = { Children => {} };
  $ptreesize = 0;

  foreach $cand (keys %candidates) {
    insert_into_prefix_tree($ptree, $cand, 0);
  }

  log_msg("info", "Total number of nodes in prefix tree:", $ptreesize);
}

# This function finds more specific candidates for the given candidate with
# the help of the prefix tree, and records more specific candidates into
# the SubClusters hash table of the given candidate

sub find_more_specific {

  my($node, $cand, $i, $min, $max) = @_;
  my($candidate, $children, $child, $cand2);
  my($candmin, $candmax);

  $candidate = $candidates{$cand};
  $candmin = $candidate->{"Vars"}->[$i]->[0];
  $candmax = $candidate->{"Vars"}->[$i]->[1];
  $children = $node->{"Children"};

  foreach $child (keys %{$children}) {

    $node = $children->{$child};

    if ($i == $candidate->{"WordCount"}) {
      if (exists($node->{"Candidate"})) {
        if ($candmin > $node->{"Min"} + $min ||
            $candmax < $node->{"Max"} + $max) { next; }
        $cand2 = $node->{"Candidate"};
        if ($cand ne $cand2) {
          $candidate->{"SubClusters"}->{$cand2} = 1;
        }
      } else {
        find_more_specific($node, $cand, $i, $min + $node->{"Min"} + 1,
                                             $max + $node->{"Max"} + 1);
      }
      next;
    }

    if (exists($node->{"Candidate"})) { next; }
    if ($candmax < $node->{"Max"} + $max) { next; }

    if ($candmin > $node->{"Min"} + $min ||
        $candidate->{"Words"}->[$i] ne $node->{"Word"}) {
      find_more_specific($node, $cand, $i, $min + $node->{"Min"} + 1,
                                           $max + $node->{"Max"} + 1);
      next;
    }

    find_more_specific($node, $cand, $i + 1, 0, 0);

    find_more_specific($node, $cand, $i, $min + $node->{"Min"} + 1,
                                         $max + $node->{"Max"} + 1);
  }
}

# This function scans all cluster candidates (stored in %candidates hash
# table), and for each candidate X it finds all candidates Y1,..,Yk which
# represent more specific line patterns. After finding such clusters Yi
# for each X, the supports of Yi are added to the support of each X.
# For speeding up the process, previously created prefix tree is used.
# In order to facilitate the detection of outliers, for each X with sufficient
# support the clusters Yi are stored to %outlierpat hash table (this allows
# for fast detection of non-outliers which match X).

sub aggregate_supports {

  my(@keys, @keys2, $cand, $cand2);

  @keys = keys %candidates;

  foreach $cand (@keys) {

    $candidates{$cand}->{"OldCount"} = $candidates{$cand}->{"Count"};
    $candidates{$cand}->{"Count2"} = $candidates{$cand}->{"Count"};
    $candidates{$cand}->{"SubClusters"} = {};

    find_more_specific($ptree, $cand, 0, 0, 0);
    @keys2 = keys %{$candidates{$cand}->{"SubClusters"}};

    foreach $cand2 (@keys2) {
      $candidates{$cand}->{"Count2"} += $candidates{$cand2}->{"Count"};
      push @{$candidates{$cand}->{Lines}}, @{$candidates{$cand2}->{Lines}};
    }
  }

  foreach $cand (@keys) {

    $candidates{$cand}->{"Count"} = $candidates{$cand}->{"Count2"};
    @keys2 = keys %{$candidates{$cand}->{"SubClusters"}};

    if (scalar(@keys2)) {

      if (defined($outlierfile) && $candidates{$cand}->{"Count"} >= $support) {
        foreach $cand2 (@keys2) { $outlierpat{$cand2} = 1; }
      }

      if ($debug) {
        log_msg("debug",
                "The support of the following candidate was increased from",
                $candidates{$cand}->{"OldCount"}, "to",
                $candidates{$cand}->{"Count"});
        print_candidate($cand);
        log_msg("debug", "with the following candidates being more specific:");
        foreach $cand2 (@keys2) {
          print_candidate($cand2);
          log_msg("debug", "(original support:",
                           $candidates{$cand2}->{"OldCount"}, ")");
        }
        log_msg("debug", "----------------------------------------");
      }
    }

  }
}

# This function makes a pass over the data set, find outliers and stores them
# to file $outlierfile (can be set with the --outliers command line option).

sub find_outliers {

  my($ifile, $line, $word, $word2, $candidate, $i, $fh);
  my(@words, @words2, @candidate);

  if (!open(OUTLIERFILE, ">$outlierfile")) {
    log_msg("err", "Can't open outlier file $outlierfile: $!");
    exit(1);
  }

  $i = 0;

  foreach $ifile (@inputfiles) {

    $fh = open_input_file($ifile);

    while (<$fh>) {

      $line = process_line($_);
      if (!defined($line)) { next; }

      @words = split(/$sepregexp/, $line);
      @candidate = ();

      foreach $word (@words) {
        if (exists($fwords{$word})) {
          push @candidate, $word;
        } elsif (defined($wfilter) && $word =~ /$wordregexp/) {
          $word =~ s/$searchregexp/$wreplace/g;
          if (exists($fwords{$word})) {
            push @candidate, $word;
          }
        } elsif (defined($wcfunc)) {
          @words2 = eval { $wcfuncptr->($word) };
          foreach $word2 (@words2) {
            if (!defined($word2)) { next; }
            if (exists($fwords{$word2})) {
              push @candidate, $word2;
              last;
            }
          }
        }
      }

      if (scalar(@candidate)) {
        $candidate = join("\n", @candidate);
        if (exists($candidates{$candidate})) { next; }
        if (defined($aggrsup) && exists($outlierpat{$candidate})) { next; }
      }

      print OUTLIERFILE $_;
      ++$i;
    }

    close($fh);
  }

  close(OUTLIERFILE);

  log_msg("info", "Total number of outliers:", $i);
}

# This function inspects the cluster candidate parameter1 and finds the weight
# of each word in the candidate description. The weights are calculated from
# word dependency information according to --weightf=1.

sub find_weights {

  my($candidate) = $_[0];
  my($ref, $total, $word, $word2, $weight);

  $ref = $candidates{$candidate}->{"Words"};
  $total = $candidates{$candidate}->{"WordCount"};
  $candidates{$candidate}->{"Weights"} = [];

  foreach $word (@{$ref}) {
    $weight = 0;
    foreach $word2 (@{$ref}) { $weight += $fword_deps{$word2}->{$word}; }
    push @{$candidates{$candidate}->{"Weights"}}, $weight / $total;
  }
}

# This function inspects the cluster candidate parameter1 and finds the weight
# of each word in the candidate description. The weights are calculated from
# word dependency information according to --weightf=2.

sub find_weights2 {

  my($candidate) = $_[0];
  my($ref, $total, $word, $word2);
  my(%weights, @words);

  $ref = $candidates{$candidate}->{"Words"};
  $candidates{$candidate}->{"Weights"} = [];

  %weights = map { $_ => 0 } @{$ref};
  @words = keys %weights;
  $total = scalar(@words) - 1;

  foreach $word (@words) {
    if (!$total) {
      $weights{$word} = 1;
      last;
    }
    foreach $word2 (@words) {
      if ($word eq $word2) { next; }
      $weights{$word} += $fword_deps{$word2}->{$word};
    }
    $weights{$word} /= $total;
  }

  foreach $word (@{$ref}) {
    push @{$candidates{$candidate}->{"Weights"}}, $weights{$word};
  }
}

# This function inspects the cluster candidate parameter1 and finds the weight
# of each word in the candidate description. The weights are calculated from
# word dependency information according to --weightf=3.

sub find_weights3 {

  my($candidate) = $_[0];
  my($ref, $total, $word, $word2, $weight);

  $ref = $candidates{$candidate}->{"Words"};
  $total = $candidates{$candidate}->{"WordCount"};
  $candidates{$candidate}->{"Weights"} = [];

  foreach $word (@{$ref}) {
    $weight = 0;
    foreach $word2 (@{$ref}) {
      $weight += ($fword_deps{$word2}->{$word} + $fword_deps{$word}->{$word2});
    }
    push @{$candidates{$candidate}->{"Weights"}}, $weight / (2 * $total);
  }
}

# This function inspects the cluster candidate parameter1 and finds the weight
# of each word in the candidate description. The weights are calculated from
# word dependency information according to --weightf=4.

sub find_weights4 {

  my($candidate) = $_[0];
  my($ref, $total, $word, $word2);
  my(%weights, @words);

  $ref = $candidates{$candidate}->{"Words"};
  $candidates{$candidate}->{"Weights"} = [];

  %weights = map { $_ => 0 } @{$ref};
  @words = keys %weights;
  $total = scalar(@words) - 1;

  foreach $word (@words) {
    if (!$total) {
      $weights{$word} = 1;
      last;
    }
    foreach $word2 (@words) {
      if ($word eq $word2) { next; }
      $weights{$word} +=
          ($fword_deps{$word2}->{$word} + $fword_deps{$word}->{$word2});
    }
    $weights{$word} /= (2 * $total);
  }

  foreach $word (@{$ref}) {
    push @{$candidates{$candidate}->{"Weights"}}, $weights{$word};
  }
}

# This function prints word weights for cluster candidate parameter1.

sub print_weights {

  my($candidate) = $_[0];
  my($i, $msg);

  $msg = "Cluster candidate with support " .
         $candidates{$candidate}->{"Count"} . ": ";

  for ($i = 0; $i < $candidates{$candidate}->{"WordCount"}; ++$i) {
    if ($candidates{$candidate}->{"Vars"}->[$i]->[1] > 0) {
      $msg .= "*{" . $candidates{$candidate}->{"Vars"}->[$i]->[0] . "," .
                     $candidates{$candidate}->{"Vars"}->[$i]->[1] . "} ";
    }
    $msg .= $candidates{$candidate}->{"Words"}->[$i] .
            " (weight: " . $candidates{$candidate}->{"Weights"}->[$i] . ") ";
  }

  if ($candidates{$candidate}->{"Vars"}->[$i]->[1] > 0) {
      $msg .= "*{" . $candidates{$candidate}->{"Vars"}->[$i]->[0] . "," .
              $candidates{$candidate}->{"Vars"}->[$i]->[1] . "}";
  }

  log_msg("debug", $msg);
}

# This function joins the cluster candidate parameter1 to a suitable cluster
# by words with insufficient weights. If there is no suitable cluster,
# a new cluster is created from the candidate.

sub join_candidate {

  my($candidate) = $_[0];
  my($i, $n, $cluster, @words);

  $n = $candidates{$candidate}->{"WordCount"};

  for ($i = 0; $i < $n; ++$i) {
    if ($candidates{$candidate}->{"Weights"}->[$i] >= $wweight) {
      push @words, $candidates{$candidate}->{"Words"}->[$i];
    } else {
      push @words, "";
    }
  }

  $cluster = join("\n", @words);

  if (!exists($clusters{$cluster})) {
    $clusters{$cluster} = {};
    $clusters{$cluster}->{"Words"} =
                               [ map { length($_)?$_:{} } @words ];
    $clusters{$cluster}->{"Vars"} =
                               [ @{$candidates{$candidate}->{"Vars"}} ];
    $clusters{$cluster}->{"WordCount"} =
                               $candidates{$candidate}->{"WordCount"};
    $clusters{$cluster}->{"Count"} = 0;
    $clusters{$cluster}->{"Lines"} = [];
  }

  for ($i = 0; $i < $n; ++$i) {
    if (ref($clusters{$cluster}->{"Words"}->[$i]) eq "HASH") {
      $clusters{$cluster}->{"Words"}->[$i]->{$candidates{$candidate}->{"Words"}->[$i]} = 1;
    }
  }

  ++$n;

  for ($i = 0; $i < $n; ++$i) {
    if ($clusters{$cluster}->{"Vars"}->[$i]->[0] >
        $candidates{$candidate}->{"Vars"}->[$i]->[0]) {
      $clusters{$cluster}->{"Vars"}->[$i]->[0] =
      $candidates{$candidate}->{"Vars"}->[$i]->[0];
    }
    if ($clusters{$cluster}->{"Vars"}->[$i]->[1] <
        $candidates{$candidate}->{"Vars"}->[$i]->[1]) {
      $clusters{$cluster}->{"Vars"}->[$i]->[1] =
      $candidates{$candidate}->{"Vars"}->[$i]->[1];
    }
  }

  $clusters{$cluster}->{"Count"} += $candidates{$candidate}->{"Count"};
  push @{$clusters{$cluster}->{"Lines"}}, @{$candidates{$candidate}->{"Lines"}}
}

# This function joins the cluster candidate parameter1 to a suitable cluster
# by words with insufficient weights. If there is no suitable cluster,
# a new cluster is created from the candidate.

sub join_candidate2 {

  my($candidate) = $_[0];
  my($i, $n, $cluster, @words);
  my($min, $max, @vars);

  $n = $candidates{$candidate}->{"WordCount"};
  $min = 0;
  $max = 0;

  for ($i = 0; $i < $n; ++$i) {
    if ($candidates{$candidate}->{"Weights"}->[$i] >= $wweight) {
      push @words, $candidates{$candidate}->{"Words"}->[$i];
      push @vars, [ $candidates{$candidate}->{"Vars"}->[$i]->[0] + $min,
                    $candidates{$candidate}->{"Vars"}->[$i]->[1] + $max ];
      $min = 0;
      $max = 0;
    } else {
      $min += ($candidates{$candidate}->{"Vars"}->[$i]->[0] + 1);
      $max += ($candidates{$candidate}->{"Vars"}->[$i]->[1] + 1);
    }
  }
  push @vars, [ $candidates{$candidate}->{"Vars"}->[$i]->[0] + $min,
                $candidates{$candidate}->{"Vars"}->[$i]->[1] + $max ];

  $cluster = join("\n", @words);

  if (!exists($clusters{$cluster})) {

    $clusters{$cluster} = {};
    $clusters{$cluster}->{"Words"} = [ @words ];
    $clusters{$cluster}->{"Vars"} = [ @vars ];
    $clusters{$cluster}->{"WordCount"} = scalar(@words);
    $clusters{$cluster}->{"Count"} = $candidates{$candidate}->{"Count"};
    $clusters{$cluster}->{"Lines"} = [];
  } else {

    $n = $clusters{$cluster}->{"WordCount"} + 1;

    for ($i = 0; $i < $n; ++$i) {
      if ($clusters{$cluster}->{"Vars"}->[$i]->[0] > $vars[$i]->[0]) {
        $clusters{$cluster}->{"Vars"}->[$i]->[0] = $vars[$i]->[0];
      }
      if ($clusters{$cluster}->{"Vars"}->[$i]->[1] < $vars[$i]->[1]) {
        $clusters{$cluster}->{"Vars"}->[$i]->[1] = $vars[$i]->[1];
      }
    }
	push @{$clusters{$cluster}->{"Lines"}}, @{$candidates{$candidate}->{"Lines"}};
    $clusters{$cluster}->{"Count"} += $candidates{$candidate}->{"Count"};
  }
}

# This function joins frequent cluster candidates into final clusters
# by words with insufficient weights. For each candidate, word weights
# are first calculated and the candidate is then compared to already
# existing clusters, in order to find a suitable cluster for joining.
# If no such cluster exists, a new cluster is created from the candidate.

sub join_candidates {

  my($candidate);

  foreach $candidate (sort { $candidates{$b}->{"Count"} <=>
                             $candidates{$a}->{"Count"} } keys %candidates) {
    $weightfunction[$weightf]->($candidate);
    if ($debug) { print_weights($candidate); }
    if (defined($wildcard)) {
      join_candidate2($candidate);
    } else {
      join_candidate($candidate);
    }
  }
}

# This function finds frequent words in detected clusters

sub cluster_freq_words {

  my($cluster, $i, $word, %words);
  my($threshold, $total, @keys);

  @keys = keys %clusters;
  $total = scalar(@keys);

  if ($total == 0) { return; }

  foreach $cluster (@keys) {
    %words = ();
    for ($i = 0; $i < $clusters{$cluster}->{"WordCount"}; ++$i) {
      if (ref($clusters{$cluster}->{"Words"}->[$i]) eq "HASH") { next; }
      $words{$clusters{$cluster}->{"Words"}->[$i]} = 1;
    }
    foreach $word (keys %words) { ++$gwords{$word}; }
  }

  $threshold = $total * $wfreq;

  foreach $word (keys %gwords) {
    if ($gwords{$word} < $threshold) { delete $gwords{$word}; }
  }
}

# This function prints the cluster parameter1 to standard output.

sub print_cluster {

  my($cluster) = $_[0];
  my($i, $word, @wordlist);

  if ($wfreq) { cluster_freq_words(); }

  for ($i = 0; $i < $clusters{$cluster}->{"WordCount"}; ++$i) {
    if ($clusters{$cluster}->{"Vars"}->[$i]->[1] > 0) {
      print "*{" . $clusters{$cluster}->{"Vars"}->[$i]->[0] . "," .
                   $clusters{$cluster}->{"Vars"}->[$i]->[1] . "}";
      print " ";
    }
    if (ref($clusters{$cluster}->{"Words"}->[$i]) eq "HASH") {
      @wordlist = keys %{$clusters{$cluster}->{"Words"}->[$i]};
      if (scalar(@wordlist) > 1) {
        $word = "(" . join("|", @wordlist) . ")";
        if (defined($color1)) {
          print Term::ANSIColor::color($color1);
          print $word, " ";
          print Term::ANSIColor::color("reset");
        } else {
          print $word, " ";
        }
      } else {
        $word = $wordlist[0];
        if (defined($color1)) {
          print Term::ANSIColor::color($color1);
          print $word, " ";
          print Term::ANSIColor::color("reset");
        } elsif (defined($color2) && exists($gwords{$word})) {
          print Term::ANSIColor::color($color2);
          print $word, " ";
          print Term::ANSIColor::color("reset");
        } else {
          print $word, " ";
        }
      }
    } else {
      $word = $clusters{$cluster}->{"Words"}->[$i];
      if (defined($color2) && exists($gwords{$word})) {
        print Term::ANSIColor::color($color2);
        print $word, " ";
        print Term::ANSIColor::color("reset");
      } else {
        print $word, " ";
      }
    }
  }

  if ($clusters{$cluster}->{"Vars"}->[$i]->[1] > 0) {
      print "*{" . $clusters{$cluster}->{"Vars"}->[$i]->[0] . "," .
                   $clusters{$cluster}->{"Vars"}->[$i]->[1] . "}";
  }

  print "\t";
  print join(",", @{$clusters{$cluster}->{"Lines"}});
  print "\t", $clusters{$cluster}->{"Count"};
  print "\n";
}

# This function prints all clusters to standard output.

sub print_clusters {

  my($cluster);

  foreach $cluster (sort { $clusters{$b}->{"Count"} <=>
                           $clusters{$a}->{"Count"} } keys %clusters) {
    print_cluster($cluster);
  }

  log_msg("info", "Total number of clusters:", scalar(keys %clusters));
}

######################### Main program #########################

$weightfunction[1] = \&find_weights;
$weightfunction[2] = \&find_weights2;
$weightfunction[3] = \&find_weights3;
$weightfunction[4] = \&find_weights4;


$progname = (split(/\//, $0))[-1];

$USAGE = qq!Usage: $progname [options]
Options:
  --input=<file_pattern> ...
  --support=<support>
  --rsupport=<relative_support>
  --separator=<word_separator_regexp>
  --lfilter=<line_filter_regexp>
  --template=<line_conversion_template>
  --lcfunc=<perl_code>
  --syslog=<syslog_facility>
  --wsize=<word_sketch_size>
  --csize=<candidate_sketch_size>
  --wweight=<word_weight_threshold>
  --weightf=<word_weight_function>
  --wfreq=<word_frequency_threshold>
  --wfilter=<word_filter_regexp>
  --wsearch=<word_search_regexp>
  --wreplace=<word_replace_string>
  --wcfunc=<perl_code>
  --outliers=<outlier_file>
  --readdump=<dump_file>
  --writedump=<dump_file>
  --readwords=<word_file>
  --writewords=<word_file>
  --color[=<color>]
  --wildcard
  --wfileint
  --wordsonly
  --aggrsup
  --debug
  --help, -?
  --version


--input=<file_pattern>
Find clusters from files matching the <file_pattern>, where each cluster
corresponds to some line pattern, and print patterns to standard output.
For example, --input=/var/log/remote/*.log finds clusters from all files
with the .log extension in /var/log/remote.
This option can be specified multiple times.
Note that special file name - means finding line patterns from data from
standard input, and reporting detected line patterns when EOF is read from
standard input. However, processing data from standard input only makes
sense for clustering modes which involve single pass over input data.
For example, consider the following stream mining scenario:
$progname --input=- --support=100 --readwords=dictionary.txt

--support=<support>
Find clusters (line patterns) that match at least <support> lines in input
file(s). Each line pattern consists of word constants and variable parts,
where individual words occur at least <support> times in input files(s).
For example, --support=1000 finds clusters (line patterns) which consist
of words that occur at least in 1000 log file lines, with each cluster
matching at least 1000 log file lines.

--rsupport=<relative_support>
This option takes a real number from the range 0..100 for its value, and
sets relative support threshold in percentage of total number of input lines.
For example, if 20000 lines are read from input file(s), --rsupport=0.1 is
equivalent to --support=20.

--separator=<word_separator_regexp>
Regular expression which matches separating characters between words.
Default value for <word_separator_regexp> is \\s+ (i.e., regular expression
that matches one or more whitespace characters).

--lfilter=<line_filter_regexp>
When clustering log file lines from file(s) given with --input option(s),
process only lines which match the regular expression. For example,
--lfilter='sshd\\[\\d+\\]:' finds clusters for log file lines that
contain the string sshd[<pid>]: (i.e., sshd syslog messages).
This option can not be used with --lcfunc option.

--template=<line_conversion_template>
After the regular expression given with --lfilter option has matched a line,
convert the line by substituting match variables in <line_conversion_template>.
For example, if --lfilter='(sshd\\[\\d+\\]:.*)' option is given, only sshd
syslog messages are considered during clustering, e.g.:
Apr 15 12:00:00 myhost sshd[123]: this is a test
When the above line matches the regular expression (sshd\\[\\d+\\]:.*),
\$1 match variable is set to:
sshd[123]: this is a test
If --template='\$1' option is given, the original input line
Apr 15 12:00:00 myhost sshd[123]: this is a test
is converted to
sshd[123]: this is a test
(i.e., the timestamp and hostname of the sshd syslog message are ignored).
Please note that <line_conversion_template> supports not only numeric
match variables (such as \$2 or \${12}), but also named match variables with
\$+{name} syntax (such as \$+{ip} or \$+{hostname}).
This option can not be used without --lfilter option.

--lcfunc=<perl_code>
Similarly to --lfilter and --template options, this option is used for
filtering and converting log file lines. This option takes the definition
of an anonymous perl function for its value. The function receives the log
file line as its only input parameter, and the value returned by the function
replaces the original log file line. In order to indicate that the line
should not be processed, 'undef' must be returned from the function.
For example, with
--lcfunc='sub { if (\$_[0] =~ s/192\\.168\\.\\d{1,3}\\.\\d{1,3}/IP-address/g) { return \$_[0]; } return undef; }'
only lines that contain the string "192.168.<digits>.<digits>" are considered
during clustering, and all strings "192.168.<digits>.<digits>" are replaced
with the string "IP-address" in such lines. Longer filtering and conversion
functions can be defined in a separate perl module. For example, with
--lcfunc='require "/home/user/TestModule.pm"; sub { TestModule::myfilter(@_); }'
all function parameters are passed to the function myfilter() from TestModule,
and the return value from myfilter() is used during clustering.
This option can not be used with --lfilter option.

--syslog=<syslog_facility>
Log messages about the progress of clustering to syslog, using the given
facility. For example, --syslog=local2 logs to syslog with local2 facility.

--wsize=<word_sketch_size>
Instead of finding frequent words by keeping each word with an occurrence
counter in memory, use a sketch of <word_sketch_size> counters for filtering
out infrequent words from the word frequency estimation process. This
option requires an additional pass over input files, but can save large
amount of memory, since most words in log files are usually infrequent.
For example, --wsize=250000 uses a sketch of 250,000 counters for filtering.

--csize=<candidate_sketch_size>
Instead of finding clusters by keeping each cluster candidate with
an occurrence counter in memory, use a sketch of <candidate_sketch_size>
counters for filtering out cluster candidates which match less than <support>
lines in input file(s). This option requires an additional pass over input
files, but can save memory if many cluster candidates are generated.
For example, --csize=100000 uses a sketch of 100,000 counters for filtering.
This option can not be used with --aggrsup option.

--wweight=<word_weight_threshold>
This option enables word weight based heuristic for joining clusters.
The option takes a positive real number not greater than 1 for its value.
With this option, an additional pass over input files is made, in order
to find dependencies between frequent words.
For example, if 5% of log file lines that contain the word 'Interface'
also contain the word 'eth0', and 15% of the log file lines with the word
'unstable' also contain the word 'eth0', dependencies dep(Interface, eth0)
and dep(unstable, eth0) are memorized with values 0.05 and 0.15, respectively.
Also, dependency dep(eth0, eth0) is memorized with the value 1.0.
Dependency information is used for calculating the weight of words in line
patterns of all detected clusters. The function for calculating the weight
can be set with --weightf option.
For instance, if --weightf=1 and the line pattern of a cluster is
'Interface eth0 unstable', then given the example dependencies above,
the weight of the word 'eth0' is calculated in the following way:
(dep(Interface, eth0) + dep(eth0, eth0)
  + dep(unstable, eth0)) / number of words = (0.05 + 1.0 + 0.15) / 3 = 0.4
If the weights of 'Interface' and 'unstable' are 1, and the word weight
threshold is set to 0.5 with --wweight option, the weight of 'eth0'
remains below threshold. If another cluster is identified where all words
appear in the same order, and all words with sufficient weight are identical,
two clusters are joined. For example, if clusters 'Interface eth0 unstable'
and 'Interface eth1 unstable' are detected where the weights of 'Interface'
and 'unstable' are sufficient in both clusters, but the weights of 'eth0'
and 'eth1' are smaller than the word weight threshold, the clusters are
joined into a new cluster 'Interface (eth0|eth1) unstable'.
In order to quickly evaluate different word weight threshold values and
word weight functions on the same set of clusters, clusters and word
dependency information can be dumped into a file during the first run of
the algorithm, in order to reuse these data during subsequent runs
(see --readdump and --writedump options).

--weightf=<word_weight_function>
This option takes an integer for its value which denotes a word weight
function, with the default value being 1. The function is used for finding
weights of words in cluster line patterns if --wweight option has been given.
If W1,...,Wk are words of the cluster line pattern, value 1 denotes the
function that finds the weight of the word Wi in the following way:
(dep(W1, Wi) + ... + dep(Wk, Wi)) / k
Value 2 denotes the function that will first find unique words U1,...Up from
W1,...Wk (p <= k, and if Ui = Uj then i = j). The weight of the word Ui is
then calculated as follows:
if p>1 then (dep(U1, Ui) + ... + dep(Up, Ui) - dep(Ui, Ui)) / (p - 1)
if p=1 then 1
Value 3 denotes a modification of function 1 which calculates the weight
of the word Wi as follows:
((dep(W1, Wi) + dep(Wi, W1)) + ... + (dep(Wk, Wi) + dep(Wi, Wk))) / (2 * k)
Value 4 denotes a modification of function 2 which calculates the weight
of the word Ui as follows:
if p>1 then ((dep(U1, Ui) + dep(Ui, U1)) + ... + (dep(Up, Ui) + dep(Ui, Up)) - 2*dep(Ui, Ui)) / (2 * (p - 1))
if p=1 then 1

--wfreq=<word_frequency_threshold>
This option enables frequent word identification in detected line patterns.
The option takes a positive real number not greater than 1 for its value.
If the total number of line patterns which are reported to the user is N,
the word W is regarded frequent if it appears in K detected line patterns and
(K / N) >= <word_frequency_threshold>. Setting <word_frequency_threshold>
to a higher value allows for identifying words that are shared by many
detected line patterns (such as hostnames or specific parts of timestamps).
In order to highlight frequent words in line patterns, use --color option.

--wfilter=<word_filter_regexp>
--wsearch=<word_search_regexp>
--wreplace=<word_replace_string>
These options are used for generating additional words during the clustering
process, in order to detect frequent words that match the same template.
If the regular expression <word_filter_regexp> matches the word, all
substrings in the word that match the regular expression <word_search_regexp>
are replaced with the string <word_replace_string>. The result of search-
and-replace operation is treated like a regular word, and can be used as
a part of a cluster candidate. However, when both the original word and
the result of search-and-replace are frequent, original word is given
a preference during the clustering process.
For example, if the following options are provided
--wfilter='[.:]' --wsearch='[0-9]+' --wreplace=N
the words 10.1.1.1 and 10.1.1.2:80 are converted into N.N.N.N and N.N.N.N:N
Note that --wfilter option requires the presence of --wsearch and --wreplace,
while --wsearch and --wreplace are ignored without --wfilter.

--wcfunc=<perl_code>
Similarly to --wfilter, --wsearch and --wreplace options, this option is
used for generating additional words during the clustering process.
This option takes the definition of an anonymous perl function for its value.
The function receives the word as its only input parameter, and returns
a list of 0 or more words (all 'undef' values in the list are ignored).
During the clustering process, the original word is used if it is frequent,
otherwise the first frequent word from the list replaces the original word.
For example, with
--wcfunc='sub { if (\$_[0] =~ /^Chrome\\/(\\d+)/) { return ("Chrome/\$1", "Chrome"); } }'
the word list ("Chrome/49", "Chrome") is generated for the word
"Chrome/49.0.2623.87". If words "Chrome/49.0.2623.87" and "Chrome/49" are
infrequent but "Chrome" is frequent, the word "Chrome" replaces the word
"Chrome/49.0.2623.87" during the clustering process.
This option can not be used with --wfilter option.

--outliers=<outlier_file>
If this option is given, an additional pass over input files is made, in order
to find outliers. All outlier lines are written to the given file.

--readdump=<dump_file>
Read clusters and frequent word dependencies from a dump file <dump_file>
that has been previously created with the --writedump option. This option
is useful for quick evaluation of different word weight thresholds and word
weight functions (see --wweight and --weightf options), without the need of
repeating the entire clustering process during each evaluation.

--writedump=<dump_file>
Write clusters and frequent word dependencies to a dump file <dump_file>.
This file can be used during later runs of the algorithm, in order to quickly
evaluate different word weight thresholds and functions for joining clusters.

--readwords=<word_file>
Don't detect frequent words from file(s) given with --input option(s), but
read them in from a word file <word_file>. With --wfileint option, <word_file>
has to be in binary format previously produced with --writewords option,
otherwise it is assumed that <word_file> is a text file where each frequent
word is provided in a separate line.

--writewords=<word_file>
After frequent words have been detected, write them to <word_file>.
With --wfileint option, <word_file> will be in binary format, otherwise
a text format will be used where each word is provided in a separate line.

--color[=[<color1>]:[<color2>]]
If --wweight option has been used for enabling word weight based heuristic
for joining clusters, words with insufficient weight are highlighted in
detected line patterns with color <color1>. If --wfreq option has been used
for finding frequent words in line patterns, frequent words are highlighted
in detected line patterns with color <color2>. If --color option is used
without a value, it is equivalent to --color=green:red.

--wildcard
If --wweight option has been used for enabling word weight based heuristic
for joining clusters, words with insufficient weight in detected line patterns
are replaced with wildcards when patterns are reported to the user.

--wfileint
If --readwords or --writewords option has been used for reading or writing
the word file, it is assumed that the word file is in binary format.

--wordsonly
Terminate after frequent words have been detected. If --writewords option
is also provided, this option allows for identifying and storing frequent
words only, so that no extra time is spent for finding clusters.

--aggrsup
If this option is given, for each cluster candidate other candidates are
identified which represent more specific line patterns. After detecting such
candidates, their supports are added to the given candidate. For example,
if the given candidate is 'Interface * down' with the support 20, and
candidates 'Interface eth0 down' (support 10) and 'Interface eth1 down'
(support 5) are detected as more specific, the support of 'Interface * down'
will be set to 35 (20+10+5).
This option can not be used with --csize option.

--debug
Increase logging verbosity by generating debug output.

--help, -?
Print this help.

--version
Print the version information.

!;

# if no options are provided in command line, set the --help option
# (check is done before GetOptions() which removes elements from @ARGV)

if (!scalar(@ARGV)) { $help = 1; }

# process command line options

GetOptions( "input=s" => \@inputfilepat,
            "support=i" => \$support,
            "rsupport=f" => \$rsupport,
            "separator=s" => \$separator,
            "lfilter=s" => \$lfilter,
            "template=s" => \$template,
            "lcfunc=s" => \$lcfunc,
            "syslog=s" => \$facility,
            "wsize=i" => \$wsize,
            "csize=i" => \$csize,
            "wweight=f" => \$wweight,
            "weightf=i" => \$weightf,
            "wfreq=f" => \$wfreq,
            "wfilter=s" => \$wfilter,
            "wsearch=s" => \$wsearch,
            "wreplace=s" => \$wreplace,
            "wcfunc=s" => \$wcfunc,
            "outliers=s" => \$outlierfile,
            "readdump=s" => \$readdump,
            "writedump=s" => \$writedump,
            "readwords=s" => \$readwords,
            "writewords=s" => \$writewords,
            "color:s" => \$color,
            "aggrsup" => \$aggrsup,
            "wildcard" => \$wildcard,
            "wfileint" => \$wfileint,
            "wordsonly" => \$wordsonly,
            "debug" => \$debug,
            "help|?" => \$help,
            "version" => \$version );

# print the usage help if requested

if (defined($help)) {
  print $USAGE;
  exit(0);
}

# print the version number if requested

if (defined($version)) {
  print "LogCluster version 0.09, Copyright (C) 2015-2017 Risto Vaarandi\n";
  exit(0);
}

# open connection to syslog with a given facility

if (defined($facility)) {
  if ($syslogavail) {
    Sys::Syslog::openlog($progname, "pid", $facility);
    $syslogopen = 1;
  }
}

# exit if improper value is given for --wweight option

if (defined($wweight) && ($wweight <= 0 || $wweight > 1)) {
  log_msg("err", "Please specify a positive real number not greater than 1 with --wweight option");
  exit(1);
}

# if --wweight option is given but --weightf is not, set it to default

if (defined($wweight) && !defined($weightf)) {
  $weightf = 1;
}

# exit if improper value is given for --weightf option

if (defined($weightf) && !defined($weightfunction[$weightf])) {
  log_msg("err", "--weightf option does not support function $weightf");
  exit(1);
}

# exit if improper value is given for --wfreq option

if (defined($wfreq) && ($wfreq <= 0 || $wfreq > 1)) {
  log_msg("err", "Please specify a positive real number not greater than 1 with --wfreq option");
  exit(1);
}

# exit if --readdump and --writedump options are used simultaneously

if (defined($readdump) && defined($writedump)) {
  log_msg("err", "--readdump and --writedump options can't be used together");
  exit(1);
}

# exit if --color option is given but no Term::ANSIColor module is installed

if (defined($color) && !$ansicoloravail) {
  log_msg("err",
  "--color option requires Term::ANSIColor module which is not installed");
  exit(1);
}

# if --color option is given with a value, parse the value and set all
# colors to 'undef' which have not been provided in the value;
# if --color option is given without a value, assume "green:red"

if (defined($color)) {
  if (length($color)) {
    ($color1, $color2) = split(/:/, $color);
    if (!length($color1)) { $color1 = undef; }
    if (!length($color2)) { $color2 = undef; }
  } else {
    $color1 = "green";
    $color2 = "red";
  }
}

# if the --readdump option has been given, use the dump file for producing
# quick output without considering other command line options

if (defined($readdump)) {

  # read data from dump file into a buffer referenced by $ref

  my $ref = retrieve($readdump);

  # copy the data from buffer to %candidates and %fword_deps hash tables

  %candidates = %{$ref->{"Candidates"}};
  %fword_deps = %{$ref->{"FwordDeps"}};

  # since the data read from dump file has been copied to %candidates and
  # %fword_deps hash tables, free the memory that holds data from dump file

  $ref = undef;

  # if --wweight option has been given but no word dependency info
  # was found in dump file, exit with error

  if (defined($wweight) && scalar(keys %fword_deps) == 0) {
    log_msg("err", "No word dependency information was found in dump file",
            $readdump, "which is required by --wweight option");
    exit(1);
  }

  # if --wweight option has been given, find the word weights for each
  # candidate and join candidates

  if (defined($wweight)) {
    join_candidates();
  } else {
    %clusters = %candidates;
  }

  print_clusters();

  exit(0);
}

# check the support value

if (!defined($support) && !defined($rsupport)) {
  log_msg("err", "No support specified with --support or --rsupport option");
  exit(1);
}

if (defined($support) && defined($rsupport)) {
  log_msg("err", "--support and --rsupport options can't be used together");
  exit(1);
}

if (defined($support) && $support < 0) {
  log_msg("err", "Please specify non-negative integer with --support option");
  exit(1);
}

if (defined($rsupport) && ($rsupport < 0 || $rsupport > 100)) {
  log_msg("err",
  "Please specify real number from the range 0..100 with --rsupport option");
  exit(1);
}

# evaluate input file patterns given in command line,
# and create the list of input files

foreach $fpat (@inputfilepat) {
  foreach $ifile (glob($fpat)) { $ifiles{$ifile} = 1; }
}

@inputfiles = keys %ifiles;

if (!scalar(@inputfiles)) {
  log_msg("err", "No input file(s) specified with --input option(s)");
  exit(1);
}

# compile the regular expression that matches word separator characters,
# and exit if the expression is invalid

if (!defined($separator)) { $separator = '\s+'; }
$sepregexp = eval { qr/$separator/ };

if ($@) {
  log_msg("err",
    "Invalid regular expression $separator given with --separator option");
  exit(1);
}

# exit if --lfilter and --lcfunc options are used together

if (defined($lfilter) && defined($lcfunc)) {
  log_msg("err", "--lfilter and --lcfunc options can't be used together");
  exit(1);
}

# compile the line filtering regular expression,
# and exit if the expression is invalid

if (defined($lfilter)) {
  $lineregexp = eval { qr/$lfilter/ };
  if ($@) {
    log_msg("err",
      "Invalid regular expression $lfilter given with --lfilter option");
    exit(1);
  }
}

# compile the line filter function, and exit if the compilation fails

if (defined($lcfunc)) {
  $lcfuncptr = compile_func_wrapper($lcfunc);
  if (!defined($lcfuncptr)) {
    log_msg("err", "Invalid function supplied with --lcfunc option");
    exit(1);
  }
}

# exit if --wfilter and --wcfunc options are used together

if (defined($wfilter) && defined($wcfunc)) {
  log_msg("err", "--wfilter and --wcfunc options can't be used together");
  exit(1);
}

# compile the word filtering regular expression,
# and exit if the expression is invalid

if (defined($wfilter)) {
  $wordregexp = eval { qr/$wfilter/ };
  if ($@) {
    log_msg("err",
      "Invalid regular expression $wfilter given with --wfilter option");
    exit(1);
  }
  if (!defined($wsearch)) {
    log_msg("err", "--wfilter option requires --wsearch");
    exit(1);
  }
  $searchregexp = eval { qr/$wsearch/ };
  if ($@) {
    log_msg("err",
      "Invalid regular expression $wsearch given with --wsearch option");
    exit(1);
  }
  if (!defined($wreplace)) {
    log_msg("err", "--wfilter option requires --wreplace");
    exit(1);
  }
}

# compile the word class function, and exit if the compilation fails

if (defined($wcfunc)) {
  $wcfuncptr = compile_func_wrapper($wcfunc);
  if (!defined($wcfuncptr)) {
    log_msg("err", "Invalid function supplied with --wcfunc option");
    exit(1);
  }
}

# exit if improper value is given for --wsize option

if (defined($wsize) && $wsize < 1) {
  log_msg("err", "Please specify positive integer with --wsize option");
  exit(1);
}

# exit if --wsize and --readwords options are used together

if (defined($wsize) && defined($readwords)) {
  log_msg("err", "--wsize and --readwords options can't be used together");
  exit(1);
}

# exit if improper value is given for --csize option

if (defined($csize) && $csize < 1) {
  log_msg("err", "Please specify positive integer with --csize option");
  exit(1);
}

# exit if --csize and --aggrsup options are used together

if (defined($csize) && defined($aggrsup)) {
  log_msg("err", "--csize and --aggrsup options can't be used together");
  exit(1);
}

# exit if --readwords and --writewords options are used together

if (defined($readwords) && defined($writewords)) {
  log_msg("err", "--readwords and --writewords options can't be used together");
  exit(1);
}

##### start the clustering process #####

log_msg("info", "Starting the clustering process...");

# if the --wsize command line option has been given, make a pass over
# the data set and create the word sketch data structure @wsketch

if (defined($wsize)) { build_word_sketch(); }

# make a pass over the data set and find frequent words (words which appear
# in $support or more lines), and store them to %fwords hash table;
# if a file is provided with the --readwords option, %fwords hash table
# is initialized from the content of this file

if (!defined($readwords)) {

  $totalinputlines = find_frequent_words();

  # if a file is provided with the --writewords option, frequent words
  # (keys in the %fwords hash table) are written to this file

  if (defined($writewords)) { write_frequent_words($totalinputlines); }

} else {
  read_frequent_words();
}

# if the --wordsonly command line option has been given, terminate without
# detecting clusters

if (defined($wordsonly)) { exit(0); }

# if the --wsize command line option has been given, release the word sketch

if (defined($wsize)) { @wsketch = (); }

# if the --csize command line option has been given, make a pass over
# the data set and create the candidate sketch data structure @csketch

if (defined($csize)) { build_candidate_sketch(); }

# make a pass over the data set and find cluster candidates;
# if --wweight option has been given, dependencies between frequent
# words are also identified during the data pass

find_candidates();

# if the --csize command line option has been given, release the candidate sketch

if (defined($csize)) { @csketch = (); }

# if --aggrsup option has been given, find more specific clusters for each
# cluster, and add supports of more specific clusters to the generic cluster

if (defined($aggrsup)) {
  build_prefix_tree();
  aggregate_supports();
  $ptree = undef;
}

# find frequent candidates

find_frequent_candidates();

# store hash tables of candidates and frequent word dependencies to file

if (defined($writedump)) {
  store({ "Candidates" => \%candidates,
          "FwordDeps" => \%fword_deps }, $writedump);
}

# if --wweight option has been given, find the word weights for each
# candidate and join candidates

if (defined($wweight)) {
  join_candidates();
} else {
  %clusters = %candidates;
}

# report clusters

print_clusters();

# if --wweight option has been given, release word dependency hash table

if (defined($wweight)) { %fword_deps = (); }

# if --outliers option has been given, detect outliers

if (defined($outlierfile)) { find_outliers(); }

