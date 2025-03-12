# PRISM - Production Root Issue Sorting Mechanism

PRISM is a Progressive Web App (PWA) designed to streamline the tracking and categorization of production issues using AI-driven classification. This tool helps manufacturing teams identify and address production bottlenecks by intelligently categorizing reported issues.

## Features

- **AI-Powered Classification**: Automatically assigns issues to the most likely department using Mistral AI
- **Intuitive Interface**: Clean and responsive UI for issue submission and tracking
- **Visualization**: Real-time charts showing impact of issues by department
- **Contest Mechanism**: Ability to contest AI classifications with reasoning
- **Data Export**: Export collected data to CSV for further analysis
- **PWA Support**: Install as a standalone application on mobile and desktop devices
- **Offline Capability**: Continue working even when network connection is lost

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Python
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **AI Model**: Mistral AI for department classification
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Data Processing**: Pandas for advanced CSV export

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/BreezBlox/PRISM-lite.git
   cd PRISM-lite
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. **Submit an Issue**: Fill out the form with job number, part number, date, and description
2. **Review Classifications**: Check the department tables to see how AI has sorted the issues
3. **Contest if Needed**: If you disagree with the classification, use the contest button
4. **Export Data**: Use the CSV export button for detailed records

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Mistral AI for providing the classification model
- Chart.js for the visualization library
- Bootstrap for the responsive framework