import os
import pandas as pd


class ExcelRouteOptimizer:

    def __init__(self, excel_file, sheet_name="B"):
        self.routes = []

        df = pd.read_excel(
            excel_file, sheet_name=sheet_name, header=None, engine="openpyxl"
        )

        df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)

        data_rows = df.iloc[1:]

        for _, row in data_rows.iterrows():
            row_values = row.tolist()

            r_id = str(row_values[0]).strip()
            if not r_id or not r_id.startswith("R"):
                continue

            route = {
                "Route_ID": r_id,
                "Route_Name": str(row_values[1]).strip(),
                "Travel_Time": float(row_values[2]),
                "Patrol_Probability": float(row_values[3]),
                "Sensor_Failure": float(row_values[4]),
                "Collapse_Probability": float(row_values[5]),
                "Success_Reward": float(row_values[6]),
            }
            self.routes.append(route)

    def execute_expected_value_analysis(self):
        optimal_route = None
        max_expected_utility = -float("inf")
        complete_log = []

        for r in self.routes:
            p_survival = (
                (1.0 - r["Patrol_Probability"])
                * (1.0 - r["Sensor_Failure"])
                * (1.0 - r["Collapse_Probability"])
            )

            expected_utility = (
                p_survival * r["Success_Reward"]
            ) - r["Travel_Time"]

            metric_entry = {
                "id": r["Route_ID"],
                "name": r["Route_Name"],
                "p_survival": round(p_survival, 4),
                "expected_utility": round(expected_utility, 4),
                "travel_time": r["Travel_Time"],
            }
            complete_log.append(metric_entry)

            if expected_utility > max_expected_utility:
                max_expected_utility = expected_utility
                optimal_route = metric_entry

        return optimal_route, complete_log


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    excel_filename = os.path.join(script_dir, "Part 4.xlsx")
    target_sheet = "B"

    try:
        optimizer = ExcelRouteOptimizer(excel_filename, sheet_name=target_sheet)
        best_route, logs = optimizer.execute_expected_value_analysis()

        print("========================================================================")
        print("⚡ EXECUTION MONITOR: METHOD A EXPECTED VALUE ANALYSER INITIALIZED")
        print("========================================================================")
        print(f"[STATUS] Processing Assigned Dataset {target_sheet} ({len(logs)} Alternate Paths Ingested)\n")
        
        print("--- COMPREHENSIVE STRATEGIC EVALUATION LOG ---")
        
        for log in logs:
            is_max = "  <-- MAXIMA" if log["id"] == best_route["id"] else ""
            display_id = log["id"].replace("R", target_sheet)
            
            print(f"[LOG] Route {display_id:<2} | "
                  f"Survival Rate: {log['p_survival']:.4f} | "
                  f"Time Cost: {log['travel_time']:>5.1f} | "
                  f"Net Expected Utility: {log['expected_utility']:>9.4f}{is_max}")
            
        print("\n------------------------------------------------------------------------")
        print("🥇 OPTIMAL TACTICAL PATH SELECTION DETECTED")
        print("------------------------------------------------------------------------")
        
        best_display_id = best_route["id"].replace("R", target_sheet)
        print(f"Selected Target      : Route {best_display_id} ({best_route['name']})")
        print(f"Mathematical Utility : {best_route['expected_utility']:.4f} Decision Units")
        print("Execution Status     : SUCCESS (Corridor cleared for secure infiltration)")
        print("========================================================================")

    except FileNotFoundError:
        print(f"Error: Excel file not found at {excel_filename}")
    except ValueError:
        print(f"Error: Target sheet '{target_sheet}' not found")