# Contributing to Rakshak Protocol

We welcome contributions from the community to improve public safety technology!

## Development Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/transparentgov/rakshak-protocol.git
   cd rakshak-protocol
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the test suite:
   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```
4. Run the end-to-end simulation:
   ```bash
   python simulations/run_scenario.py
   ```

## Pull Request Guidelines
- Ensure all tests pass before submitting.
- Include unit tests for any new edge biometric or acoustic filters.
- Maintain tamper-evident hash chaining in the Evidence Vault.
