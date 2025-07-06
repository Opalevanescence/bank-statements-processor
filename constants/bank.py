from enum import Enum

class SchwabColumns (Enum):
  """Column names of CSV file from Lloyds."""
  DATE = "Date"
  DESCRIPTION = "Description"
  WITHDRAWAL = "Withdrawal"
  DEPOSIT = "Deposit"

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

