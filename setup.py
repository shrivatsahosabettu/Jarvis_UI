import os

from setuptools import setup

from version import version_info

base_url = 'https://github.com/thevickypedia/Jarvis_UI'

# https://pypi.org/classifiers/
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Information Technology',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Multimedia :: Sound/Audio :: Speech',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Multimedia :: Sound/Audio :: Conversion',
    'Natural Language :: English'
]


def read(name: str) -> str:
    """Reads the file that was received as argument.

    Args:
        name: Name of the file that has to be opened and read.

    Returns:
        str:
        Content of the file that was read.

    References:
        https://pythonhosted.org/an_example_pypi_project/setuptools.html#setting-up-setup-py
    """
    req_file = os.path.join(os.path.dirname(__file__), name)
    if os.path.isfile(req_file):
        with open(req_file) as file:
            content = file.read()
        return content
    else:
        return ""


def dependencies() -> list:
    """Gathers dependencies from requirements file.

    Returns:
        list:
        List of dependencies to be installed.
    """
    requirement_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib', 'requirements.txt')
    if os.path.isfile(requirement_file):
        with open(requirement_file) as requirements:
            install_requires = requirements.read().splitlines()
    return install_requires


setup(
    name='jarvis-ui',
    version='.'.join(str(c) for c in version_info),
    description="Jarvis UI to perform voice commands via API calls.",
    long_description=read('README.md') + '\n\n' + read('CHANGELOG'),
    long_description_content_type='text/markdown',
    author='Vignesh Sivanandha Rao',
    author_email='svignesh1793@gmail.com',
    License='MIT',
    url=base_url,
    python_requires=">=3.8",
    install_requires=dependencies(),
    classifiers=classifiers,
    keywords='python, natural-language-processing, text-to-speech, speech-recognition, jarvis, hotword-detection,'
             'virtual-assistant, multiprocessing, threadpool',
    download_url=f'{base_url}/archive/main.zip',
    project_urls={
        'Source': base_url,
        'Docs': 'https://thevickypedia.github.io/Jarvis_UI',
        'Bug Tracker': f'{base_url}/issues'
    },
    zip_safe=True
)