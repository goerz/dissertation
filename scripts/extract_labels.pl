#!/usr/bin/env perl
use strict;
use warnings;

# Given a list of tex files as arguments, print all the labels defined in those
# files to STDOUT (one label per line).
#
# Check that no label is defined twice, abort otherwise

my %labels = ();
my $location;
my $label;
my $line_nr;

foreach my $file (@ARGV){
    open(INFILE, $file) or die("Can't open $file\n");
    $line_nr = 0;
    while (<INFILE>){
        $line_nr += 1;
        while (/\\label\{([\w.:\+-]+?)\}/g){
            $location = "$file:$line_nr";
            if (defined($labels{$1})){
                die("Label $1 in $location was already defined in $labels{$1}\n");
            } else {
                $labels{$1} = $location
            }
            print $1, "\n";
        }
    }
    close INFILE;
}
