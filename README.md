# Production Delay Tracker

A production delay tracking system powered by AI-driven department classification and advanced analytics. This application streamlines operational efficiency and provides intelligent insights into production bottlenecks.

## Features

- Track production delays with detailed information
- AI-driven automatic department classification
- Visualize delay data with responsive charts
- Ability to contest misclassified delays
- Export data to CSV for further analysis
- Responsive design works on desktop and mobile devices
- Progressive Web App (PWA) capabilities for offline use

## Technologies Used

- Flask web framework
- SQLAlchemy for database management
- Mistral AI for intelligent department classification
- Pandas for data processing and enhanced CSV export
- Gunicorn web server
- Chart.js for data visualization
- Bootstrap for responsive UI

## Setup and Installation

1. Clone the repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Requirements

- Python 3.9+
- See requirements.txt for Python package dependencies

## Usage

1. Navigate to the application in your web browser
2. Submit delay information through the form
3. View delays organized by department
4. Contest delays if they're classified incorrectly
5. Export data for further analysis

## License

[MIT](https://choosealicense.com/licenses/mit/)