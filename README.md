![Banner](banner.png)

# dso-data-pattern-replacer
Finds and replaces data matching a regular expression pattern with a specified replacement string. - Focused on Tools for sanitizing and obfuscating sensitive data within text files and structured data formats

## Install
`git clone https://github.com/ShadowGuardAI/dso-data-pattern-replacer`

## Usage
`./dso-data-pattern-replacer [params]`

## Parameters
- `-h`: Show help message and exit
- `-o`: The output file to write to. If not specified, overwrites the input file.
- `-e`: The encoding of the input file. If not specified, attempts to detect it.
- `-v`: Enable verbose logging.
- `-n`: Perform a dry run without writing changes.

## Behavior notes
- Without `-o`, the tool overwrites the input file in place. That default stays: the input is read fully before anything is written.
- Every run counts its replacements and logs the count, as dry run mode already did. A run with zero replacements (the pattern matches nothing, or the input is empty) prints a plain "No replacements made" line and exits non-zero. In separate output mode it writes no output file on such a run; in place mode the input is left untouched.
- A replacement of the form `faker.<attribute>` must name a real faker attribute. An invalid attribute fails the run at exit 1 before any write, instead of stamping the literal attribute text over the matches.

## License
Copyright (c) ShadowGuardAI
