import pandas as pd
import sys
import os
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
                print(f"Found team: {current_team}")
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
        
        print(f"Conversion completed!")
        print(f"Total players extracted: {len(players_df)}")
        print(f"Teams present: {players_df['Team'].nunique()}")
        print(f"CSV file saved to: {output_csv_path}")
        
        print("\nPreview of first 5 players:")
        print(players_df.head())
        
        try:
            send2trash(excel_file_path)
            print(f"Excel file moved to trash: {excel_file_path}")
        except Exception as e:
            print(f"Unable to move Excel file to trash: {str(e)}")
        
        return str(output_csv_path)
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None

def main():

    if len(sys.argv) < 2:
        print("Usage: python converter.py <excel_file.xlsx> [output.csv]")
        print("Example: python converter.py giornata1.xlsx")
        return
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(excel_file):
        print(f"Error: File {excel_file} does not exist.")
        return
    
    result = excel_to_csv_players_only(excel_file, output_file)
    
    if result:
        print(f"\n Conversion completed successfully!")
        print(f"CSV file available: {result}")
    else:
        print("\n Conversion failed.")

if __name__ == "__main__":
    main()