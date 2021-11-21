"""Tools for working with dates."""

from datetime import datetime

DATE_FORMATS = (
    '%d.%m.%Y',
    '%d.%m.%y',
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
    raise ValueError(f'String: {date_str} contains wrong date format')
