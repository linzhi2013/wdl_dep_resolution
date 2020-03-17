#!/usr/bin/env python3
import sys
import os
import re
import argparse
import shutil

def get_para(parser):

    parser.add_argument('-project_root', metavar='<directory>',
        default='./',
        help='the project_root directory [%(default)s]')

    parser.add_argument('-project_name', metavar='<file>', required=True, help="project name")

    return parser


def make_project_dirs(project_path=None):
    '''
    Creae basic project folders.
    '''

    # src/wdl
    src_wdl_dir = os.path.join(project_path, 'src', 'wdl')
    os.makedirs(src_wdl_dir)

    # src/deps
    src_deps_dir = os.path.join(project_path, 'src', 'deps')
    os.makedirs(src_deps_dir)

    # doc
    doc_dir = os.path.join(project_path, 'doc')
    os.makedirs(doc_dir)

    # doc/deps
    doc_deps_dir = os.path.join(project_path, 'doc', 'deps')
    os.makedirs(doc_deps_dir)

    # docker
    docker_dir = os.path.join(project_path, 'docker')
    os.makedirs(docker_dir)

    # docker/deps
    docker_deps_dir = os.path.join(project_path, 'docker', 'deps')
    os.makedirs(docker_deps_dir)

    # test
    test_dir = os.path.join(project_path, 'test')
    os.makedirs(test_dir)


def create_pkg_info(project_path=None):
    '''
    Create a pkg_info.txt file.
    '''
    project_name = os.path.basename(project_path)

    content = '''name: {project_name}
version: 1.0.0
deps:

# lines start with '#' will be omitted.
# the dependencies can be specified like:
# minimap, nextdenovo:>1.0, BWA: >0.1 <0.9
#
# DO NOT forget the semilicon (:) when version(s) requirments
# are specified!
#
# project name must match the following pattern:
# r'[a-z]+(\\_[a-z0-9]+)*$'
#
# package tarball filename pattern:
# r'[a-z]+(\\_[a-z0-9]+)*\\-\\d+(\\.\\d+)*\\.tar\\.gz$'

'''.format(project_name=project_name)

    pkg_info_file = os.path.join(project_path, 'pkg_info.txt')
    with open(pkg_info_file, 'w') as fh:
        print(content, file=fh)


def create_readme(project_path=None):
    '''
    Create a README.md file.
    '''

    project_name = os.path.basename(project_path)

    content = '''Wellcome to {project_name}!

Project structure:

{project_name}/README.md # This file itself.


{project_name}/src/wdl  # Where WDL files will be created by youself.
{project_name}/src/deps # Where WDL pipelines can be installed by the wdlpmt tool.


{project_name}/doc      # Where WDL documentations will be created by youself.
{project_name}/doc/deps # Where WDL documentations can be installed by the wdlpmt tool.


{project_name}/docker      # Where Docker image recipes will be created by youself.
{project_name}/docker/deps # Where Docker image recipes can be installed by the wdlpmt tool.


{project_name}/config      # Where WDL input.json files will be created by youself.
{project_name}/config/deps # Where WDL input.json files can be installed by the wdlpmt tool.


{project_name}/crommwell_configs # the example cromwell configure templates and shell scripts to run a WDL workflow


{project_name}/test    # Where WDL tests will be created by youself.

        '''.format(project_name=project_name)

    readme_file = os.path.join(project_path, 'README.md')
    with open(readme_file, 'w') as fh:
        print(content, file=fh)

    return readme_file


def copy_cromwell_configs(project_path='./'):
    source_crommwell_configs_dir = os.path.join(os.path.dirname(__file__), 'crommwell_configs')

    dest_crommwell_configs_dir = os.path.join(project_path, 'crommwell_configs')

    if os.path.exists(source_crommwell_configs_dir):
        shutil.copytree(source_crommwell_configs_dir, dest_crommwell_configs_dir)



def create_project(project_root='./', project_name='my_new_wdl_pipeline'):
    '''
    create project directory structure and some basic files.
    '''
    project_path = os.path.join(project_root, project_name)

    if os.path.exists(project_path):
        sys.exit(project_path + ' exists! Exit!')

    make_project_dirs(project_path)

    create_readme(project_path=project_path)

    create_pkg_info(project_path=project_path)

    copy_cromwell_configs(project_path=project_path)



def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()

    parser = get_para(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    args.project_root = os.path.abspath(args.project_root)

    print(args)

    create_project(
        project_root=args.project_root,
        project_name=args.project_name)


if __name__ == '__main__':
    main(paras=sys.argv[1:])


