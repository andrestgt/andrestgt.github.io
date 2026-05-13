#!/usr/bin/env bash
set -euo pipefail

perl <<'PERL'
use strict;
use warnings;
use utf8;
use Encode qw(decode);

sub norm {
    my ($s) = @_;
    $s =~ s/Ä/Ae/g;
    $s =~ s/Ö/Oe/g;
    $s =~ s/Ü/Ue/g;
    $s =~ s/ä/ae/g;
    $s =~ s/ö/oe/g;
    $s =~ s/ü/ue/g;
    $s =~ s/ß/ss/g;
    $s = lc($s);
    $s =~ s/[^a-z0-9]+//g;
    return $s;
}

my $xml = `unzip -p Reviews-master.docx word/document.xml`;
$xml = decode('UTF-8', $xml);

$xml =~ s/<w:p[^>]*>/\n/g;
$xml =~ s/<[^>]+>//g;
$xml =~ s/&amp;/&/g;
$xml =~ s/&lt;/</g;
$xml =~ s/&gt;/>/g;

my @lines = grep { length } map {
    s/\r//g;
    s/^\s+//;
    s/\s+$//;
    $_;
} split /\n/, $xml;

my %reviews;
my $germany_seen = 0;
my $started = 0;

for (my $i=0; $i<=$#lines; $i++) {
    my $line = $lines[$i];

    if ($line eq "Germany") {
        $germany_seen++;
        if ($germany_seen == 2) {
            $started = 1;
            next;
        }
    }

    next unless $started;
    last if $line eq "Austria";

    next if $line =~ /· \d+ review/ || $line =~ /· \d+ reviews/;

    next unless (
        $i + 2 <= $#lines &&
        $lines[$i+1] =~ /^[★☆]/ &&
        $lines[$i+2] =~ /Germany$/
    );

    my $title = $line;
    next if $title eq "Ottweiler (Saar)";

    my @body;
    for (my $j = $i + 3; $j <= $#lines; $j++) {
        my $t = $lines[$j];

        last if (
            $j + 2 <= $#lines &&
            $lines[$j+1] =~ /^[★☆]/ &&
            $lines[$j+2] =~ /Germany$/
        );

        last if $t eq "Austria";
last if $t =~ /· \d+ review/;
last if $t =~ /· \d+ reviews/;

        next if $t =~ /^Food:\s/;
        next if $t =~ /^Service:\s/;
        next if $t =~ /^Atmosphere:\s/;

        push @body, $t;
    }

    $reviews{ norm($title) } = join("\n\n", @body);
}

my @files = `find food/germany -name index.md`;
chomp @files;
my $updated = 0;

for my $file (@files) {
    open my $fh, "<:utf8", $file or next;
    local $/;
    my $txt = <$fh>;
    close $fh;

    next unless $txt =~ /review:\s*true/;
    next if $txt =~ /title:\s*Caf[ée] Moulu/m;

    my ($title) = $txt =~ /^title:\s*(.+)$/m;
    next unless $title;

    my $body = $reviews{ norm($title) };
    next unless $body;

    next unless $txt =~ /^(---.*?---\s*)(.*?)(### Practical.*)$/s;

    my $new = $1 . "\n" . $body . "\n\n" . $3;

    open my $out, ">:utf8", $file or next;
    print $out $new;
    close $out;

    print "Updated: $title\n";
    $updated++;
}

print "\nTotal updated: $updated\n";
PERL
