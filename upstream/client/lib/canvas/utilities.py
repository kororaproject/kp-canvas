import os
import shutil
import subprocess
import tarfile
import zipfile

def copy_object_file(path, to_directory='.'):
    dst_path = os.path.join(to_directory, os.path.basename(path))

    shutil.copyfile(path, dst_path)

def execute_object_file(path):
    ret = subprocess.run(path, shell=True)

    return ret

def extract_object_file(path, to_directory='.'):
    if path.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif path.endswith('.tar.gz') or path.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif path.endswith('.tar.bz2') or path.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    else:
        raise ValueError("Could not extract `{0}` as no appropriate extractor is found".format(path))

    cwd = os.getcwd()
    os.chdir(to_directory)

    try:
        file = opener(path, mode)

        try:
            file.extractall()

        finally:
            file.close()

    finally:
        os.chdir(cwd)
