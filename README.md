# Automated Document Scanner and Perspective Rectifier

## Description
Computer vision pipeline that detects document boundaries in unconstrained photographic inputs, applies four-point perspective transformation, and produces high-contrast digitized scans.

## Live Demo
Access the live demonstration and portfolio showcase at: [https://sohail.devsil.com/projects.html](https://sohail.devsil.com/projects.html)

## Tech Stack
- Python 3.10+
- OpenCV
- NumPy
- Imutils

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git version control

### Installation and Setup
1. Clone the repository:
```bash
git clone https://github.com/sohailahmed-bsrh/document-scanner-project.git
cd document-scanner-project
```

2. Configure environment and dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/scan.py --image input.jpg
```

## Architecture and Project Structure
The repository is structured according to modular engineering standards:

```text
document-scanner-project/
|-- src/
|-- data/
|-- .gitignore
|-- README.md
`-- requirements.txt
```

## Interface and Verification
The system produces verifiable execution logs, data summaries, or interactive interfaces depending on the execution target. Validate operation by running the test suite or local entrypoint.

## Author
Developed by Sohail Ahmed ([Portfolio](https://sohail.devsil.com) | [GitHub](https://github.com/sohailahmed-bsrh)).
