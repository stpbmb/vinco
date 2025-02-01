# Vinco - Wine Production Management System

Vinco is a comprehensive web application designed to manage wine production processes, from vineyard management to final bottling. It provides tools for tracking harvests, managing suppliers, monitoring fermentation, and controlling inventory.

## Features

### Vineyard Management
- Track owned and supplied vineyards
- Record vineyard details (location, size, grape variety)
- Manage supplier relationships
- Monitor harvest history

### Harvest Management
- Record grape harvests
- Track juice yields
- Manage juice allocation to tanks
- Calculate remaining juice volumes

### Packaging Management
- Track bottling operations
- Manage inventory
- Record packaging details

## Technology Stack

- **Backend**: Django
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: PostgreSQL
- **Authentication**: Django Authentication System

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vinco.git
cd vinco
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
vinco/
├── vineyards/          # Vineyard management app
├── harvests/           # Harvest tracking app
├── packaging/          # Packaging management app
├── cellars/           # Cellar and tank management
├── static/            # Static files
│   ├── css/          # Stylesheets
│   └── js/           # JavaScript files
└── templates/         # Base templates
```

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use Django's coding style for templates
- Follow Bootstrap conventions for CSS

### Documentation
- Add docstrings to all models and views
- Comment complex logic
- Keep README up to date

### Testing
- Write tests for new features
- Run tests before committing
- Maintain test coverage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Your Name - Initial work

## Acknowledgments

- Thanks to all contributors
- Special thanks to the Django community
