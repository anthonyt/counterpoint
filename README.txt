INTRODUCTION
------------
Repository for Anthony Theocharis' as-yet-unnamed CSC479 project.

This system aims to provide a simple mechanism for the input and evaluation of
music according to theoretical rules.

Music can be read from the dictionary defined in tracks.py, or from a MIDI file.

Errors will be printed to the console.

This iteration of the program supports first and second species, using
2, 3, or 4 voices, with the following caveats:

	Inner voices are not treated specially.
	While the rule for inner voices are usually more lax than for outer voices,
	the addition of those exceptions is deferred to the next iteration.

	Minor keys are not supported.
	This program relies heavily on the mingus music theory framework, which has
	basically no support for minor keys. This will require a large refactoring
	of the mingus framework, and is deferred to the next iteration.

	Particularly dense midi files (eg. a minute of 16th notes at 100bpm) will
	not parse correctly. This is probably not a problem for the vast majority
	of counterpoint exercises.
	I've already rewritten most of mingus' midi-to-python library once, but I
	think accumulated rounding error is muddling the timing of notes after
	a long enough duration.


   USAGE
------------

Usage: counterpoint.py [options]

Options:
  -h, --help            show this help message and exit

  -t                    Read tracks from tracks.py. If encountered, will
                        ignore instructions to read from MIDI file.

  -r MIDI_FILE
  --read-midi=MIDI_FILE
                        Read tracks from midi provided MIDI_FILE. If
                        encountered, will ignore instructions to write to MIDI
                        file.

  -s SPECIES
  --species=SPECIES
                        One of 1, 2, or 4. Only applies to MIDI files.

  -w OUTPUT_FILE
  --write-midi=OUTPUT_FILE
                        Write midi file OUTPUT_FILE

  -p PNG_FILE
  --write-png=PNG_FILE
                        Write printed music to PNG_FILE

  -z MIDI_FILE          Testing option. Read in a midi file, but do not test
                        it for errors. Can be used with -w, -p and -l

  -l LY_FILE            Testing option. Write lilypond string to LY_FILE.


Example 1:
	./counterpoint.py -t

	This will read the note and track data from a 'melodies' dict in tracks.py
	tracks.py contains example data for first and second species counterpoint.
	Uncomment the block at the bottom of tracks.py for an example of second
	species parsing.

Example 2:
	./counterpoint.py -t -w harmonization.mid

	This will read the data from tracks.py, the same as above, but the
	-w flag tells the program to write out a MIDI file of the current score
	named 'harmonization.mid' in the current directory.

Example 3:
	./counterpoint.py -t -p harmonization.png

	This will read the data from tracks.py, the same as above, but the
	-w flag tells the program to write out a PNG image of the generated score
	named 'harmonization.png' in the current directory.

Example 4:
	./counterpoint.py -r harmony.mid -s 2

	This will read note and track data from a midi file named 'harmony.mid'
	The tracks in this midi file must be named Soprano, Alto, Tenor, or Bass.
	There must be no more than one of each track name, and there must be
	between 2 and 4 tracks total.

	The -s flag tells the program to evaluate the music as second species.
	The default (if the -s flag is omitted) is first species.
	

Example 5:
	./counterpoint.py -r harmony.mid -p harmonization.png

	This will read from a midi file, like in Example 4.
	The music will be evaluated as first species, because the -s flag is missing.
	Typeset music will then be written to 'harmonization.png' as in Example 3.

