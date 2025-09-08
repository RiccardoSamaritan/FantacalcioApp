"""
Data Processor for Fantacalcio Matchday Excel files.

This module provides functionality to convert Fantacalcio Excel files to CSV format
and extract player data for use in the simulator.
"""

import pandas as pd
import re
import logging
from pathlib import Path
from typing import Optional, List, Dict, Union
from send2trash import send2trash


class DataProcessorError(Exception):
    """Base exception for data processor errors."""
    pass


class FileProcessingError(DataProcessorError):
    """Raised when file processing fails."""
    pass


class FantacalcioDataProcessor:
    """
    A class to process Fantacalcio Excel files and convert them to CSV format.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize the data processor.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    def excel_to_csv(self, excel_file_path: Union[str, Path], 
                     output_csv_path: Optional[Union[str, Path]] = None,
                     delete_excel: bool = False) -> str:
        """
        Convert an Excel file from Fantacalcio.it to a CSV file containing only player data.
        
        Args:
            excel_file_path: Path to the input Excel file
            output_csv_path: Path to the output CSV file (optional)
            delete_excel: Whether to delete the original Excel file after conversion
            
        Returns:
            Path to the output CSV file
            
        Raises:
            FileProcessingError: If the file cannot be processed
        """
        excel_path = Path(excel_file_path)
        
        if not excel_path.exists():
            raise FileProcessingError(f"Excel file not found: {excel_file_path}")
        
        if not excel_path.suffix.lower() in ['.xlsx', '.xls']:
            raise FileProcessingError(f"Invalid file format. Expected Excel file, got: {excel_path.suffix}")
        
        try:
            self.logger.info(f"Processing Excel file: {excel_path.name}")
            df = pd.read_excel(excel_path, sheet_name=0, header=None)
            
            players_data = self._extract_player_data(df)
            
            if not players_data:
                raise FileProcessingError("No player data found in the Excel file")
            
            players_df = pd.DataFrame(players_data)
            
            if output_csv_path is None:
                matchday_num = self.extract_matchday_number(excel_path.name)
                if matchday_num:
                    output_csv_path = excel_path.parent / f"matchday{matchday_num}.csv"
                else:
                    output_csv_path = excel_path.with_suffix('.csv')
            else:
                output_csv_path = Path(output_csv_path)

            players_df.to_csv(output_csv_path, index=False, encoding='utf-8')
            self.logger.info(f"CSV file created: {output_csv_path.name}")
            self.logger.info(f"Processed {len(players_data)} player records")
            
            if delete_excel:
                try:
                    send2trash(str(excel_path))
                    self.logger.info(f"Original Excel file moved to trash: {excel_path.name}")
                except Exception as e:
                    self.logger.warning(f"Could not delete Excel file: {e}")
            
            return str(output_csv_path)
            
        except Exception as e:
            self.logger.error(f"Error processing Excel file: {str(e)}")
            raise FileProcessingError(f"Failed to process Excel file: {str(e)}")
    
    def _extract_player_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Extract player data from the Excel DataFrame.
        
        Args:
            df: Pandas DataFrame from the Excel file
            
        Returns:
            List of player record dictionaries
        """
        players_data = []
        current_team = None
        
        for index, row in df.iterrows():
            row_data = [cell if pd.notna(cell) else None for cell in row.tolist()]
            
            if all(cell is None or cell == '' for cell in row_data):
                continue
            
            if self._is_header_or_footer_row(row_data):
                continue
            
            if self._is_column_header_row(row_data):
                continue
            
            if self._is_team_name_row(row_data):
                current_team = row_data[0]
                self.logger.debug(f"Found team: {current_team}")
                continue
            
            if self._is_player_data_row(row_data):
                player_record = self._create_player_record(row_data, current_team)
                if player_record:
                    players_data.append(player_record)
        
        return players_data
    
    def _is_header_or_footer_row(self, row_data: List) -> bool:
        """Check if row contains header or footer information."""
        if not row_data or not row_data[0]:
            return False
        
        text = str(row_data[0])
        keywords = [
            'Voti Fantacalcio', 'www.fantacalcio.it', 
            'QUESTO FILE', 'USO PERSONALE'
        ]
        return any(keyword in text for keyword in keywords)
    
    def _is_column_header_row(self, row_data: List) -> bool:
        """Check if row contains column headers."""
        return (len(row_data) >= 3 and 
                row_data[0] == 'Cod.' and 
                row_data[1] == 'Ruolo' and 
                row_data[2] == 'Nome')
    
    def _is_team_name_row(self, row_data: List) -> bool:
        """Check if row contains a team name."""
        return (len(row_data) >= 1 and 
                row_data[0] and 
                all(cell is None or cell == '' for cell in row_data[1:]) and
                not self._is_header_or_footer_row(row_data))
    
    def _is_player_data_row(self, row_data: List) -> bool:
        """Check if row contains player data."""
        return (len(row_data) >= 4 and 
                row_data[0] is not None and 
                isinstance(row_data[0], (int, float)) and 
                row_data[1] is not None and 
                isinstance(row_data[1], str) and 
                row_data[1] != "ALL" and  # Exclude coaches
                row_data[2] is not None and 
                isinstance(row_data[2], str))
    
    def _create_player_record(self, row_data: List, team: str) -> Optional[Dict]:
        """Create a player record dictionary from row data."""
        try:
            return {
                'Team': team,
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
        except (ValueError, IndexError) as e:
            self.logger.warning(f"Could not create player record from row: {e}")
            return None
    
    def extract_matchday_number(self, filename: str) -> Optional[int]:
        """
        Extract matchday number from filename.
        
        Supports patterns like:
        - Voti_Fantacalcio_Stagione_2024_25_Giornata_1.xlsx
        - giornata1.xlsx
        - matchday1.xlsx
        - Any filename containing 'Giornata_N' or 'giornata' followed by number
        
        Args:
            filename: The filename to extract matchday from
            
        Returns:
            Matchday number or None if not found
        """
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
    
    def batch_process_excel_files(self, input_directory: Union[str, Path], 
                                 output_directory: Optional[Union[str, Path]] = None,
                                 delete_excel: bool = False) -> List[str]:
        """
        Process multiple Excel files in a directory and standardize player lists.
        
        Args:
            input_directory: Directory containing Excel files
            output_directory: Directory for output CSV files (optional)
            delete_excel: Whether to delete original Excel files
            
        Returns:
            List of paths to created CSV files
        """
        input_path = Path(input_directory)
        if not input_path.exists() or not input_path.is_dir():
            raise FileProcessingError(f"Input directory not found: {input_directory}")
        
        if output_directory:
            output_path = Path(output_directory)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path
        
        excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
        
        if not excel_files:
            self.logger.warning(f"No Excel files found in {input_directory}")
            return []
        
        self.logger.info(f"Found {len(excel_files)} Excel files to process")
        
        processed_files = []
        errors = []
        
        temp_csv_files = []
        for excel_file in excel_files:
            try:
                matchday_num = self.extract_matchday_number(excel_file.name)
                if matchday_num:
                    output_file = output_path / f"matchday{matchday_num}.csv"
                else:
                    output_file = output_path / excel_file.with_suffix('.csv').name
                
                csv_path = self.excel_to_csv(excel_file, output_file, delete_excel)
                temp_csv_files.append(csv_path)
                
            except Exception as e:
                error_msg = f"Failed to process {excel_file.name}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        # Second pass: standardize player lists across all matchdays
        if temp_csv_files:
            try:
                self.logger.info("Standardizing player lists across all matchdays...")
                standardized_files = self.standardize_player_lists(temp_csv_files)
                processed_files = standardized_files
                self.logger.info("Player list standardization completed")
            except Exception as e:
                self.logger.error(f"Failed to standardize player lists: {str(e)}")
                processed_files = temp_csv_files
        else:
            processed_files = temp_csv_files
        
        self.logger.info(f"Successfully processed {len(processed_files)}/{len(excel_files)} files")
        
        if errors:
            self.logger.warning(f"Encountered {len(errors)} errors during batch processing")
            for error in errors:
                self.logger.warning(f"  - {error}")
        
        return processed_files
    
    def standardize_player_lists(self, csv_files: List[str]) -> List[str]:
        """
        Standardize player lists across all matchday CSV files.
        
        Ensures that all players who appear in any matchday are present in all matchdays,
        with zero values for ratings and bonuses when they don't actually play.
        
        Args:
            csv_files: List of CSV file paths to standardize
            
        Returns:
            List of paths to standardized CSV files
        """
        if not csv_files:
            return []
        
        self.logger.info(f"Collecting unique players from {len(csv_files)} CSV files...")
        
        # Step 1: Collect all unique players across all matchdays
        all_players = {}  # key: (Team, Cod, Role, Name), value: player record template
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                for _, row in df.iterrows():
                    player_key = (row['Team'], row['Cod'], row['Role'], row['Name'])
                    if player_key not in all_players:
                        # Store player info without ratings/bonuses for template
                        all_players[player_key] = {
                            'Team': row['Team'],
                            'Cod': row['Cod'],
                            'Role': row['Role'],
                            'Name': row['Name']
                        }
            except Exception as e:
                self.logger.error(f"Error reading {csv_file} for player collection: {str(e)}")
                continue
        
        self.logger.info(f"Found {len(all_players)} unique players across all matchdays")
        
        # Step 2: Standardize each CSV file
        standardized_files = []
        
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file)
                existing_players = set()
                
                # Track which players are already in this matchday
                for _, row in df.iterrows():
                    player_key = (row['Team'], row['Cod'], row['Role'], row['Name'])
                    existing_players.add(player_key)
                
                # Add missing players with zero values
                missing_players = []
                for player_key, player_template in all_players.items():
                    if player_key not in existing_players:
                        missing_record = player_template.copy()
                        # Set all numeric fields to 0
                        missing_record.update({
                            'Rating': 0,
                            'Gf': 0,
                            'Gs': 0,
                            'Rp': 0,
                            'Rs': 0,
                            'Rf': 0,
                            'Au': 0,
                            'Amm': 0,
                            'Esp': 0,
                            'Ass': 0
                        })
                        missing_players.append(missing_record)
                
                if missing_players:
                    self.logger.debug(f"Adding {len(missing_players)} missing players to {Path(csv_file).name}")
                    missing_df = pd.DataFrame(missing_players)
                    df = pd.concat([df, missing_df], ignore_index=True)
                
                # Sort by Team, then Role, then Name for consistency
                df = df.sort_values(['Team', 'Role', 'Name'])
                
                # Save the standardized file
                df.to_csv(csv_file, index=False, encoding='utf-8')
                standardized_files.append(csv_file)
                
            except Exception as e:
                self.logger.error(f"Error standardizing {csv_file}: {str(e)}")
                standardized_files.append(csv_file)  # Include even if standardization failed
        
        return standardized_files
    
    def validate_csv_data(self, csv_file_path: Union[str, Path]) -> Dict:
        """
        Validate the structure and content of a processed CSV file.
        
        Args:
            csv_file_path: Path to the CSV file to validate
            
        Returns:
            Dictionary with validation results
        """
        csv_path = Path(csv_file_path)
        
        if not csv_path.exists():
            return {'valid': False, 'error': f'CSV file not found: {csv_file_path}'}
        
        try:
            df = pd.read_csv(csv_path)
            
            required_columns = ['Team', 'Cod', 'Role', 'Name', 'Rating']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    'valid': False, 
                    'error': f'Missing required columns: {missing_columns}'
                }
            
            # Basic data validation
            teams = df['Team'].nunique()
            players = len(df)
            roles = df['Role'].value_counts().to_dict()
            
            return {
                'valid': True,
                'teams': teams,
                'players': players,
                'roles': roles,
                'file_size': csv_path.stat().st_size
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'Error validating CSV: {str(e)}'}

def process_excel_file(excel_file_path: Union[str, Path], 
                      output_csv_path: Optional[Union[str, Path]] = None,
                      delete_excel: bool = False) -> str:
    """
    Quick function to process a single Excel file.
    
    Args:
        excel_file_path: Path to Excel file
        output_csv_path: Output CSV path (optional)
        delete_excel: Whether to delete original file
        
    Returns:
        Path to created CSV file
    """
    processor = FantacalcioDataProcessor()
    return processor.excel_to_csv(excel_file_path, output_csv_path, delete_excel)


def batch_process_directory(input_directory: Union[str, Path],
                          output_directory: Optional[Union[str, Path]] = None,
                          delete_excel: bool = False) -> List[str]:
    """
    Quick function to batch process Excel files in a directory.
    
    Args:
        input_directory: Directory with Excel files
        output_directory: Output directory (optional)
        delete_excel: Whether to delete original files
        
    Returns:
        List of created CSV file paths
    """
    processor = FantacalcioDataProcessor()
    return processor.batch_process_excel_files(input_directory, output_directory, delete_excel)

if __name__ == "__main__":

    # Example usage: process all Excel files in "data/2021-22" and delete originals
    batch_process_directory("data/2021-22", delete_excel=True)