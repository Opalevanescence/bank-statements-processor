from enum import Enum

class Bank (Enum):
  """Banks we can process CSVs for."""
  LLOYDS = 'lloyds'
  SCHWAB = 'schwab'

class SchwabColumns (Enum):
  """Column names of CSV file from Lloyds."""
  DATE = "date"
  DESCRIPTION = "description"
  WITHDRAWAL = "withdrawal"
  DEPOSIT = "deposit"

class LloydsColumns (Enum):
  """Column names of CSV file from Lloyds."""
  DATE = "Transaction Date"
  DESCRIPTION = "Transaction Description"
  WITHDRAWAL = "Debit Amount"
  DEPOSIT = "Credit Amount"

class Currency (Enum):
  """Currency types."""
  USD = "USD"
  GBP = "GBP"
  EUR = "EUR"

