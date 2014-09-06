#!/usr/bin/env perl
use strict;
use warnings;

# Given a list of bib files as arguments, print all the bib keys
# files to STDOUT (one key per line).
#
# Check that no key is defined twice, abort otherwise

my %keys = ();
my $location;
my $label;
my $line_nr;

foreach my $file (@ARGV){
    open(INFILE, $file) or die("Can't open $file\n");
    $line_nr = 0;
    while (<INFILE>){
        $line_nr += 1;
        if (/^\s*@(article|book|booklet|conference|inbook|incollection|inproceedings|manual|mastersthesis|misc|phdthesis|proceedings|techreport|unpublished)\{\s*(.*),/i){
            $location = "$file:$line_nr";
            if (defined($keys{$2})){
                die("Key $2 in $location was already defined in $keys{$2}\n");
            } else {
                $keys{$2} = $location
            }
            print $2, "\n";
        }
    }
    close INFILE;
}

