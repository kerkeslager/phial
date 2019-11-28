import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='fwx',
    version='0.0.1',
    scripts=['fwx.py'] ,
    author='David Kerkeslager',
    author_email='kerkeslager+pypi@gmail.com',
    description='A minimalist functional web framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kerkeslager/fwx',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
)
