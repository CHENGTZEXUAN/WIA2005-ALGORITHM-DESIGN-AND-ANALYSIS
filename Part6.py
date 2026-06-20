import pandas as pd
import time
import heapq
import os
import sys

def load_excel_dataset(file_path):
    operational_stream = []
    
    df = pd.read_excel(file_path, sheet_name='B')
    df = df.fillna('')
    
    for _, row in df.iterrows():
        col_event_id = str(row.iloc[1]).strip()       
        col_threat = str(row.iloc[2]).strip()         
        
        if 'Event_ID' in col_event_id or 'Threat' in col_threat:
            continue
        if col_event_id == '' or col_threat == '':
            continue
            
        try:
            threat_val = int(float(row.iloc[2]))       
            timestamp_val = str(row.iloc[3]).strip()   
            zone_val = str(row.iloc[4]).strip()        
            event_type_val = str(row.iloc[5]).strip()  
            code_val = int(float(row.iloc[6])) if str(row.iloc[6]).strip() != '' else 0 
            
            formatted_log = {
                'event_id': col_event_id,
                'threat_priority': threat_val, 
                'timestamp': timestamp_val,             
                'zone': zone_val,
                'event_type': event_type_val,
                'code_value': code_val
            }
            operational_stream.append(formatted_log)
            
        except Exception:
            continue
        
    return operational_stream


def run_bounded_heap(dataset, k=3, existing_heap=None):
    heap = existing_heap if existing_heap is not None else []
    start_time = time.perf_counter_ns()
    for item in dataset:
        entry = (-item['threat_priority'], item['timestamp'], item)
        if len(heap) < k:
            heapq.heappush(heap, entry)
        else:
            if entry > heap[0]:
                heapq.heappushpop(heap, entry)
    duration_ns = time.perf_counter_ns() - start_time
    mem_size = sys.getsizeof(heap)
    final_top_k = sorted([item[2] for item in heap], key=lambda x: (x['threat_priority'], x['timestamp']))
    return duration_ns / 1e9, final_top_k, mem_size, heap


def render_vertical_dashboard(dataset, static_metrics, k=3, delay=0.5):
    t_hp, static_winners, shared_mem_hp = static_metrics
    
    final_dyn_hp = 0.0
    d_mem_hp = 0
    final_dyn_winners = []
    
    live_stream_heap = []
    cumulative_heap_time = 0.0

    for idx, incoming_item in enumerate(dataset, 1):
        os.system('cls' if os.name == 'nt' else 'clear')

        t_heap_step, active_top_k, d_mem_hp, live_stream_heap = run_bounded_heap(
            dataset=[incoming_item], 
            k=k, 
            existing_heap=live_stream_heap
        )
        cumulative_heap_time += t_heap_step
        final_dyn_hp = cumulative_heap_time
        final_dyn_winners = [x['event_id'] for x in active_top_k]

        print("=" * 85)
        print(" [SECTION 1: STATIC TIMING RESULT]")
        print("=" * 85)
        print(f" Static Bounded Min-Heap    : {t_hp:.8f} seconds")
        print("=" * 85 + "\n")
        
        print("=" * 85)
        print(f" [SECTION 2: DYNAMIC LIVE STREAMING TIMER - PACKET {idx} OF {len(dataset)}]")
        print("=" * 85)
        print(f"  Current Ingestion Target : ID: {incoming_item['event_id']} | Type: {incoming_item['event_type']} | Zone: {incoming_item['zone']}")
        print("-" * 85)
        print(f"Dynamic Bounded Heap Efficiency      : {cumulative_heap_time:.8f}s | Allocation: {d_mem_hp} B")
        print("-" * 85)

        print(f"CURRENT ACTIVE MONITOR LIVE RANKINGS (TOP-{k})")
        print("-" * 85)
        for rank, match in enumerate(active_top_k, 1):
            print(f"  Rank {rank} -> ID: {match['event_id']} | Threat Priority: {match['threat_priority']} | Time: {match['timestamp']}")
            
        time.sleep(delay)


    print("\n" + "=" * 92)
    print("FINAL TIME & SPACE COMPLEXITY REPORT")
    print("=" * 92)
    print(f" {'ALGORITHM':<20} | {'STATIC/DYNAMIC MEMORY':<23} | {'STATIC BATCH TIME':<19} | {'DYNAMIC TOTAL TIME':<10}")
    print("-" * 92)
    print(f" Bounded Min-Heap      | {shared_mem_hp:<13} Bytes   | {t_hp:.8f}s {'':<10} | {final_dyn_hp:.8f}s")
    print("-" * 92)
    print(f"Final Winners (Batch): {static_winners}")
    print("=" * 92 + "\n")


if __name__ == "__main__":
    DATASET_PATH = "/Users/siew/Desktop/WIA2005-ALGORITHM-DESIGN-AND-ANALYSIS/Part 6.xlsx"
    TARGET_K = 3
    
    try:
        user_stream = load_excel_dataset(DATASET_PATH)
    except Exception as e:
        print(f"Error loading Excel data structure: {e}")
        exit()

    t_heap, static_top_k, space_hp, _ = run_bounded_heap(user_stream, k=TARGET_K)
    static_winners_list = [x['event_id'] for x in static_top_k]
    
    metric_bundle = (t_heap, static_winners_list, space_hp)
    
    render_vertical_dashboard(user_stream, metric_bundle, k=TARGET_K, delay=0.5)