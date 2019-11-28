import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='phial',
    version='0.0.1',
    scripts=['phial.py'] ,
    author='David Kerkeslager',
    author_email='kerkeslager+pypi@gmail.com',
    description='A minimalist functional web framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kerkeslager/phial',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
