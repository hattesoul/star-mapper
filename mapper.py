#!/usr/bin/python3
# temporary workaround to run with ipython
# sys.argv = ['']

# to do:
# * get script running (✅ 2020-10-20)
# * implement default output folder

# Parser for command-line options, arguments and sub-commands
import argparse

# check for boolean value
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

# check command-line arguments
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass
parser = argparse.ArgumentParser(
    description='Map FASTQ reads to genome data.\nE.g.:\n  mapper.py -s /path/to/STAR/binary -f "/path/to/fastq/files -g /path/to/genome/index -o /output/path -z True -t True -c True -r 8 -v True',
    formatter_class=Formatter)
parser.add_argument(
    '-s', '--STARPath',
    required=True,
    help='set path to STAR binary')
parser.add_argument(
    '-f', '--fastqPath',
    required=True,
    help='set path to FASTQ files')
parser.add_argument(
    '-g', '--genomePath',
    required=True,
    help='set path to the folder that contains the genome indices')
parser.add_argument(
    '-o', '--output',
    default='mappings',
    help='set output folder')
parser.add_argument(
    '-z', '--gzipped',
    type=str2bool,
    nargs='?',
    const=True,
    default=False,
    help='set True if FASTQ files are in .gz file format')
parser.add_argument(
    '-t', '--transcriptCoordinates',
    type=str2bool,
    nargs='?',
    const=True,
    default=True,
    help='set True to output transcript coordinates translated alignments')
parser.add_argument(
    '-c', '--geneCount',
    type=str2bool,
    nargs='?',
    const=True,
    default=True,
    help='set True for counting number of reads per gene')
parser.add_argument(
    '-r', '--threads',
    default=4,
    help='set number of CPU threads')
parser.add_argument(
    '-v', '--verbose',
    type=str2bool,
    nargs='?',
    const=True,
    default=False,
    help='more output while the script is running')
arguments=parser.parse_args()

print('Starting script:')

# import modules
if arguments.verbose:
    print('  importing modules…', end='')

# Object-oriented filesystem paths
import pathlib

# Regular expression operations
import re

# System-specific parameters and functions
import sys

# Subprocess management
import subprocess

if arguments.verbose:
    print(' done')

# initital settings
if arguments.verbose:
    print('  initializing settings…', end='')
counter = dict()
counter['all'] = 0
if arguments.gzipped:
    extension = 'gz'
else:
    extension = 'fastq'
files = dict()
if arguments.verbose:
    print(' done')

# get file list
if arguments.verbose:
    print('  getting file list:')
fileList = pathlib.Path(arguments.fastqPath).glob('**/*.' + extension)
for item in fileList:
    if item.is_file():
        counter['all'] += 1
        files[str(item)] = '"' + arguments.STARPath + '"' \
            ' --genomeDir "' + arguments.genomePath + '"' + \
            ' --readFilesIn "' + arguments.fastqPath + '/' + item.name + '"' + \
            ' --outFileNamePrefix "' + arguments.output + '/' + re.match('(.*)\.fastq.*', item.name).group(1) + '/"' \
            ' --runThreadN ' + str(arguments.threads)
        if arguments.gzipped:
            files[str(item)] += ' --readFilesCommand zcat'
        if arguments.transcriptCoordinates or arguments.geneCount:
            files[str(item)] += ' --quantMode'
            if arguments.transcriptCoordinates:
                files[str(item)] += ' TranscriptomeSAM'
            if arguments.geneCount:
                files[str(item)] += ' GeneCounts'

# exit if no files were found
if counter['all'] == 0:
    print('[WARNING] No files found in folder \'' + arguments.fastqPath + '\'')
    sys.exit('Exiting')
if arguments.verbose:
    print('    total files found in \'' + arguments.fastqPath + '\': ' + str(counter['all']))

for item in files:
    if arguments.verbose:
        print('  mapping ' + str(item) + ':')
    execute = subprocess.run(files[item], shell=True)
print('All done and exiting.\n')
