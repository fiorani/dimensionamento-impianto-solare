import numpy as np
from scipy.optimize import linprog
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ore = 24  # numero di ore
C_impianto = 250/(25*365) # Costo dell'impianto solare in euro/kW al giorno (500 euro/kW in 25 anni)
C_batteria = 500/(10*365)  # Costo della batteria di accumulo in euro/kW al giorno (1000 euro/kW in 10 anni)
C_elettrica_acquistata = 0.3  # Costo dell'energia elettrica dalla rete in euro/kWh
C_elettrica_venduta = 0.1  # valore dell'energia elettrica venduta in euro/kWh
p_max_impianto = 6 # Potenza massima dell'impianto solare in kWh
p_max_batteria = 15  # Capacità massima della batteria di accumulo in kW
E_consumo = np.zeros(ore*60)  # Inizializza l'array con tutti gli elementi a 0

for i in range(ore*60):
    E_consumo[i] =1/60
    
def plot(P_impianto, P_batteria):
    minutes = np.arange(0, ore*60)
    solar_curve = P_impianto/60 * np.sin(np.pi * (minutes) / (12 * 60))  # Funzione sinusoidale per rappresentare la generazione solare
    solar_curve = np.maximum(solar_curve, 0)
    battery_energy = np.zeros_like(solar_curve)  
    battery_charge = np.zeros_like(solar_curve)
    battery_discharge = np.zeros_like(solar_curve)
    eccesso = np.zeros_like(solar_curve)
    
    for i in range(1, len(minutes)):
        if battery_energy[i-1]*60 < P_batteria : 
            battery_charge[i] = max(solar_curve[i] - E_consumo[i], 0)  
        else :
            eccesso[i] = max(solar_curve[i] - E_consumo[i], 0) 
        if battery_energy[i-1]>0:
            battery_discharge[i] = max(E_consumo[i] - solar_curve[i], 0)  
        battery_energy[i] = battery_energy[i-1] + battery_charge[i]/60 - battery_discharge[i]/60
        battery_energy[i] = max(0, min(battery_energy[i], P_batteria/60))

    plt.clf()
    fig, ax = plt.subplots(figsize=(24, 6))
    ax.plot(minutes/60, solar_curve*60, label="Energia prodotta")
    ax.plot(minutes/60, battery_energy*60, label="Batteria")
    ax.plot(minutes/60, eccesso*60, label="eccesso")
    ax.plot(minutes/60, battery_charge*60, label="Batteria ricarica")
    ax.plot(minutes/60, battery_discharge*60, label="Batteria scarica")
    ax.plot(minutes/60, E_consumo*60, label="Consumo")
    ax.set_xlabel("ore")
    ax.set_ylabel("Potenza (kW)")
    ax.legend()
    ax.grid(True)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    
    
#funzione obiettivo
def objective(x, C_impianto, C_batteria, C_elettrica_acquistata, E_consumo,C_elettrica_venduta):
    P_impianto, P_batteria = x
    
    minutes = np.arange(0, ore*60)
    solar_curve = P_impianto/60 * np.sin(np.pi * (minutes) / (12 * 60))  # Funzione sinusoidale per rappresentare la generazione solare
    solar_curve = np.maximum(solar_curve, 0)
    battery_energy = np.zeros_like(solar_curve)  
    battery_charge = np.zeros_like(solar_curve)
    battery_discharge = np.zeros_like(solar_curve)
    eccesso = np.zeros_like(solar_curve)
    
    for i in range(1, len(minutes)):
        if battery_energy[i-1]*60 < P_batteria : 
            battery_charge[i] = max(solar_curve[i] - E_consumo[i], 0)  
        else :
            eccesso[i] = max(solar_curve[i] - E_consumo[i], 0) 
        if battery_energy[i-1]>0:
            battery_discharge[i] = max(E_consumo[i] - solar_curve[i], 0)  
        battery_energy[i] = battery_energy[i-1] + battery_charge[i]/60 - battery_discharge[i]/60
        battery_energy[i] = max(0, min(battery_energy[i], P_batteria/60))
    
    E_impianto_generata = np.sum(solar_curve) 
    E_impianto_venduta = np.sum(eccesso)  
    E_impianto_usata = E_impianto_generata - np.sum(battery_charge) - np.sum(eccesso) 
    E_batteria_usata = np.sum(battery_discharge)
    E_acquistata=np.sum(E_consumo) - E_impianto_usata - E_batteria_usata
    E_risparmiata=np.sum(E_consumo) - E_acquistata
    
    costo_totale = C_impianto * P_impianto + C_batteria * P_batteria + E_acquistata * C_elettrica_acquistata - C_elettrica_venduta * E_impianto_venduta - E_risparmiata* C_elettrica_acquistata
    #print("P_impianto:",P_impianto,"P_batteria:", P_batteria,"Costo totale iterazione:", costo_totale,"E_impianto_generata:", E_impianto_generata,"E_impianto_usata:", E_impianto_usata, "E_impianto_venduta",E_impianto_venduta,"E_batteria_usata",E_batteria_usata,"E_acquistata",E_acquistata)
    return costo_totale

# Definizione dei vincoli
def constraint(x):
    P_impianto, P_batteria = x
    if P_impianto == 0:
        return P_impianto
    else:
        return P_batteria

def constraint1(x):
    P_impianto, P_batteria = x
    return [P_impianto, P_batteria]

def constraint2(x):
    P_impianto, P_batteria = x
    return [p_max_impianto - P_impianto, p_max_batteria - P_batteria]

cons = [
        {'type': 'ineq', 'fun': constraint},
        {'type': 'ineq', 'fun': constraint1},
        {'type': 'ineq', 'fun': constraint2}
       ]

bounds = [(0, p_max_impianto), (0, p_max_batteria)]

# Valori iniziali delle variabili decisionali
x0 = [0, 0]

# specifico l'incremnto dei valori
options = {'eps': [1, 1]}


def run_optimization():
    try:
        res = minimize(objective, x0, args=(C_impianto, C_batteria, C_elettrica_acquistata, E_consumo, C_elettrica_venduta), bounds=bounds, constraints=cons, tol=1e-2, options=options)

        result_text.set(f"Potenza dell'impianto solare ottimale: {res.x[0]:.2f} kW\n"
                        f"Potenza della batteria di accumulo ottimale: {res.x[1]:.2f} kW\n"
                        f"Risparmio giornaliero: {res.fun:.2f} euro")
        plot(res.x[0],res.x[1])
        
    except Exception as e:
        messagebox.showerror("Error", f"Si è verificato un errore: {e}")

root = Tk()
root.title("Solar Power Optimization")

frame = Frame(root)
frame.pack(padx=20, pady=20)

run_button = Button(frame, text="Esegui Ottimizzazione", command=run_optimization)
run_button.pack()

result_text = StringVar()
result_label = Label(frame, textvariable=result_text)
result_label.pack()

plot_frame = Frame(root)
plot_frame.pack()

root.mainloop()


