# Technical Context

## Technologies Used

### Backend
- Django 4.x
- Python 3.x
- PostgreSQL (production) / SQLite (development)
- Django REST Framework for API endpoints
- Celery for background tasks
- Redis for caching

### Frontend
- Tailwind CSS for styling
- JavaScript for dynamic interactions
- HTML templates with Django template language
- Chart.js for data visualization

## Core Components

### Multi-Tenancy Components
1. **Core App**
   - `TenantModel`: Base model for tenant isolation
   - `TenantMiddleware`: Request processing
   - `TenantRouter`: Database operations
   - `TenantViewMixin`: View filtering
   - `TenantFormMixin`: Form handling

2. **Organizations App**
   - `Organization`: Tenant model
   - `OrganizationUser`: User-tenant relationship
   - Organization selection views
   - Role-based access control

### Production Management
1. **Vineyards App**
   - Purpose: Manage vineyard operations
   - Models: Vineyard, Block, Plot
   - Features:
     - GPS tracking
     - Climate monitoring
     - Task scheduling

2. **Harvests App**
   - Purpose: Plan and execute harvests
   - Models: Harvest, Batch, Quality
   - Features:
     - Scheduling system
     - Quality tracking
     - Yield management

3. **Cellars App**
   - Purpose: Wine aging and storage
   - Models: Cellar, Tank, Barrel
   - Features:
     - Environment monitoring
     - Aging timeline
     - Location tracking

4. **Packaging App**
   - Purpose: Bottling and labeling
   - Models: Bottle, Label, Package
   - Features:
     - Production line tracking
     - Quality control
     - Material management

5. **Inventory App**
   - Purpose: Complete stock management system
   - Models: Stock, Price, Location, Batch
   - Features:
     - Real-time tracking
     - Multi-location support
     - Pricing management
     - Integration with production apps

6. **Sales App**
   - Purpose: Sales and customer management
   - Models: Sale, Customer, Invoice, Payment
   - Features:
     - Order processing
     - Invoice generation
     - Customer database
     - Analytics dashboard

7. **Tasks App**
   - Purpose: Cross-module task management system
   - Models: Task, TaskCategory, TaskTemplate, TaskAssignment
   - Features:
     - Task creation and tracking
     - Assignment management
     - Due date monitoring
     - Priority handling
     - Status workflows
     - Integration with all modules

### Optional Components
1. **Webshop**
   - Framework: Django Oscar
   - Features:
     - Multi-organization catalog
     - Custom storefronts
     - Advanced filtering
     - Integration with Inventory and Sales apps

2. **Payment Processing**
   - Platform: Stripe Connect
   - Features:
     - Direct organization payments
     - Secure transactions
     - Webhook handling

## Development Setup

### Prerequisites
- Python 3.x
- pip
- virtualenv
- PostgreSQL (optional for development)
- Node.js and npm (for frontend assets)

### Installation Steps
1. Create and activate virtual environment
2. Install dependencies from requirements.txt
3. Install frontend dependencies (npm install)
4. Run database migrations
5. Create initial superuser
6. Create initial organization

### Environment Variables
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode flag
- `ALLOWED_HOSTS`: Allowed host names
- `REDIS_URL`: Redis connection string
- `STRIPE_*`: Stripe API keys (if using webshop)

## Technical Constraints
1. **Database**:
   - PostgreSQL in production
   - Proper indexing for multi-tenant queries
   - Regular backup strategy

2. **Security**:
   - HTTPS required
   - Secure session handling
   - Regular dependency updates
   - Data encryption at rest

3. **Performance**:
   - Query optimization
   - Caching strategy
   - Background task queuing
   - Asset compression

4. **Scalability**:
   - Horizontal scaling ready
   - Load balancer compatible
   - Static file separation
   - CDN support
