# Development Guide

This guide provides detailed information for developers working on the Vinco project.

## Development Environment Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Git

### Local Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/vinco.git
cd vinco
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

### Database Setup
1. Create a PostgreSQL database:
```sql
CREATE DATABASE vinco;
CREATE USER vinco_user WITH PASSWORD 'your_password';
ALTER ROLE vinco_user SET client_encoding TO 'utf8';
ALTER ROLE vinco_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE vinco_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE vinco TO vinco_user;
```

2. Configure database settings in `.env`:
```
DB_NAME=vinco
DB_USER=vinco_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Maximum line length: 100 characters
- Use docstrings for all classes and functions

Example:
```python
def calculate_juice_yield(quantity: float, efficiency: float) -> float:
    """
    Calculate juice yield based on grape quantity and press efficiency.

    Args:
        quantity: Grape quantity in kilograms
        efficiency: Press efficiency as decimal (0.0 to 1.0)

    Returns:
        float: Calculated juice yield in liters
    """
    return quantity * efficiency
```

### Django Templates
- Use 4 spaces for indentation
- Keep logic in templates minimal
- Use template inheritance effectively
- Name blocks descriptively

Example:
```html
{% extends 'base.html' %}

{% block content %}
    <div class="container">
        {% block page_content %}{% endblock %}
    </div>
{% endblock %}
```

### JavaScript
- Use ES6+ features
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable and function names
- Add comments for complex logic

Example:
```javascript
// Debounce search input to prevent excessive API calls
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};
```

## Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test vineyards.tests.test_models

# Run with coverage
coverage run manage.py test
coverage report
coverage html  # Generate HTML report
```

### Writing Tests
- Write tests for all new features
- Follow AAA pattern (Arrange, Act, Assert)
- Use meaningful test names
- Test edge cases and error conditions

Example:
```python
def test_harvest_remaining_juice_calculation(self):
    """Test that remaining juice is correctly calculated."""
    # Arrange
    harvest = Harvest.objects.create(
        vineyard=self.vineyard,
        date=timezone.now().date(),
        quantity=1000,
        juice_yield=700
    )
    HarvestAllocation.objects.create(
        harvest=harvest,
        tank=self.tank,
        allocated_volume=200
    )

    # Act
    remaining_juice = harvest.remaining_juice

    # Assert
    self.assertEqual(remaining_juice, 500)
```

## Git Workflow

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/description`
- Bugfix branches: `bugfix/description`
- Release branches: `release/version`

### Commit Messages
Follow the conventional commits specification:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- test: Adding or modifying tests
- chore: Maintenance tasks

Example:
```
feat(harvests): add juice allocation tracking

- Add HarvestAllocation model
- Implement remaining juice calculation
- Add allocation form and validation

Closes #123
```

## Deployment

### Staging Environment
1. Push to staging branch
2. Automated tests run
3. Deploy to staging server
4. Run migrations
5. Test functionality

### Production Environment
1. Create release branch
2. Update version numbers
3. Run full test suite
4. Deploy to production
5. Tag release

## Documentation

### Code Documentation
- Add docstrings to all classes and functions
- Document complex algorithms
- Update README.md with new features
- Keep API documentation current

### User Documentation
- Update user guide with new features
- Add screenshots for UI changes
- Document new workflows
- Update FAQ section

## Performance Considerations

### Database
- Use select_related() and prefetch_related()
- Create appropriate indexes
- Monitor query performance
- Use database constraints

### Caching
- Cache expensive calculations
- Use template fragment caching
- Configure Redis caching
- Monitor cache hit rates

### Frontend
- Minimize JavaScript bundle size
- Optimize image loading
- Use lazy loading
- Implement debouncing

## Security

### General Guidelines
- Keep dependencies updated
- Use HTTPS everywhere
- Implement rate limiting
- Follow security best practices

### Authentication
- Use strong password policies
- Implement 2FA
- Monitor failed login attempts
- Regular security audits

## Monitoring

### Error Tracking
- Configure error logging
- Set up alerts
- Monitor application health
- Track performance metrics

### Analytics
- Track user behavior
- Monitor system usage
- Collect performance data
- Generate reports
