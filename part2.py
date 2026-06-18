import time
from pathlib import Path
import pandas as pd

def find_suspicious_agents(registry):
    access_key_map = {} 
    alias_map = {}      
    suspicious_ids = set() 
    
    print("[SYSTEM] Scanning registry via O(n) Hash Map...")
    time.sleep(0.5)
    
    for record in registry:
        agent_id = record['Agent_ID']
        alias = record['Alias']
        access_key = record['Access_Key']
        
        if access_key in access_key_map:
            if agent_id not in suspicious_ids:
                print(f"  [!] KEY COLLISION: '{access_key}' shared by {agent_id} and {access_key_map[access_key]}")
            
            suspicious_ids.add(agent_id) 
            suspicious_ids.add(access_key_map[access_key]) 
        else:
            access_key_map[access_key] = agent_id
            
        normalized_alias = alias.lower().replace("_", "").replace(" ", "")
        
        if normalized_alias in alias_map:
            if agent_id not in suspicious_ids:
                 print(f"  [!] ALIAS COLLISION: Normalized '{normalized_alias}' shared by {agent_id} and {alias_map[normalized_alias]}")
            
            suspicious_ids.add(agent_id) 
            suspicious_ids.add(alias_map[normalized_alias]) 
        else:
            alias_map[normalized_alias] = agent_id

    print("\n[SYSTEM] Scan complete. Extracting full profiles...\n")
    time.sleep(0.5)
    
    suspicious_details = [rec for rec in registry if rec['Agent_ID'] in suspicious_ids]
    return suspicious_details

def load_data_from_excel(file_path, target_sheet='C'):
    """
    Reads agent registry data from the Excel file.
    Uses header=1 to skip the first instruction row.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet, header=1)
        df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
        df.dropna(subset=['Agent_ID'], inplace=True)
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Ensure it is in the same directory.")
        return []
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []

if __name__ == "__main__":
    file_name = Path(__file__).with_name('Part 2.xlsx')
    registry_data = load_data_from_excel(file_name, target_sheet='C')
    
    if registry_data:
        print("=" * 70)
        print(f"{'OPERATION: DOUBLE AGENT REGISTRY PURGE':^70}")
        print("=" * 70)
        
        anomalies = find_suspicious_agents(registry_data)

        print(f"[ALERT] Isolated {len(anomalies)} suspicious entries:")
        print("=" * 70)
        print(f"{'Agent ID':<10} | {'Alias':<12} | {'Key':<6} | {'Status':<12} | {'Linked Site'}")
        print("-" * 70)
        
        for anomaly in anomalies:
            print(f"{anomaly['Agent_ID']:<10} | {anomaly['Alias']:<12} | {anomaly['Access_Key']:<6} | {anomaly['Status']:<12} | {anomaly['Linked_Site']}")
        print("=" * 70)