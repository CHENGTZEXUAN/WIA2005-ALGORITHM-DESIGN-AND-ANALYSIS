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
    
    eg_sector, eg_strat, eg_time = run_epsilon_greedy_upstream_filtered(dataset)
    print(f"[ALGORITHM 2: Epsilon-Greedy Algorithm]")
    print(f" -> Chosen Route   : {eg_sector}")
    print(f" -> Selection Mode : {eg_strat}")
    print(f" -> Execution Time : {eg_time * 1e6:.2f} microseconds\n")
    


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