# Install Python API for AMPL:
$ python -m pip install amplpy --upgrade

# Install solver modules:
$ python -m amplpy.modules install highs gurobi cplex

# Activate your AMPL CE license:
$ python -m amplpy.modules run amplkey activate --uuid f384c8f3-d7d5-4268-8192-ec7d456f8433

# Import, load, and instantiate AMPL in Python:
$ python
>>> from amplpy import AMPL, modules
>>> modules.load() # load all AMPL modules
>>> ampl = AMPL() # instantiate AMPL object
