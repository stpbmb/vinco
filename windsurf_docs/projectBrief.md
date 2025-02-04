# Vinco - Project Brief

## Project Overview
Vinco is a comprehensive wine production management system built with Django. The application serves as an end-to-end solution for managing vineyard operations, harvest tracking, wine production processes, inventory control, and sales operations.

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

### 5. Inventory Management
- Complete wine stock tracking
- Multi-location inventory control
- Batch management
- Organization-specific pricing
- Real-time monitoring

### 6. Sales Operations
- Direct sales processing (B2B/B2C)
- Customer relationship management
- Invoice generation
- Payment tracking
- Sales analytics

### 7. Task Management
- Cross-module task tracking
- Assignment and responsibility management
- Due date and priority handling
- Workflow automation
- Progress monitoring
- Integration with all production stages

### 8. Optional Webshop
- Global marketplace
- Organization-specific storefronts
- Online payment processing
- Integration with inventory and sales

## Technical Architecture

### Technology Stack
- **Backend Framework**: Django 4.x
- **API Framework**: Django REST Framework
- **Frontend**: Tailwind CSS with JavaScript
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache**: Redis
- **Background Tasks**: Celery
- **Payment Processing**: Stripe Connect (optional)
- **Development Tools**: django-debug-toolbar

### Project Structure
```
vinco/
├── core/         # Core functionality and multi-tenancy
├── organizations/# Organization management
├── vineyards/    # Vineyard management module
├── harvests/     # Harvest tracking module
├── packaging/    # Packaging operations
├── cellars/     # Cellar management
├── inventory/    # Stock management
├── sales/       # Sales operations
├── tasks/       # Task management
├── webshop/     # Optional online store
├── static/      # Static assets
└── templates/   # HTML templates
```

## Development Standards
1. **Code Organization**
   - Follow Django best practices
   - Maintain app independence
   - Clear separation of concerns
   - Multi-tenancy aware models

2. **UI/UX Standards**
   - Consistent Tailwind CSS styling
   - Wine-themed components
   - Responsive design
   - Accessible interfaces

3. **Testing Requirements**
   - Unit tests for models and views
   - Integration testing
   - Multi-tenancy testing
   - Performance testing

4. **Documentation**
   - Code documentation
   - API documentation
   - User guides
   - Design patterns
