import pandas as pd
import sys
import os
import re
from pathlib import Path
from send2trash import send2trash


def excel_to_csv_players_only(excel_file_path, output_csv_path=None):
    """
    Convert an Excel file taken from Fantacalcio.it to a CSV file containing only player data
    of the specified matchday.
    :param excel_file_path: Path to the input Excel file
    :param output_csv_path: Path to the output CSV file (optional)
    :return: Path to the output CSV file if successful, None otherwise
    """
    try:
        df = pd.read_excel(excel_file_path, sheet_name=0, header=None)
        
        players_data = []
        current_team = None
        
        for index, row in df.iterrows():
        
            row_data = [cell if pd.notna(cell) else None for cell in row.tolist()]
            
            if all(cell is None or cell == '' for cell in row_data):
                continue
            
            if (len(row_data) >= 1 and row_data[0] and 
                any(keyword in str(row_data[0]) for keyword in [
                    'Voti Fantacalcio', 'www.fantacalcio.it', 
                    'QUESTO FILE', 'USO PERSONALE'])):
                continue

            if (len(row_data) >= 3 and row_data[0] == 'Cod.' and 
                row_data[1] == 'Ruolo' and row_data[2] == 'Nome'):
                continue

            if (len(row_data) >= 1 and row_data[0] and 
                all(cell is None or cell == '' for cell in row_data[1:]) and
                not any(keyword in str(row_data[0]) for keyword in [
                    'Voti Fantacalcio', 'www.fantacalcio.it', 
                    'QUESTO FILE', 'USO PERSONALE'])):
                current_team = row_data[0]
                continue
            
            if (len(row_data) >= 4 and 
                row_data[0] is not None and 
                isinstance(row_data[0], (int, float)) and 
                row_data[1] is not None and 
                isinstance(row_data[1], str) and 
                row_data[1] != "ALL" and  # Exclude coaches
                row_data[2] is not None and 
                isinstance(row_data[2], str)):
                
                player_record = {
                    'Team': current_team,
                    'Cod': int(row_data[0]),
                    'Role': row_data[1],
                    'Name': row_data[2],
                    'Rating': row_data[3] if len(row_data) > 3 else None,
                    'Gf': row_data[4] if len(row_data) > 4 else None,
                    'Gs': row_data[5] if len(row_data) > 5 else None,
                    'Rp': row_data[6] if len(row_data) > 6 else None,
                    'Rs': row_data[7] if len(row_data) > 7 else None,
                    'Rf': row_data[8] if len(row_data) > 8 else None,
                    'Au': row_data[9] if len(row_data) > 9 else None,
                    'Amm': row_data[10] if len(row_data) > 10 else None,
                    'Esp': row_data[11] if len(row_data) > 11 else None,
                    'Ass': row_data[12] if len(row_data) > 12 else None
                }
                
                players_data.append(player_record)
        
        players_df = pd.DataFrame(players_data)
        
        if output_csv_path is None:
            excel_path = Path(excel_file_path)
            output_csv_path = excel_path.with_suffix('.csv')
        
        players_df.to_csv(output_csv_path, index=False, encoding='utf-8')
        

        send2trash(excel_file_path)
        
        return str(output_csv_path)
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None


def extract_matchday_number(filename):
    """
    Extract matchday number from filename.
    Supports patterns like:
    - Voti_Fantacalcio_Stagione_2024_25_Giornata_1.xlsx
    - giornata1.xlsx
    - matchday1.xlsx
    - Any filename containing 'Giornata_N' or 'giornata' followed by number
    """
    # Try different patterns
    patterns = [
        r'Giornata_(\d+)',  # Voti_Fantacalcio_Stagione_2024_25_Giornata_1.xlsx
        r'giornata(\d+)',   # giornata1.xlsx
        r'matchday(\d+)',   # matchday1.xlsx
        r'(\d+)'           # fallback: any number in filename
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return None


def main():
    
    excel_file = sys.argv[1]
    
    if not os.path.exists(excel_file):
        print(f"Error: File {excel_file} does not exist.")
        return
    
    matchday_number = extract_matchday_number(excel_file)
    
    output_file = f"matchday{matchday_number}.csv"

    excel_to_csv_players_only(excel_file, output_file)

if __name__ == "__main__":
    main()