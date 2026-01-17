## Quick Start

### Prerequisites

- Python 3.10 or higher

### Installation

1. **Navigate to the project**

   ```bash
   cd deal-pipeline/deals_processor
   ```

2. **Create virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

### Running the Application

**Using the entry point (recommended):**

```bash
# Activate the virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate
run-deals-processor
```

### User Details
The application comes with pre-defined users for testing:
| Username             | Password   | Role    |
|----------------------|------------|---------|
| admin@default.com    | admin123   | admin   |
| testuser@example.com | test123456 | analyst |
| user1@example.com    | user123456 | partner |