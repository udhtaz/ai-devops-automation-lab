from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

class Reporter:
    """
    Writes a list of file‐metadata dicts to disk and optionally prints a preview.
    Supports CSV and JSON output based on the output_path suffix.
    """

    def __init__(
        self,
        output_path: Path,
        index: bool = False,
        print_preview: bool = True
    ):
        """
        :param output_path: Path to write the report to. Uses suffix to choose format.
        :param index: Whether to include the DataFrame index in output.
        :param print_preview: If True, prints the DataFrame to stdout after saving.
        """
        self.output_path = output_path
        self.index = index
        self.print_preview = print_preview
        self.df: pd.DataFrame = pd.DataFrame()

    def save(self, metas: List[Dict[str, Any]]) -> None:
        """
        Convert metas (list of dicts) into a DataFrame and save to disk.
        """
        # Build DataFrame
        self.df = pd.DataFrame(metas)

        # Choose writer by suffix
        suffix = self.output_path.suffix.lower()
        if suffix == ".csv":
            self.df.to_csv(self.output_path, index=self.index)
        elif suffix == ".json":
            # orient=records for list-of-dicts style JSON
            self.df.to_json(self.output_path, orient="records", indent=2)
        else:
            # Fallback: write CSV with .csv extension
            csv_path = self.output_path.with_suffix(".csv")
            self.df.to_csv(csv_path, index=self.index)
            print(f"[Reporter] Unknown suffix '{suffix}', saved as CSV to {csv_path}")
            self.output_path = csv_path

        if self.print_preview:
            self.print_report()

    def print_report(self) -> None:
        """
        Print a table preview of the DataFrame to stdout.
        """
        if self.df.empty:
            print("[Reporter] No data to preview. Did you call save()?")
        else:
            print("\n[Reporter] Report Preview:")
            print(self.df.to_string(index=self.index))

    def get_dataframe(self) -> pd.DataFrame:
        """
        Return the underlying DataFrame (after save()).
        """
        return self.df