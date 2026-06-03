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


def run_insertion_sort(dataset):
    arr = []
    start_time = time.perf_counter_ns()
    
    for item in dataset:
        arr.append(item)
        
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        
        while j >= 0 and (arr[j]['threat_priority'] > key['threat_priority'] or 
                         (arr[j]['threat_priority'] == key['threat_priority'] and arr[j]['timestamp'] > key['timestamp'])):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
            
    duration_ns = time.perf_counter_ns() - start_time
    mem_size = sys.getsizeof(arr)
    return duration_ns / 1e9, arr, mem_size


def timsort_insertion_slice(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and (arr[j]['threat_priority'] > key['threat_priority'] or 
                            (arr[j]['threat_priority'] == key['threat_priority'] and arr[j]['timestamp'] > key['timestamp'])):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


def merge_sort(arr, l, m, r):
    left_slice = arr[l:m + 1]
    right_slice = arr[m + 1:r + 1]
    
    peak_mem = sys.getsizeof(left_slice) + sys.getsizeof(right_slice)
    
    i = j = 0
    k = l
    
    while i < len(left_slice) and j < len(right_slice):
        if left_slice[i]['threat_priority'] < right_slice[j]['threat_priority']:
            arr[k] = left_slice[i]
            i += 1
        elif left_slice[i]['threat_priority'] == right_slice[j]['threat_priority'] and left_slice[i]['timestamp'] <= right_slice[j]['timestamp']:
            arr[k] = left_slice[i]
            i += 1
        else:
            arr[k] = right_slice[j]
            j += 1
        k += 1
        
    while i < len(left_slice):
        arr[k] = left_slice[i]
        i += 1
        k += 1
        
    while j < len(right_slice):
        arr[k] = right_slice[j]
        j += 1
        k += 1
        
    return peak_mem


def run_timsort(dataset, run_size=4):
    arr = list(dataset)
    n = len(arr)
    start_time = time.perf_counter_ns()
    max_merge_mem = 0
    
    for i in range(0, n, run_size):
        timsort_insertion_slice(arr, i, min((i + run_size - 1), (n - 1)))
        
    size = run_size
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            
            if mid < right:
                allocated = merge_sort(arr, left, mid, right)
                if allocated > max_merge_mem:
                    max_merge_mem = allocated
        size = 2 * size
        
    duration_ns = time.perf_counter_ns() - start_time
    total_space = sys.getsizeof(arr) + max_merge_mem
    return duration_ns / 1e9, arr, total_space


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
    t_ins, t_tim, t_hp, static_winners, shared_mem_ins, shared_mem_tim, shared_mem_hp = static_metrics
    t_dynamic_tim = 0.0  
    
    final_dyn_ins = 0.0
    final_dyn_tim = 0.0
    final_dyn_hp = 0.0
    
    d_mem_ins = 0
    d_mem_hp = 0
    final_dyn_winners = []
    
    live_stream_heap = []
    cumulative_heap_time = 0.0

    for idx, incoming_item in enumerate(dataset, 1):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        current_stream_chunk = dataset[:idx]
        t_dynamic_insertion, sorted_sim_arr, d_mem_ins = run_insertion_sort(current_stream_chunk)
        final_dyn_ins = t_dynamic_insertion

        if idx == len(dataset):
            t_dyn_tim_start = time.perf_counter_ns()
            _, _, _ = run_timsort(current_stream_chunk, run_size=4)
            t_dynamic_tim = (time.perf_counter_ns() - t_dyn_tim_start) / 1e9
            final_dyn_tim = t_dynamic_tim

        t_heap_step, active_top_k, d_mem_hp, live_stream_heap = run_bounded_heap(
            dataset=[incoming_item], 
            k=k, 
            existing_heap=live_stream_heap
        )
        cumulative_heap_time += t_heap_step
        final_dyn_hp = cumulative_heap_time
        final_dyn_winners = [x['event_id'] for x in active_top_k]

        print("=" * 85)
        print(" [SECTION 1: STATIC TIMING RESULTS]")
        print("=" * 85)
        print(f"  • Static Insertion Sort Time : {t_ins:.8f} seconds")
        print(f"  • Static Timsort Time        : {t_tim:.8f} seconds")
        print(f"  • Static Bounded Min-Heap    : {t_hp:.8f} seconds")
        print(f"  Verified Baseline Winners : {static_winners}\n")
        
        print("=" * 85)
        print(f" [SECTION 2: DYNAMIC LIVE STREAMING TIMERS - PACKET {idx} OF {len(dataset)}]")
        print("=" * 85)
        print(f"  Current Ingestion Target : ID: {incoming_item['event_id']} | Type: {incoming_item['event_type']} | Zone: {incoming_item['zone']}")
        print("-" * 85)
        print(f"Algorithm 1 (Dynamic Insertion Sort) : {t_dynamic_insertion:.8f}s | Allocation: {d_mem_ins} B")
        
        if idx < len(dataset):
            print(f"Algorithm 2 (Dynamic Timsort Engine) : HOLDING... (0.00000000s) | Allocation: 0 B")
        else:
            print(f"Algorithm 2 (Dynamic Timsort Engine) : ACTIVATED! ({t_dynamic_tim:.8f}s) | Allocation: {shared_mem_tim} B")
            
        print(f"Algorithm 3 (Dynamic Bounded Heap)   : {cumulative_heap_time:.8f}s| Allocation: {d_mem_hp} B")
        print("-" * 85)

        print(f"CURRENT ACTIVE MONITOR LIVE RANKINGS (TOP-{k})")
        print("-" * 85)
        print(f" {'RANK':<6} | {'INSERTION SORT':<30} | {'TIMSORT ENGINE':<30} | {'BOUNDED HEAP':<30}")
        print("-" * 85)
        active_insertion_top_k = sorted_sim_arr[:k]

        for rank in range(1, k + 1):
            if rank <= len(active_insertion_top_k):
                ins_item = active_insertion_top_k[rank - 1]
                ins_str = f"[{ins_item['event_id']}] P:{ins_item['threat_priority']} Z:{ins_item['zone']}"
            else:
                ins_str = "[EMPTY]"

            if idx < len(dataset):
                tim_str = "[LOCK / NO DATA UPFRONT]"
            else:
                _, final_tim_arr, _ = run_timsort(current_stream_chunk, run_size=4)
                tim_item = final_tim_arr[rank - 1] if rank <= len(final_tim_arr) else None
                tim_str = f"[{tim_item['event_id']}] P:{tim_item['threat_priority']} Z:{tim_item['zone']}" if tim_item else "[EMPTY]"

            if rank <= len(active_top_k):
                hp_item = active_top_k[rank - 1]
                hp_str = f"[{hp_item['event_id']}] P:{hp_item['threat_priority']} Z:{hp_item['zone']}"
            else:
                hp_str = "[EMPTY]"

            print(f" Rank {rank:<1} | {ins_str:<30} | {tim_str:<30} | {hp_str:<30}")
            
        print("=" * 110 + "\n")
        
        time.sleep(delay)

    print("\n" + "=" * 92)
    print("FINAL TIME & SPACE COMPLEXITY REPORT")
    print("=" * 92)
    print(f" {'ALGORITHM':<20} | {'STATIC/DYNAMIC MEMORY':<23} | {'STATIC BATCH TIME':<19} | {'DYNAMIC TOTAL TIME':<10}")
    print("-" * 92)
    print(f" 1. Insertion Sort   | {shared_mem_ins:<13} Bytes   | {t_ins:.8f}s {'':<10} | {final_dyn_ins:.8f}s")
    print(f" 2. Timsort Engine   | {shared_mem_tim:<13} Bytes   | {t_tim:.8f}s {'':<10} | {final_dyn_tim:.8f}s")
    print(f" 3. Bounded Min-Heap | {shared_mem_hp:<13} Bytes   | {t_hp:.8f}s {'':<10} | {final_dyn_hp:.8f}s")
    print("-" * 92)
    print(f"Final Winners  : {static_winners}")
    print("=" * 92 + "\n")


if __name__ == "__main__":
    DATASET_PATH = "/Users/siew/Desktop/WIA2005-ALGORITHM-DESIGN-AND-ANALYSIS/Part 6.xlsx"
    TARGET_K = 3
    
    try:
        user_stream = load_excel_dataset(DATASET_PATH)
    except Exception as e:
        print(f"Error loading Excel data structure: {e}")
        exit()

    t_insert, sorted_insert, space_ins = run_insertion_sort(user_stream)
    static_id_winners = [x['event_id'] for x in sorted_insert[:TARGET_K]]
    
    t_tim, _, space_tim = run_timsort(user_stream, run_size=4)
    t_heap, _, space_hp, _ = run_bounded_heap(user_stream, k=TARGET_K)
    
    metric_bundle = (t_insert, t_tim, t_heap, static_id_winners, space_ins, space_tim, space_hp)
    
    render_vertical_dashboard(user_stream, metric_bundle, k=TARGET_K, delay=0.5)