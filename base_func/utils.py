from datetime import datetime, date


DATE_FORMATS = (
    '%d.%m.%Y',
    '%Y.%m.%d',
    '%m.%d.%Y',
    '%d-%m-%Y',
    '%Y-%m-%d',
    '%m-%d-%Y',
    '%d/%m/%Y',
    '%Y/%m/%d',
    '%m/%d/%Y',
)


def convert_to_date(date_str: str) -> datetime.date:
    """Convert sting to date from different formats."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return date(1970, 1, 1)
