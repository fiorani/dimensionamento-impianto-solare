from amplpy import AMPL, modules
modules.load() # load all AMPL modules
ampl = AMPL() # instantiate AMPL object
ampl.read('test.mod') # Caricare il modello da file
ampl.read_data('test.dat') # Caricare i dati da file
ampl.option["solver"] = "highs" # Risolvere il modello
ampl.solve()
print("Total_Profit is:", ampl.get_objective('Total_Profit').get().value())
print("x is:", ampl.get_variable('X').get_values())