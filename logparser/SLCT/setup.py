from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build_py import build_py as build_py
from Cython.Build import cythonize
import numpy
import shutil

print('Building extenstion modules...')
print('==============================================')
ext_modules=[Extension('slct',
                             ['logparser/slct/slct.pyx',
                             'logparser/slct/cslct.c'],
                             include_dirs=[numpy.get_include()],
                extra_compile_args=["-O2"]         
             )]

setup(
  name = "SLCT Cython module",
  cmdclass={'build_py': build_py},
  ext_modules = cythonize(ext_modules)
)
shutil.move('slct.so', 'logparser/slct.so')
print('==============================================')
print("Build done.\n")