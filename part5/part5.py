import csv
import os

def execute_segmented_merge_sort(file_path):
    if not os.path.exists(file_path):
        print(f"Error: Target file '{file_path}' not found in the current folder.")
        return
        
    with open(file_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        rows = list(reader)
        
    header_row_idx = -1
    for idx, row in enumerate(rows):
        if any("Segment_Group" in str(cell) for cell in row):
            header_row_idx = idx
            break
            
    if header_row_idx == -1:
        print("Error: Could not find 'Segment_Group' in file headers.")
        return

    headers = [str(cell).strip() for cell in rows[header_row_idx]]
    
    group_idx = -1
    seq_idx = -1
    status_idx = -1
    data_idx = -1
    id_idx = -1
    
    for i, h in enumerate(headers):
        if "Segment_Group" in h: group_idx = i
        elif "Sequence_No" in h: seq_idx = i
        elif "Integrity_Status" in h: status_idx = i
        elif "Data_Block" in h: data_idx = i
        elif "Fragment_ID" in h: id_idx = i

    print("\n" + "="*60)
    print("PHASE 1: DIVIDE & FILTER (BUCKETING PROCESS)")
    print("="*60)
    
    buckets = {}
    
    for row in rows[header_row_idx + 1:]:
        if not row or len(row) <= max(group_idx, seq_idx, status_idx, data_idx):
            continue
            
        group = row[group_idx].strip()
        status = row[status_idx].strip()
        seq_str = row[seq_idx].strip()
        data_block = row[data_idx].strip()
        frag_id = row[id_idx].strip() if id_idx != -1 else "Unknown"
        
        if not group:
            continue
            
        if status in ["Corrupted", "Missing"]:
            print(f"[-] Filtered Out: {frag_id} | Group: {group} | Seq: {seq_str} | Status: {status}")
            continue
            
        if group not in buckets:
            buckets[group] = []
            
        try:
            seq_no = int(seq_str)
            buckets[group].append({
                "Fragment_ID": frag_id,
                "Sequence_No": seq_no,
                "Data_Block": data_block
            })
            print(f"[+] Partitioned: {frag_id} -> Bucket: {group} | Sequence: {seq_no}")
        except ValueError:
            continue

    def merge_sort(arr):
        if len(arr) <= 1:
            return arr
        mid = len(arr) // 2
        left = merge_sort(arr[:mid])
        right = merge_sort(arr[mid:])
        return merge(left, right)

    def merge(left, right):
        sorted_arr = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i]["Sequence_No"] <= right[j]["Sequence_No"]:
                sorted_arr.append(left[i])
                i += 1
            else:
                sorted_arr.append(right[j])
                j += 1
        sorted_arr.extend(left[i:])
        sorted_arr.extend(right[j:])
        return sorted_arr

    print("\n" + "="*60)
    print("PHASE 2: CONQUER (STABLE RECURSIVE MERGE SORT)")
    print("="*60)
    
    sorted_buckets = {}
    ordered_groups = sorted(list(buckets.keys()))
    
    for group in ordered_groups:
        items = buckets[group]
        print(f"\nSorting Bucket Group: [{group}]")
        if not items:
            print("  (No valid fragments in this bucket)")
            sorted_buckets[group] = []
            continue
            
        unsorted_ids = [f"{x['Fragment_ID']}(Seq:{x['Sequence_No']})" for x in items]
        print(f"  Unsorted Stream Layout: {', '.join(unsorted_ids)}")
        
        sorted_buckets[group] = merge_sort(items)
        
        sorted_ids = [f"{x['Fragment_ID']}(Seq:{x['Sequence_No']})" for x in sorted_buckets[group]]
        print(f"  Sorted Sequence Layout: {', '.join(sorted_ids)}")

    print("\n" + "="*60)
    print("PHASE 3: COMBINE (CONCATENATING STREAMS)")
    print("="*60)
    
    final_reconstruction = []
    for group in ordered_groups:
        print(f"Extracting sorted fragments from [{group}]:")
        for item in sorted_buckets[group]:
            final_reconstruction.append(item["Data_Block"])
            print(f"  -> Appending Block: {item['Data_Block']} (Source: {item['Fragment_ID']})")
            
    final_signal = "".join(final_reconstruction)
    
    print("\n" + "="*60)
    print("RECONSTRUCTED CYPHER NEXUS CORE ACTIVATION KEY:")
    print("="*60)
    print(final_signal)
    print("="*60 + "\n")
    return final_signal

if __name__ == "__main__":
    possible_filenames = ["Part 5.csv", "Part 5.xlsx - C.csv", "Part 5.xlsx - B.csv", "Part 5.xlsx - A.csv"]
    target_file = ""
    for name in possible_filenames:
        if os.path.exists(name):
            target_file = name
            break
            
    if not target_file:
        target_file = "Part 5.csv"
        
    execute_segmented_merge_sort(target_file)