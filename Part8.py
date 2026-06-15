import csv
import time


def compute_lps_array(pattern):
    """Precomputes the Longest Proper Prefix which is also Suffix (LPS) array."""
    m = len(pattern)
    lps = [0] * m
    length = 0  # length of the previous longest prefix suffix
    i = 1
   
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text, pattern):
    """Performs a linear-time string search using the KMP algorithm."""
    # Standardize to lowercase for resilient case-insensitive matching
    text = text.lower()
    pattern = pattern.lower()
   
    n = len(text)
    m = len(pattern)
   
    if m == 0:
        return True
       
    lps = compute_lps_array(pattern)
    i = 0  # index for text
    j = 0  # index for pattern
   
    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1
       
        if j == m:
            return True  # Pattern discovered in text string
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
               
    return False


def process_covert_stream(csv_filename):
    """Loads Dataset A via CSV and searches for the operational trigger phrases."""
    # Targeted operational target trigger keywords
    target_phrases = ["silent code", "shadow key", "final protocol", "launch trigger"]
   
    print("=" * 70)
    print("         CRITICAL SIGNAL INTERCEPTION LAB - DATASET A PARSING")
    print("=" * 70)
    print(f"[SYSTEM] Establishing handle on source file: {csv_filename}...")
   
    # Track metrics for validation output
    matched_records = []
   
    start_time = time.perf_counter()
   
    try:
        with open(csv_filename, mode='r', encoding='utf-8') as csv_file:
            # Flexible dialect sniffer to handle commas/semicolons seamlessly
            sample = csv_file.read(2048)
            dialect = csv.Sniffer().sniff(sample) if sample else 'excel'
            csv_file.seek(0)
           
            reader = csv.DictReader(csv_file, dialect=dialect)
           
            # Dynamic header standardization to account for variable naming conventions
            headers = reader.fieldnames
            msg_id_col = next((h for h in headers if 'id' in h.lower()), 'Message_ID')
            text_col = next((h for h in headers if 'text' in h.lower() or 'stream' in h.lower()), 'Text_Stream')
            route_col = next((h for h in headers if 'route' in h.lower() or 'tag' in h.lower()), 'Route_Tag')
           
            print(f"[CONFIG] Identified target columns: [{msg_id_col}] | [{text_col}] | [{route_col}]")
            print("-" * 70)
           
            for row in reader:
                msg_id = row.get(msg_id_col, "Unknown")
                text_stream = row.get(text_col, "")
                route_tag = row.get(route_col, "NULL")
               
                # Check how many distinct tactical phrases are present in this specific row
                found_phrases = [phrase for phrase in target_phrases if kmp_search(text_stream, phrase)]
               
                if found_phrases:
                    matched_records.append({
                        "id": msg_id,
                        "text": text_stream,
                        "tag": route_tag if route_tag and route_tag.strip().upper() != "NULL" else "NULL",
                        "matches": found_phrases
                    })
                   
    except FileNotFoundError:
        print(f"[FATAL] Target stream matrix '{csv_filename}' not found. Verify the file path.")
        return
       
    end_time = time.perf_counter()
    execution_time_us = (end_time - start_time) * 1_000_000
   
    # Display the final execution summary
    print("\n" + "=" * 70)
    print("                        RUNTIME METRICS SUMMARY")
    print("=" * 70)
    print(f"Algorithm Applied : Method A: Knuth-Morris-Pratt (Deterministic Automaton)")
    print(f"Processing Speed  : {execution_time_us:.2f} microseconds")
    print(f"Total Matches Found: {len(matched_records)}")
    print("-" * 70)
   
    for record in matched_records:
        print(f"  -> [MATCH DETECTED] Message ID: {record['id']}")
        print(f"     Stream Fragment   : \"{record['text']}\"")
        print(f"     Identified Flags  : {record['matches']}")
        print(f"     Extracted Route   : \033[92m{record['tag']}\033[0m")
        print("-" * 70)


if __name__ == "__main__":
    # Point this to your localized Dataset A csv filename
    process_covert_stream("dataset_a.csv")
