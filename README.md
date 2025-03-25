# Salesgentic Agent

FastAPI-based ReAct agent that performs interactive chain-of-thought reasoning.

The Agent takes in existing sales data and learns from this, allowing it to make
predictive actions in regards to your sales actions.

Integrates with Hubspot as your main CRM source.

## Requirements

- Python 3.9 or higher
- Poetry (Python package manager)

## Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the Poetry environment:
```bash
poetry shell
```

## Development

To add new dependencies:
```bash
poetry add package-name
```

To update dependencies:
```bash
poetry update
```

To run the project:
```bash
poetry run python main.py
```

## Features

- Chain-of-thought reasoning for sales predictions
- Hubspot CRM integration
- FastAPI backend for quick response times
- Interactive learning from historical sales data

## Project Structure

```
salesgentic-agent/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core business logic
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── tests/            # Test files
├── pyproject.toml    # Poetry dependency management
└── README.md         # This file
```

## Configuration

The application can be configured using environment variables:

```bash
HUBSPOT_API_KEY=your_api_key
DEBUG=True/False
```

## Testing

Run tests using Poetry:

```bash
poetry run pytest
```
