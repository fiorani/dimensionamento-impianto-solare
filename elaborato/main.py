import numpy as np
from scipy.optimize import linprog
from scipy.optimize import minimize
import matplotlib.pyplot as plt
'''
# Consumi
demand = 45  # Domanda energetica in kW che vale al giorno
grid_price_kw = 0.30  # Tariffe al kW dell'energia elettrica
grid_price_sell_kw = 0.05  # Tariffe al kW dell'energia elettrica venduta

# Sistema solare
solar_max_kwh  = 6  # Massima potenza in kW generabile dai pannelli solari
solar_degradation = 0.05  # Fattore di degrado annuale dei pannelli solari
solar_price_kw = 50  # Prezzo al kW del sistema solare

# Batteria
storage_max_kw  = 10  # Capacità in kW massima della batteria
storage_price_kw = 10  # Prezzo al kW della batteria
storage_degradation = 0.10  # Fattore di degrado annuale dello stoccaggio dell'energia

# Durata
life = 10  # Anni di vita per la batteria e il sistema solare

# Curva impianto solare
hours = np.arange(0, 24)
solar_curve = solar_max_kwh  * np.sin(np.pi * (hours - 7) / 12)  # Funzione sinusoidale per rappresentare la generazione solare
solar_curve[solar_curve < 0] = 0  # Imposta a 0 la generazione solare quando è negativa

# Curva batteria
battery_energy = np.zeros_like(solar_curve)  # Inizializza l'array per l'energia accumulata nella batteria
for i in range(1, len(hours)):
    excess_energy = max(solar_curve[i] - demand / 24, 0)  # Energia in eccesso rispetto alla domanda
    deficit_energy = max(demand / 24 - solar_curve[i], 0)  # Energia mancante rispetto alla domanda
    battery_energy[i] = battery_energy[i-1] + excess_energy - deficit_energy
    battery_energy[i] = max(0, min(battery_energy[i], storage_max_kw ))

# Plot della curva solare, della curva della batteria e della domanda energetica
plt.figure(figsize=(10, 6))
plt.plot(hours, solar_curve, label="Energia prodotta")
plt.plot(hours, battery_energy, label="Batteria")
plt.plot(hours, np.full_like(hours, demand)/24, label="Consumo")
plt.xlabel("Ore del giorno")
plt.ylabel("Potenza (kW)")
plt.legend()
plt.grid(True)
plt.show()

#impianto solare
energy_generated = np.sum(solar_curve)*365* life
energy_used = np.sum(np.minimum(solar_curve, demand/24))*365* life
energy_sell= energy_generated-energy_used
energy_consu=demand *365* life
solar_lifetime_cost = grid_price_kw*energy_used +  grid_price_sell_kw*energy_sell -(solar_max_kwh*solar_price_kw)
grid_energy_cost = - grid_price_kw * energy_consu
print("Energia generata dall'impianto solare:", energy_generated)
print("Energia usata dall'impianto solare:", energy_used)
print("Energia venduta dall'impianto solare:", energy_sell)
print("risparmio dell'energia generata dall'impianto solare:", solar_lifetime_cost)
print("Costo dell'energia acquistata dalla rete elettrica:", grid_energy_cost)
if solar_lifetime_cost > grid_energy_cost:
    print("Conviene l'installazione dell'impianto solare.")
else:
    print("Non conviene l'installazione dell'impianto solare.")
    
    
#impianto solare con accumolo
storage_energy_used = np.sum(np.minimum(solar_curve+battery_energy, demand/24))*365* life
storage_energy_sell= energy_generated-storage_energy_used
storage_solar_lifetime_cost = grid_price_kw*storage_energy_used +  grid_price_sell_kw*storage_energy_sell -(storage_max_kw*storage_price_kw)-(solar_max_kwh*solar_price_kw)
print("Energia usata dall'impianto solare:", storage_energy_used)
print("Energia venduta dall'impianto solare:", storage_energy_sell)
print("risparmio dell'energia generata dall'impianto solare con accumolo:", storage_solar_lifetime_cost)
if storage_solar_lifetime_cost > grid_energy_cost:
    print("Conviene l'installazione dell'impianto solare con accumolo.")
else:
    print("Non conviene l'installazione dell'impianto solare con accumolo.")
    
    
    
    
    
    

ore=24
C_impianto = 500/(25*365)  # Costo dell'impianto solare in euro/kW al giorno 500euro/kw in 25anni
C_batteria = 1000/(10*365)  # Costo della batteria di accumulo in euro/kW al giorno 1000euro/kw in 10anni
C_elettrica = 0.3  # Costo dell'energia elettrica dalla rete in euro/kWh
E_consumo = 2    # Consumo energetico all'ora dell'abitazione in kWh
p_max_impianto = 6  # Potenza massima dell'impianto solare in kW
p_max_batteria = 15  # Capacità massima della batteria di accumulo in kW

def objective(x, C_impianto, C_batteria, C_elettrica, E_consumo):
    P_impianto, P_batteria = x
    
    hours = np.arange(0, ore)
    solar_curve = P_impianto * np.sin(np.pi * (hours-7) / 12)  # Funzione sinusoidale per rappresentare la generazione solare
    solar_curve = np.maximum(solar_curve, 0)  # Imposta a 0 la generazione solare quando è negativa
    battery_energy = np.zeros_like(solar_curve)  # Inizializza l'array per l'energia accumulata nella batteria
    battery_charge = np.zeros_like(solar_curve)
    battery_discharge = np.zeros_like(solar_curve)
    eccesso = np.zeros_like(solar_curve)
    for i in range(1, len(hours)):
        if np.sum(battery_energy) <= P_batteria : 
            battery_charge[i] = max(solar_curve[i] - E_consumo, 0)  # Energia in eccesso rispetto alla domanda 
        else :
            eccesso[i] = max(solar_curve[i] - E_consumo, 0)  # Energia in eccesso rispetto alla domanda 
        if battery_energy[i-1]> E_consumo : 
            battery_discharge[i] = max(E_consumo - solar_curve[i], 0)  # Energia mancante rispetto alla domanda
        else :
            battery_discharge[i] = max(battery_energy[i-1]-E_consumo, battery_energy[i-1])
        battery_energy[i] = battery_energy[i-1] + battery_charge[i] -  battery_discharge[i]
        battery_energy[i] = max(0, min(battery_energy[i], P_batteria))
    E_impianto_generata = np.sum(solar_curve)  # Energia generata durante il giorno
    E_impianto_usata = E_impianto_generata - np.sum(battery_charge)- np.sum(eccesso) # Energia usata dall'impianto durante il giorno
    E_impianto_venduta = np.sum(eccesso)  # Energia venduta dall'impianto durante il giorno
    E_batteria_usata = np.sum(battery_discharge)  # Energia usata dalla batteria durante il giorno
    print("E_impianto_usata:", E_impianto_usata, "E_impianto_venduta",E_impianto_venduta,"E_batteria_usata",E_batteria_usata)
    
    plt.figure(figsize=(24,6))
    plt.plot(hours, solar_curve, label="Energia prodotta")
    plt.plot(hours, battery_energy, label="Batteria")
    plt.plot(hours, eccesso, label="eccesso")
    plt.plot(hours, battery_charge, label="Batteria ricarica")
    plt.plot(hours, battery_discharge, label="Batteria scarica")
    plt.plot(hours, np.full_like(hours, E_consumo), label="Consumo")
    plt.xlabel("Ore del giorno")
    plt.ylabel("Potenza (kW)")
    plt.legend()
    plt.grid(True)
    plt.show()
    costo_totale = C_impianto * P_impianto + C_batteria * P_batteria + ((E_consumo*ore) - E_impianto_usata - E_batteria_usata - E_impianto_venduta) * C_elettrica
    #print("Costo totale iterazione:", costo_totale, "euro potenza impianto",P_impianto,"potenza batteria",P_batteria)
    return costo_totale

# Vincoli

def constraint(x):
    P_impianto, P_batteria = x
    if P_impianto==0:
        return 0
    else :
        return P_batteria

bounds = [
    (0, p_max_impianto), (0, p_max_batteria)
    ]
# Vincoli
cons = [
        {'type': 'eq', 'fun': constraint}
        ]

# Valori iniziali delle variabili decisionali
x0 = [3, 15]

# Ottimizzazione
res = minimize(objective, x0, args=(C_impianto, C_batteria, C_elettrica, E_consumo),
               #constraints=cons,
               bounds=bounds,
               options={'disp': True})

# Risultati
print("Stato dell'ottimizzazione:", res.success)
print("Messaggio dell'ottimizzazione:", res.message)
print("Potenza dell'impianto solare ottimale:", res.x[0], "kW")
print("Potenza della batteria di accumulo ottimale:", res.x[1], "kW")
print("Costo totale dell'energia elettrica:", res.fun, "euro")
'''
    
    
    


