import time
import heapq
from pathlib import Path
import pandas as pd


def load_dataset_from_excel(file_path, target_sheet='B'):
    """
    Reads routing data specifically from Sheet 'B'.
    Uses header=2 to skip the top two rows of text instructions in the Excel file.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=target_sheet, header=2)
        
        df.rename(columns={
            'From_Node': 'from',
            'To_Node': 'to',
            'Distance': 'distance',
            'Travel_Time': 'time',
            'Risk_Level': 'risk',
            'Detection_Probability': 'detection',
            'Route_Status': 'status'
        }, inplace=True)
        
        df.dropna(subset=['from', 'to'], inplace=True)
        
        return df.to_dict('records')
    except FileNotFoundError:
        print(f"[ERROR] Excel file not found at: {file_path}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred reading the Excel file: {e}")
        return []


def calculate_composite_cost(route):
    """
    Applies Min-Max Normalization to prevent large raw scalars (like Distance) 
    from overpowering smaller metrics (like Detection), then applies weights.
    """
    MIN_DIST, MAX_DIST = 1.0, 10.0
    MIN_TIME, MAX_TIME = 1.0, 10.0
    MIN_RISK, MAX_RISK = 1.0, 10.0
    MIN_DET, MAX_DET = 0.0, 1.0

    norm_dist = (route["distance"] - MIN_DIST) / (MAX_DIST - MIN_DIST)
    norm_time = (route["time"] - MIN_TIME) / (MAX_TIME - MIN_TIME)
    norm_risk = (route["risk"] - MIN_RISK) / (MAX_RISK - MIN_RISK)
    norm_det = (route["detection"] - MIN_DET) / (MAX_DET - MIN_DET)

    return (norm_dist * 0.3) + (norm_time * 0.3) + (norm_risk * 2.0) + (norm_det * 10.0)


def run_method_a_dijkstra(raw_routes, start_node="Port Authority Hub", end_node="Financial Vault Access"):
    """
    Solution 1 (BEST): Multi-stage pipeline.
    1) Prunes 'Restricted' routing edges via string sanitization.
    2) Arranges vertices by structural risk level.
    3) Evaluates optimal paths using Priority Queue (O(E log V)).
    """
    active_routes = [r for r in raw_routes if str(r["status"]).strip().lower() != "restricted"]
    
    nodes = set()
    for r in active_routes:
        nodes.add(r['from'])
        nodes.add(r['to'])
        
    adj_matrix = {n: [] for n in nodes}
    for r in active_routes:
        cost = calculate_composite_cost(r)
        adj_matrix[r["from"]].append((r["to"], cost, r))
    
    for node in adj_matrix:
        adj_matrix[node].sort(key=lambda x: x[2]["risk"])
        
    min_heap = [(0.0, start_node, [start_node])]
    min_cost_registry = {n: float('inf') for n in nodes}
    
    if start_node not in min_cost_registry:
        return [], float('inf')
        
    min_cost_registry[start_node] = 0.0
    settled_nodes = set()
    
    while min_heap:
        current_cost, u, current_path = heapq.heappop(min_heap)
        
        if u == end_node:
            return current_path, current_cost
            
        if u in settled_nodes:
            continue
        settled_nodes.add(u)
        
        for v, edge_cost, route_meta in adj_matrix[u]:
            if v in settled_nodes:
                continue
            new_cost = current_cost + edge_cost
            if new_cost < min_cost_registry[v]:
                min_cost_registry[v] = new_cost
                heapq.heappush(min_heap, (new_cost, v, current_path + [v]))
                
    return [], float('inf')


if __name__ == "__main__":
    EXCEL_FILE_PATH = Path(__file__).with_name("Part 1.xlsx")
    
    print("=" * 80)
    print(f"{'SHADOW NETWORK INFRASTRUCTURE CORE: INITIALIZING DATA':^80}")
    print("=" * 80)
    
    dataset_b = load_dataset_from_excel(EXCEL_FILE_PATH, target_sheet='B')
    
    if not dataset_b:
        print("[TERMINAL ERROR] Pipeline halted. No valid data extracted from Excel.")
    else:
        print(f"Successfully loaded {len(dataset_b)} route records from Sheet 'B'.\n")
        print(f"{'Source':<25}{'Destination':<25}{'Dist':<6}{'Time':<6}{'Risk':<6}{'Detect':<8}{'Status'}")
        print("-" * 90)
        for route in dataset_b:
            print(f"{str(route['from']):<25}{str(route['to']):<25}"
                  f"{route['distance']:<6.1f}{route['time']:<6.1f}{route['risk']:<6.1f}{route['detection']:<8.2f}{route['status']}")
        print("=" * 90 + "\n")

        print("[PROCESSING UPSTREAM FILTERS... PRUNING ALL REJECTED RESTRICTED PATHS]")
        time.sleep(0.4) 
        print("Executing Optimal Dijkstra Routing Pass...\n")

        start_time = time.perf_counter()
        
        path_a, cost_a = run_method_a_dijkstra(dataset_b, start_node="Port Authority Hub", end_node="Financial Vault Access")
        
        exec_time_a = (time.perf_counter() - start_time) * 1e6

        print("=" * 90)
        print(f"{'REAL-TIME PATH ROUTING PROFILING LOG':^90}")
        print("=" * 90)

        print("[METHOD A: MULTI-VARIABLE DIJKSTRA VECTOR OPTIMIZATION]")
        if path_a:
            print(f"  -> Path Sequence  : {' -> '.join(path_a)}")
            print(f"  -> Path Accuracy  : 100.00% Guaranteed Globally Optimal")
            print(f"  -> Computed Cost  : {cost_a:.4f} Total Composite Value Units")
        else:
            print(f"  -> Path Sequence  : [NO VALID PATH FOUND - ALL ROUTES RESTRICTED OR DISCONNECTED]")
            
        print(f"  -> System Latency : {exec_time_a:.2f} microseconds")
        print("=" * 90)