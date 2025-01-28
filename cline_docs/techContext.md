# Technical Context

## Technologies Used
1. Backend Framework
   - Django (Python web framework)
   - Django ORM for database operations
   - Django Forms for input handling

2. Database
   - Django's default database system
   - Relational database structure
   - Migration-based schema management

3. Frontend
   - Django Templates
   - HTML/CSS
   - Form-based interfaces

## Development Setup
1. Project Structure
   - Django project: 'vinco'
   - Main app: 'vineyards'
   - Templates in vineyards/templates/
   - Static files (if any) in vineyards/static/

2. Key Files
   - models.py: Data models and business logic
   - views.py: Request handling and processing
   - urls.py: URL routing
   - forms.py: Form definitions
   - admin.py: Admin interface customization

3. Database Models
   - Company
   - Supplier
   - Vineyard
   - Harvest
   - Cellar
   - Tank
   - CrushedJuiceAllocation

## Technical Constraints
1. Data Integrity
   - Foreign key relationships must be maintained
   - Volume calculations must be accurate
   - Croatian-specific identifiers must be valid

2. Performance
   - Real-time volume tracking
   - Concurrent user access
   - Form validation processing

3. Security
   - User authentication required
   - Data access controls
   - Input validation and sanitization

4. Compliance
   - Croatian regulatory requirements
   - Data format standards
   - Identification number formats (OIB, IBK, MIBPG)
