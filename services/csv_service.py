
import pandas as pd
from .validators import validate_filename
from .schemas import success_response
from .exceptions import ValidationError


def summarize_csv(filename: str):
    file_path = validate_filename(filename)

    df = pd.read_csv(file_path)

    summary = {
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict()
    }

    return success_response(summary)


def filter_csv(filename: str, column: str, value):
    file_path = validate_filename(filename)

    df = pd.read_csv(file_path)

    if column not in df.columns:
        raise ValidationError(f"Column '{column}' not found")

    filtered = df[df[column] == value]

    preview = filtered.head(5).to_dict(orient="records")

    return success_response({
        "rows_found": len(filtered),
        "preview": preview
    })

