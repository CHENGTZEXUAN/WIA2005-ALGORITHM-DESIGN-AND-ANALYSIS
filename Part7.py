import pandas as pd
import time
import random

def load_excel_dataset(file_path):
    """
    Loads tactical metrics from Sheet C by dynamically determining the column offsets.
    """
    sector_matrix = {}

    df = pd.read_excel(file_path, sheet_name='C', header=None)
    df = df.fillna('')
    
    header_row_idx = -1
    offsets = {}
    
    for r_idx, row in df.iterrows():
        row_str = [str(val).strip().lower() for val in row]
        if any('sector' in val for val in row_str):
            header_row_idx = r_idx
            for c_idx, val in enumerate(row_str):
                if 'sector' in val: offsets['sector'] = c_idx
                elif 'patrol' in val: offsets['patrol_freq'] = c_idx
                elif 'thermal' in val: offsets['thermal_scan'] = c_idx
                elif 'drone' in val: offsets['drone_cover'] = c_idx
                elif 'predicted' in val: offsets['enemy_pred'] = c_idx
                elif 'decoy' in val: offsets['decoy_val'] = c_idx
            break

    required_keys = ['sector', 'patrol_freq', 'thermal_scan', 'drone_cover', 'enemy_pred', 'decoy_val']
    if header_row_idx == -1 or not all(k in offsets for k in required_keys):
        offsets = {
            'sector': 0, 'patrol_freq': 1, 'thermal_scan': 2, 
            'drone_cover': 3, 'enemy_pred': 4, 'decoy_val': 5
        }
        start_row = 1
    else:
        start_row = header_row_idx + 1

    for _, row in df.iloc[start_row:].iterrows():
        col_sector = str(row.iloc[offsets['sector']]).strip()       
        if col_sector == '' or 'sector' in col_sector.lower():
            continue
            
        try:
            patrol_freq  = int(float(row.iloc[offsets['patrol_freq']]))
            thermal_scan = int(float(row.iloc[offsets['thermal_scan']]))
            drone_cover  = int(float(row.iloc[offsets['drone_cover']]))
            enemy_pred   = str(row.iloc[offsets['enemy_pred']]).strip()
            decoy_val    = int(float(row.iloc[offsets['decoy_val']]))
            
            sector_matrix[col_sector] = {
                'Patrol_Freq': patrol_freq,
                'Thermal_Scan': thermal_scan,
                'Drone_Cover': drone_cover,
                'Enemy_Predicted': enemy_pred,
                'Decoy_Value': decoy_val
            }
            
        except Exception:
            continue
        
    return sector_matrix

def calculate_base_risk(sector_data):
    """ Risk = Patrol_Freq + Thermal_Scan + Drone_Cover """
    return sector_data['Patrol_Freq'] + sector_data['Thermal_Scan'] + sector_data['Drone_Cover']


def run_las_vegas_filtered(dataset, threat_limit=13):
    """ Solution 1: Pure Randomization with Downstream Filter """
    sectors = list(dataset.keys())
    iterations = 0
    start_time = time.perf_counter()
    
    while True:
        iterations += 1
        chosen_sector = random.choice(sectors)
        metrics = dataset[chosen_sector]
        risk = calculate_base_risk(metrics)
        
        if metrics['Enemy_Predicted'] == 'Yes' or risk > threat_limit:
            continue
        else:
            execution_time = time.perf_counter() - start_time
            return chosen_sector, iterations, execution_time


def run_epsilon_greedy_upstream_filtered(dataset, epsilon=0.20):
    """ Solution 2 (BEST): Epsilon-Greedy with Upstream Filter """
    start_time = time.perf_counter()
    
    safe_pool = {
        sec: data for sec, data in dataset.items() 
        if data['Enemy_Predicted'].lower() == 'no'
    }
    if not safe_pool:
        safe_pool = dataset 
        
    roll = random.random()
    if roll > epsilon:
        chosen_sector = min(
            safe_pool.keys(), 
            key=lambda s: (calculate_base_risk(safe_pool[s]) - safe_pool[s]['Decoy_Value'])
        )
        strategy_used = "Exploitation (Greedy Optimal)"
    else:
        chosen_sector = random.choice(list(safe_pool.keys()))
        strategy_used = "Exploration (Unpredictable Step)"
        
    execution_time = time.perf_counter() - start_time
    return chosen_sector, strategy_used, execution_time


