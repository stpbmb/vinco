# Vinco - Project Brief

## Project Overview
Vinco is a comprehensive wine production management system built with Django. The application serves as an end-to-end solution for managing vineyard operations, harvest tracking, and wine production processes.

## Core Functionality

### 1. Vineyard Management
- Tracking of owned and supplier vineyards
- Management of vineyard details (location, size, grape varieties)
- Supplier relationship management
- Harvest history monitoring

### 2. Harvest Operations
- Recording and tracking grape harvests
- Juice yield tracking and management
- Tank allocation system
- Volume management and calculations

### 3. Production & Packaging
- Bottling operation management
- Inventory control
- Packaging process tracking

### 4. Cellar Management
- Tank and cellar monitoring
- Storage management
- Production process tracking

## Technical Architecture

### Technology Stack
- **Backend Framework**: Django 4.2+
- **Frontend**: Bootstrap 5 with JavaScript
- **Database**: PostgreSQL
- **Form Processing**: django-crispy-forms with crispy-bootstrap4
- **Development Tools**: django-debug-toolbar

### Project Structure
```
vinco/
├── vineyards/     # Vineyard management module
├── harvests/      # Harvest tracking module
├── packaging/     # Packaging operations
├── cellars/      # Cellar management
├── core/         # Core functionality
├── static/       # Static assets
└── templates/    # HTML templates
```

## Development Standards

### Code Quality
- Follows PEP 8 Python coding standards
- Django best practices for views and models
- Bootstrap conventions for frontend
- Comprehensive documentation requirements

### Testing
- Test coverage for new features
- Integration with pytest
- Continuous testing practices

## Security & Authentication
- Built-in Django Authentication System
- Environment-based configuration
- Secure database handling

## Deployment & Environment
- PostgreSQL database in production
- Environment variable configuration
- Staticfiles management
- Logging system in place

## Current Status
The project appears to be in active development with a solid foundation of core features implemented. The modular architecture allows for easy expansion and maintenance of different aspects of wine production management.
