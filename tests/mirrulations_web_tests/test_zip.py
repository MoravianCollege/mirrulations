import zipfile
import mirrulations_web.directory_zip as dz
import os

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../test_files/regulations-data/")
add_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../test_files/mirrulations_web_files/")

AHRQ_path = "AHRQ_FRDOC/AHRQ_FRDOC_0001/AHRQ_FRDOC_0001-0036"


def make_replacement_zip(file):
    replacement = open(file, 'w+')
    replacement.write('')
    replacement.close()


def test_add_readme():
    zipfile_path = add_PATH+"AHRQ_FRDOC_0001-0036.zip"
    dz.add_readme(zipfile_path, "AHRQ_FRDOC_0001-0036")
    archive = zipfile.ZipFile(zipfile_path)
    f = bytes.decode(archive.read('README.md'))
    assert f == "This is a README file for AHRQ_FRDOC_0001-0036"
    make_replacement_zip(zipfile_path)


def test_zip_directory():
    zipped_directory = dz.zip_directory_zip_version('AHRQ_FRDOC_0001-0036', PATH + AHRQ_path)
    archive = zipfile.ZipFile(zipped_directory.filename, 'r')
    readme_file = bytes.decode(archive.read('README.md'))
    json_file = bytes.decode(archive.read('AHRQ_FRDOC_0001-0036/doc.AHRQ_FRDOC_0001-0036.json'))
    assert readme_file == 'This is a README file for AHRQ_FRDOC_0001-0036'
    assert json_file == '{}'
    os.remove(zipped_directory.filename)
