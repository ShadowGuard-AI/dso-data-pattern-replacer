#!/usr/bin/env python3

import argparse
import re
import logging
import os
import sys
import chardet
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Finds and replaces data matching a regular expression pattern with a specified replacement string.")

    parser.add_argument("input_file", help="The input file to process.")
    parser.add_argument("pattern", help="The regular expression pattern to search for.")
    parser.add_argument("replacement", help="The replacement string. Use 'faker.name', 'faker.email', etc. for dynamic faker values.")
    parser.add_argument("-o", "--output_file", help="The output file to write to. If not specified, overwrites the input file.", default=None)
    parser.add_argument("-e", "--encoding", help="The encoding of the input file. If not specified, attempts to detect it.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-n", "--dry_run", action="store_true", help="Perform a dry run without writing changes.")


    return parser

def detect_encoding(file_path):
    """
    Detects the encoding of a file.
    """
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        logging.error(f"Error detecting encoding: {e}")
        return None

def process_file(input_file, pattern, replacement, output_file=None, encoding=None, dry_run=False):
    """
    Processes the input file, replaces data matching the pattern, and writes the output.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if encoding is None:
            encoding = detect_encoding(input_file)
            if encoding is None:
                encoding = 'utf-8' # Default to utf-8 if detection fails
                logging.warning("Could not detect encoding, defaulting to utf-8.")

        try:
            with open(input_file, 'r', encoding=encoding) as f:
                data = f.read()
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding file with encoding {encoding}: {e}")

        # Build the function re.sub calls for each match. The old code ran
        # eval on the faker expression once, without calling it, so the
        # replacement text was the string form of a bound method object and
        # every match got that same useless string. Resolving the attribute
        # by name and calling it per match gives each match its own value,
        # and returning the literal through a callable keeps backslashes in
        # it from being read as regex template escapes.
        fake = Faker()
        if replacement.startswith("faker."):
            attr_name = replacement[len("faker."):]
            provider = getattr(fake, attr_name, None) if attr_name.isidentifier() else None
            if callable(provider):
                def replacement_fn(match):
                    return str(provider())
            else:
                # An invalid faker attribute fails the run here, before
                # any write. The old code logged the error and stamped
                # the literal attribute text over every match instead.
                raise ValueError(f"Invalid faker attribute: {attr_name}")
        else:
            def replacement_fn(match):
                return replacement

        # Validate pattern
        try:
            re.compile(pattern)  # Attempt to compile the regex
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {e}")

        # Count replacements on every run, as dry run already did. A
        # run that replaces nothing has not done the work it reports,
        # so it fails here, before any write, in every mode.
        num_replacements = len(re.findall(pattern, data))
        if num_replacements == 0:
            logging.error("No replacements made: the pattern matched nothing in the input.")
            raise ValueError("No replacements made: the pattern matched nothing in the input.")

        new_data = re.sub(pattern, replacement_fn, data)

        if dry_run:
            logging.info("Dry run: No changes will be written.")
            logging.info(f"Dry run complete.  Would have made {num_replacements} replacements.")
            return

        if output_file is None:
            output_file = input_file

        try:
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(new_data)
            logging.info(f"Made {num_replacements} replacements.")
            logging.info(f"Successfully processed file: {input_file}. Output written to: {output_file}")

        except Exception as e:
            raise IOError(f"Error writing to output file: {e}")

    except FileNotFoundError as e:
        logging.error(e)
        raise
    except ValueError as e:
        logging.error(e)
        raise
    except IOError as e:
        logging.error(e)
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        raise


def main():
    """
    Main function to execute the data pattern replacer.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)  # Set logging level to DEBUG

    logging.debug(f"Input file: {args.input_file}")
    logging.debug(f"Pattern: {args.pattern}")
    logging.debug(f"Replacement: {args.replacement}")
    logging.debug(f"Output file: {args.output_file}")
    logging.debug(f"Encoding: {args.encoding}")
    logging.debug(f"Dry run: {args.dry_run}")


    try:
        process_file(args.input_file, args.pattern, args.replacement, args.output_file, args.encoding, args.dry_run)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    main()