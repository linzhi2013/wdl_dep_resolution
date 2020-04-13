from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import PackageForm
from .models import Package, PkgFile
from django.template import loader

from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth import logout
from django.conf import settings

from haystack.generic_views import SearchView

import os
import re
import subprocess
import sys
import glob

def index(request):
    pkg_list = Package.objects.order_by('name')
    template = loader.get_template('pipeline/index.html')
    context = {
        'pkg_list': pkg_list,
    }
    return HttpResponse(template.render(context, request))


def pkg_detail(request, pkg_id):
    pkg_obj = Package.objects.get(id=pkg_id)
    return HttpResponse("You're looking at package {0}, {1}, {2}".format(pkg_id, pkg_obj.name, pkg_obj.version))


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = PackageForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES['file']
            file_name = os.path.basename(file_obj.name)
            print('uploaded file name:', file_name, flush=True)

            # validate file name format
            if not re.match(r'[a-z]+(\_[a-z0-9]+)*\-\d+(\.\d+)*\.tar\.gz$', file_name):
                return HttpResponse("the uploaded file's filename format is not correct: {0}".format(file_name))

            pkg_name, version_str = file_name.split('-', 1)
            pkg_name = pkg_name.lower()
            version = version_str.replace('.tar.gz', '')

            # check if the same package exists
            old_pkgs = Package.objects.filter(name=pkg_name, version=version)
            if old_pkgs:
                return HttpResponse('package: {pkg_name}<{version}> already exists!!\nYou must use a new version number!'.format(pkg_name=pkg_name, version=version))

            temp_file_path = file_obj.temporary_file_path()
            pkg_deps, author, project_url, description, decompressed_pkg_dir = get_pkg_info(temp_file_path, file_name)


            # save the newly uploaded file
            instance = Package(name=pkg_name, version=version, deps=pkg_deps, file=file_obj, author=author, project_url=project_url, description=description)
            instance.save()

            # save each WDL file content
            package = Package.objects.get(id=instance.id)
            extract_file_content(decompressed_pkg_dir=decompressed_pkg_dir, package=package)


            # push to gitlab
            if settings.UPLOAD_TO_GITLAB:
                push_to_gitlab(
                    project_dir = settings.GITLAB_DIR,
                    pkg_name=file_name)

            return HttpResponse('uploaded!')
    else:
        form = PackageForm()

    return render(request, 'pipeline/upload.html', {
        'form': form
    })


def download_pkg(request, pkg_id):
    pkg_obj = Package.objects.get(id=pkg_id)
    file_path = pkg_obj.file.path
    pkg_tarfile = "{name}-{version}.tar.gz".format(name=pkg_obj.name, version=pkg_obj.version)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pkg_tarfile)
            return response
    raise Http404


def get_pkg_info(temp_file_path, file_name):
    # extract the tarball file
    decompressedFiles_dir = os.path.join(settings.GITLAB_DIR, 'decompressed_files')

    if not os.path.exists(decompressedFiles_dir):
        os.makedirs(decompressedFiles_dir, exist_ok=True)

    decompressed_pkg_tarfile =os.path.abspath(os.path.join(decompressedFiles_dir, file_name))
    pkg_tarfile = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'repo', file_name))

    decompressed_pkg_dir = os.path.join(decompressedFiles_dir, file_name).replace('.tar.gz', '')

    # delete previous files
    if os.path.exists(decompressed_pkg_dir):
        cmd = 'rm -rf {}'.format(decompressed_pkg_dir)
        subprocess.check_call(cmd, shell=True)

    if os.path.exists(pkg_tarfile):
        cmd = 'rm -rf {}'.format(pkg_tarfile)
        subprocess.check_call(cmd, shell=True)

    if os.path.exists(decompressed_pkg_tarfile):
        cmd = 'rm -rf {}'.format(decompressed_pkg_tarfile)
        subprocess.check_call(cmd, shell=True)


    cmd = "cp {temp_file_path} {decompressed_pkg_tarfile}".format(temp_file_path=temp_file_path, decompressed_pkg_tarfile=decompressed_pkg_tarfile)
    subprocess.check_call(cmd, shell=True)


    cmd2 = 'tar -zxf {0} -C {1}'.format(decompressed_pkg_tarfile, decompressedFiles_dir)
    subprocess.check_call(cmd2, shell=True)

    # get the deps
    pkg_info_file = os.path.join(decompressed_pkg_dir, 'pkg_info.txt')

    author = ''
    project_url = ''
    description = ''
    deps = []
    if os.path.exists(pkg_info_file):
        with open(pkg_info_file, 'r') as fh:
            for i in fh:
                i = i.strip()
                if not i or i.startswith('#'):
                    continue

                key, value = re.split(r'\:\s*', i, 1)
                if key == 'deps':
                    dep = value.split(',')
                    for k in dep:
                        k = k.strip()
                        deps.append(k)
                elif key == 'author':
                    author = value
                elif key == 'project_url':
                    project_url = value
                elif key == 'description':
                    description = value
    else:
        print('can not find', pkg_info_file, file=sys.stderr)

    pkg_deps = ','.join(deps)

    cmd3 = 'rm -rf {}'.format(decompressed_pkg_tarfile)
    subprocess.check_call(cmd3, shell=True)

    return pkg_deps, author, project_url, description, decompressed_pkg_dir


def extract_file_content(decompressed_pkg_dir=None, package=None):
    wdl_files = glob.glob(decompressed_pkg_dir + '/**/*.wdl', recursive=True)
    print('wdl_files:\n', wdl_files, flush=True)
    for f in wdl_files:
        with open(f, 'r') as fh:
            content = '\n'.join(fh.readlines())
        f_path = f.split('decompressed_files/')[-1]
        instance = PkgFile(package=package, file_path=f_path, content=content)
        instance.save()


def download_metadata_file(request):
    # pepare a metadata file
    metadata_file = os.path.join(settings.MEDIA_ROOT, 'metadata.txt')
    with open(metadata_file, 'w') as fhout:
        for e in Package.objects.all():
            print(e.id, e.name, e.version, e.deps, sep='\t', file=fhout)

    if os.path.exists(metadata_file):
        with open(metadata_file, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(metadata_file)
            return response

    raise Http404


def logout_view(request):
    logout(request)
    return index(request)


def push_to_gitlab(project_dir=None, pkg_name=None):
    '''
    cd <localdir>
    git init
    git add .
    git commit -m 'message'
    git remote add origin <url>
    git push -u origin master

    '''

    try:
        os.chdir(project_dir)

        hidden_git_folder = os.path.join(project_dir, '.git')
        if not os.path.exists(hidden_git_folder):
            cmd = 'git init'
            subprocess.check_call(cmd, shell=True)

            cmd = 'git remote add origin {0}'.format(settings.GITLAB_URL)
            subprocess.check_call(cmd, shell=True)

        cmd = "git pull origin master"
        subprocess.check_call(cmd, shell=True)

        cmd = "git add -A"
        subprocess.check_call(cmd, shell=True)

        cmd = '''git commit -m "add {pkg_name}"'''.format(pkg_name=pkg_name)
        subprocess.check_call(cmd, shell=True)

        cmd = "git push origin master"
        subprocess.check_call(cmd, shell=True)

    except Exception as e:
        print('push_to_gitlab failed!', file=sys.stderr)
        print(e, file=sys.stderr)



