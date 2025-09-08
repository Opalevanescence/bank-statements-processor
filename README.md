# Bank Statements Processor

This repository is used to categorize bank transactions.

_Original Purpose_

This repository is still in progress. The first iteration of the repository was intended to be used with `python categorize_transactions.py <csv_in> [-o <csv_out>]`.
With the input CSV needing to contain at least these columns: Date, Description, Withdrawal, Deposit.

Currently working on improving the repository to have a use REST endpoints, have a db, etc.


## Setup

```
brew install uv

# Create an environment
uv venv

# tell uv to treat current directory as a project with pyproject.toml as source of dependencies
# Note - i'm dubious this does what it says above
uv pip install --editable . 

# Add new dependencies to the project.toml file
# Dev flag will only add dependency to the dev list
uv add --dev <dependency>

# run using script
uv dev
```
