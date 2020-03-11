#!/usr/bin/env python3
import re
import sys
import os
import glob2
import argparse
import subprocess


def get_para():
    desc = """
    To extract the reST content from *.wdl files into *.rst files.
    The directory tree will be preserved in the output directory.
    """

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-a', dest='source_dir', metavar='<directory>',
        default='.',
        help='the directory which *.wdl files located. [%(default)s]')

    parser.add_argument('-o', dest='out_dir', metavar='<directory>',
        default='./rst_for_wdl',
        help='the output directory for the *.rst files. [%(default)s]')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def search_wdl_files(wdir='.'):
    wdir = os.path.abspath(wdir)
    return glob2.glob(wdir+'/**/*.wdl')


def extract_comment_from_wdl_file(wdl_file=None, result_dir='.'):
    comments = []
    with open(wdl_file, 'r') as fh:
        comment = ''
        previous_is_wdl = False
        for i in fh:
            i = i.lstrip()
            if i.startswith('#*'):
                i = re.sub(r'^#\*[ ]?', '', i)
                comment += i
                previous_is_wdl = True
            else:
                if previous_is_wdl:
                    comments.append(comment)
                    comments.append('\n')
                    comment = ''
                    previous_is_wdl = False
        # the last comment
        if comment:
            comments.append(comment)
            comments.append('\n')
            comment = ''
            previous_is_wdl = False

    if len(comments) > 0:
        out_rst_file = re.sub(r'.wdl$', r'.rst', os.path.basename(wdl_file))
        out_rst_file = os.path.join(result_dir, out_rst_file)
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        with open(out_rst_file, 'w') as fhout:
            for comment in comments:
                print(comment, file=fhout)


def main():
    args = get_para()

    args.source_dir = os.path.abspath(args.source_dir)
    args.out_dir = os.path.abspath(args.out_dir)

    all_wdl_files = search_wdl_files(wdir=args.source_dir)

    for wdl_file in all_wdl_files:
        out_path = re.sub(args.source_dir, '', wdl_file)
        out_path = re.sub(r'^/', '', out_path) # remove the leading '/'
        out_path_dirname = os.path.dirname(out_path)
        out_path_dirname2 = os.path.join(args.out_dir, out_path_dirname)

        cmd = 'mkdir -p {}'.format(out_path_dirname2)
        subprocess.check_output(cmd, shell=True)
        extract_comment_from_wdl_file(
            wdl_file=wdl_file,
            result_dir=out_path_dirname2)



if __name__ == '__main__':
    main()