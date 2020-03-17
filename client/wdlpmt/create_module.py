#!/usr/bin/env python3
import sys
import os
import re
import argparse

# not finished!!!

def get_para(parser):
    # create a new module
    parser.add_argument('-project_root', metavar='<directory>',
        default='./',
        help="the project_root directory (which has the subdirectory 'src/wdl') [%(default)s]")

    parser.add_argument('-module_name', metavar='<file>', required=True, help="module name")

    return parser


def create_readme(project_root='./', module_path='./', module_name=None):
    '''
    Create a readme on how to organize the codes for a module.
    '''

    content = '''How to organize codes for a module?

# 1.Tasks

In the '{module_path}/Tasks/' directory,
create a *.wdl file (e.g., single_function_task.wdl), which should be
a WDL **task** with a minimum function:

task copyFileTask{{
    String in_file
    String out_file
    String thread = 2
    String mem_size = '4G'

    String workdir
    String? root='/export/'
    String? docker_prefix = ''

    command <<<
    set -ex
    mkdir -p ${{workdir}}
    cd ${{workdir}}

    cat ${{in_file}} > ${{out_file}}

    >>>

    output {{
        String result_file = workdir + '/' + out_file
    }}

    runtime {{
        docker: docker_prefix + "my-docker-image-name"
        root: root
        cpu: thread
        memory: mem_size
    }}

}}


**Do not** write a WDL **workflow** in this file.


This means that this *.wdl file can not be executed directly by the Cromwell
engine, because it needs a **workflow** as the enterance.

Next, validate the grammar of 'single_function_task.wdl' file:
$ java -jar ${{womtool_jar}} validate {module_path}/Tasks/single_function_task.wdl

Modify your *.wdl file if there are any grammar errors reported.


# 2.TestTasks

Whenever you finish writing a *.wdl file in the
'{module_path}/Tasks/' directory, come to this
'{module_path}/TestTasks/' directory immediately!!

And then create a *.wdl file (e.g., run_single_function_task.wdl),
which should be a WDL **workflow** for running the 'single_function_task.wdl'
file in the 'Tasks/' directory.

On the head of 'run_single_function_task.wdl' script, there should be a line
like this:

import src/wdl/{module_name}/Tasks/single_function_task.wdl as my_fun

Then in the workflow section you can call it like this:

call my_fun.copyFileTask as RuncopyFileTask {{
    input:
        in_file = in_file,
        out_file = out_file,
        thread = thread,
        mem_size = mem_size,
        workdir = workdir,
        root = root,
        mem_size = mem_size,
}}



Then, go to the '{project_root}' directory:
$ cd {project_root}

Step 1. compress the 'src/' directory:
$ zip -r src.zip src/

Step 2. validate the grammar of 'run_single_function_task.wdl' script:
$ java -jar ${{womtool_jar}} validate {module_path}/TestTasks/run_single_function_task.wdl


Step 3. Prepare a JSON file:
$ java -jar ${{womtool_jar}} inputs {module_path}/TestTasks/run_single_function_task.wdl > input.json

You can redirect the output to else where and then change to that directory by yourself.


Step 4. Set up the parameter values of the 'input.json' file.


Step 5. run the 'run_single_function_task.wdl' file:
$ java -Dsystem.job-shell=/bin/sh \
-Dconfig.file=${{cromwell_config}} \
-jar ${{cromwell_jar}} run \
{module_path}/TestTasks/run_single_function_task.wdl \
-p {project_root}/src.zip \
-i input.json \
1>crm.log 2>crm.err


A few cromwell configure files and run scirpts should have been placed in the
'{project_root}/docker' directory when you create this project. You can use
these scripts (e.g. the 'localhost.docker.sh' file) to run
'{module_path}/TestTasks/run_single_function_task.wdl'


When this test run succeeds, you can write another *.wdl file in the
'{module_path}/Tasks/' directory and repeat the steps mentioned above.



# 3. Workflow
When all your codes in '{module_path}/Tasks/' and '{module_path}/TestTasks/'
are finished, you can integrate them together by creating a file
like '{module_name}.wdl' in the '{module_path}/Workflow' directory.

Normally, this file should only "import" the files in the
'{module_path}/TestTasks/' directory. I do not recommend to "import" any files
in the '{module_path}/Tasks/' directory.

'''.format(project_root=project_root, module_path=module_path, module_name=module_name)

    module_readme_file = os.path.join(module_path, 'README.md')
    with open(module_readme_file, 'w') as fh:
        print(content, file=fh)

    return module_readme_file


def create_module(project_root='./', module_name='my_module'):
    '''
    create module directory structure and some basic files.
    '''
    module_path = os.path.join(project_root, 'src', 'wdl', module_name)

    if os.path.exists(module_path):
        sys.exit(module_path + ' exists! Exit!')

    os.makedirs(module_path, exist_ok=True)

    Tasks_dir = os.path.join(module_path, 'Tasks')
    os.makedirs(Tasks_dir, exist_ok=True)

    TestTasks_dir = os.path.join(module_path, 'TestTasks')
    os.makedirs(TestTasks_dir, exist_ok=True)

    Workflow_dir = os.path.join(module_path, 'Workflow')
    os.makedirs(Workflow_dir, exist_ok=True)

    create_readme(
        project_root=project_root,
        module_path=module_path,
        module_name=module_name)



def main(parser=None, paras=None):

    if not parser:
        parser = argparse.ArgumentParser()


    parser = get_para(parser)


    if len(sys.argv) == 1 or len(paras) == 0:
        parser.print_help()
        sys.exit()

    args = parser.parse_args(paras)

    args.project_root = os.path.abspath(args.project_root)

    print(args)

    create_module(
        project_root=args.project_root,
        module_name=args.module_name)

if __name__ == '__main__':
    main(paras=sys.argv[1:])

