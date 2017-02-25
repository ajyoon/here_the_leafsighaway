from distutils.core import setup

setup(
    name='Part Maker',
    version='',
    packages=['gui', 'top', 'lily', 'chance', 'shared', 'image_tools', 'instruments', 'document_tools',
              'special_instructions'],
    install_requires=["reportlab", "Pillow", "PyPDF2"],
    url='',
    license='',
    author='Andrew Yoon',
    author_email='',
    description=''
)