def run_lcg_filtered(dataset, previous_state=0,threat_limit=13):
    """ Solution 3: LCG Math Wheel with Rejection Filter """
    sectors = list(dataset.keys())
    m = len(sectors)
    
    a = sum(d['Thermal_Scan'] for d in dataset.values()) | 1  
    c = sum(d['Patrol_Freq'] for d in dataset.values())
    
    iterations = 0
    state = previous_state
    start_time = time.perf_counter()
    
    while True:
        iterations += 1
        state = (a * state + c) % m
        chosen_sector = sectors[state]
        metrics = dataset[chosen_sector]
        risk = calculate_base_risk(metrics)
        
        if metrics['Enemy_Predicted'].lower() == 'yes' or risk > threat_limit:
            state = (state + 1) % m #Proof that this algorithm is not safe
            '''This part of the code exists because the algorithm freezed without it, by using the mathematical formula that is constant the algorithm might only jump between the few dangerous states, in order to prevent that from happening, this line of code is added to make sure that the algorithm does not freeze and the time complexity does not become unbounded.'''
            continue
        else:
            execution_time = time.perf_counter() - start_time
            return chosen_sector, state, iterations, execution_time


def render_vertical_dashboard(dataset):
    print("=" * 65)
    print("                       RUNTIME RESULTS        ")
    print("=" * 65)
    print(f"{'Sector':<8}{'Base Risk':<12}{'Enemy Predicted':<18}{'Decoy Value':<12}")
    print("-" * 65)
    for sector, metrics in dataset.items():
        risk = calculate_base_risk(metrics)
        print(f"{sector:<8}{risk:<12}{metrics['Enemy_Predicted']:<18}{metrics['Decoy_Value']:<12}")
    print("=" * 65)
    
    lv_sector, lv_iter, lv_time = run_las_vegas_filtered(dataset)
    print(f"[ALGORITHM 1: Las Vegas Algorithm]")
    print(f" -> Chosen Route   : {lv_sector}")
    print(f" -> Loop Iterations: {lv_iter}")
    print(f" -> Execution Time : {lv_time * 1e6:.2f} microseconds\n")
    
    eg_sector, eg_strat, eg_time = run_epsilon_greedy_upstream_filtered(dataset)
    print(f"[ALGORITHM 2: Epsilon-Greedy Algorithm]")
    print(f" -> Chosen Route   : {eg_sector}")
    print(f" -> Selection Mode : {eg_strat}")
    print(f" -> Execution Time : {eg_time * 1e6:.2f} microseconds\n")
    
    lcg_sector, new_state, lcg_iter, lcg_time = run_lcg_filtered(dataset, previous_state=0)
    print(f"[ALGORITHM 3: Filtered Linear Congruential Generator]")
    print(f" -> Chosen Route   : {lcg_sector}")
    print(f" -> Internal State : {new_state}")
    print(f" -> Loop Iterations: {lcg_iter}")
    print(f" -> Execution Time : {lcg_time * 1e6:.2f} microseconds")
    print("=" * 65)


if __name__ == "__main__":
    DATASET_PATH = "/Users/siew/Desktop/WIA2005-ALGORITHM-DESIGN-AND-ANALYSIS/Part 7.xlsx"
    
    try:
        tactical_matrix = load_excel_dataset(DATASET_PATH)
        if not tactical_matrix:
            print("Error: The dynamic offset engine could not find valid column headers on Sheet C.")
            exit()
            
        render_vertical_dashboard(tactical_matrix)
        
    except Exception as e:
        print(f"Critical System Crash: {e}")