ore = 24  # numero di ore
C_impianto = 250/(25*365) # Costo dell'impianto solare in euro/kW all'ora (500 euro/kW in 25 anni)
C_batteria = 500/(10*365)  # Costo della batteria di accumulo in euro/kW all'ora (1000 euro/kW in 10 anni)
C_elettrica_acquistata = 0.3  # Costo dell'energia elettrica dalla rete in euro/kWh
C_elettrica_venduta = 0.1  # Costo dell'energia elettrica dalla rete in euro/kWh
p_max_impianto = 6 # Potenza massima dell'impianto solare in kWh
p_max_batteria = 15  # Capacità massima della batteria di accumulo in kW
E_consumo = np.zeros(ore*60)  # Inizializza l'array con tutti gli elementi a 0

for i in range(ore*60):
    E_consumo[i] =1/60
    if(i >1000):
        E_consumo[i] = 1/60
    
    
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
    
    plt.figure(figsize=(24, 6))
    plt.plot(minutes/60, solar_curve*60, label="Energia prodotta")
    plt.plot(minutes/60, battery_energy*60, label="Batteria")
    plt.plot(minutes/60, eccesso*60, label="eccesso")
    plt.plot(minutes/60, battery_charge*60, label="Batteria ricarica")
    plt.plot(minutes/60, battery_discharge*60, label="Batteria scarica")
    plt.plot(minutes/60, E_consumo*60, label="Consumo")
    plt.xlabel("ore")
    plt.ylabel("Potenza (kW)")
    plt.legend()
    plt.grid(True)
    plt.show()
    
   
    costo_totale = C_impianto * P_impianto + C_batteria * P_batteria + E_acquistata * C_elettrica_acquistata - C_elettrica_venduta * E_impianto_venduta -E_risparmiata* C_elettrica_acquistata
    print("P_impianto:",P_impianto,"P_batteria:", P_batteria,"Costo totale iterazione:", costo_totale,"E_impianto_generata:", E_impianto_generata,"E_impianto_usata:", E_impianto_usata, "E_impianto_venduta",E_impianto_venduta,"E_batteria_usata",E_batteria_usata,"E_acquistata",E_acquistata)
    return costo_totale

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
    return [p_max_impianto - P_impianto, p_max_batteria - P_batteria]  # Restituisce una lista con le differenze

# Definizione dei vincoli
cons = [#{'type': 'eq', 'fun': constraint},
       # {'type': 'ineq', 'fun': constraint1},
       #{'type': 'ineq', 'fun': constraint2}
       ]
bounds = [(0, p_max_impianto), (0, p_max_batteria)]
# Valori iniziali delle variabili decisionali
x0 = [0, 0]
options = { 'eps': [1, 1]}
# Ottimizzazione
res = minimize(objective, x0, args=(C_impianto, C_batteria, C_elettrica_acquistata, E_consumo,C_elettrica_venduta),bounds=bounds,constraints=cons,tol=1e-2,options=options)

# Risultati
print("Stato dell'ottimizzazione:", res.success)
print("Messaggio dell'ottimizzazione:", res.message)
print("Potenza dell'impianto solare ottimale:", res.x[0], "kW")
print("Potenza della batteria di accumulo ottimale:", res.x[1], "kW")
print("Costo totale dell'energia elettrica:", res.fun, "euro")



