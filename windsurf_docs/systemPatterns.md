# System Patterns

## Architecture Overview

### Multi-Tenancy Pattern

#### Organization Context Handling

The application uses a middleware-based approach for handling organization context:

1. TenantMiddleware (Primary Handler):
   - Intercepts all requests
   - Manages organization context and session
   - Handles redirects for organization selection
   - Skips checks for exempt URLs (static, admin, auth)
   - Uses database transactions for data safety
   - Comprehensive logging for debugging

2. TenantViewMixin (Secondary Handler):
   - Ensures login requirement
   - Acts as safety net for middleware
   - Minimal logic to prevent conflicts

3. Organization Selection:
   - Transaction-based organization selection
   - Session verification after save
   - Smart next URL handling
   - User-friendly error messages

#### Session Management

- Organization ID stored in session
- Explicit session saves
- Session verification after writes
- Cleanup of invalid session data

### Model Patterns
1. **Base Models**
   - `TenantModel`: Adds organization field and validation
   - Common fields: created_by, updated_by, created_at, updated_at

2. **Relationship Rules**
   - ForeignKey relationships must be within same organization
   - Validation enforced at model and form level
   - Database constraints prevent invalid relationships

### View Patterns
1. **Class-Based Views**
   - Use `TenantViewMixin` for organization filtering
   - Handle organization context in forms
   - Validate user access to organization

2. **Form Handling**
   - Use `TenantFormMixin` for organization context
   - Filter related object choices by organization
   - Set organization on model save

### UI Patterns
1. **Organization Context**
   - Organization selection required
   - Current organization displayed in header
   - Organization switching in user menu

2. **Data Display**
   - Only show data from current organization
   - Clear empty states for no data
   - Consistent styling across modules

### E-commerce Patterns

#### Global Webshop Architecture
1. **Django Oscar Integration**:
   - Customized catalog app for wine products
   - Multi-organization product listings
   - Organization-specific storefronts
   - URL-based organization filtering

2. **URL Routing**:
   - Global webshop: `/shop/`
   - Organization storefronts: `/shop/org/<org-name>/` or `<org-name>.domain.com/shop/`
   - Product detail: `/shop/org/<org-name>/products/<product-id>/`
   - Category views: `/shop/org/<org-name>/category/<category-slug>/`

3. **Data Access Patterns**:
   - Global product listing with organization context
   - Organization-specific product views
   - Filtered catalog queries
   - Cache strategies for performance

#### Payment Integration
1. **Stripe Connect Flow**:
   - OAuth-based account connection
   - Secure credential storage
   - Webhook handling
   - Error management

2. **Payment Processing**:
   - Direct-to-organization payments
   - Transaction logging
   - Refund handling
   - Order status management

#### Inventory Management
1. **Stock Control**:
   - Real-time inventory tracking
   - Organization-specific stock levels
   - Low stock alerts
   - Reservation system

2. **Data Synchronization**:
   - Production to inventory sync
   - Order to inventory updates
   - Stock level verification
   - Audit logging

## Core Apps Architecture

### Vineyards App
1. **Block Management**:
   - Hierarchical structure (vineyard → block → plot)
   - GPS coordinate tracking
   - Soil composition data
   - Climate monitoring

2. **Operations Tracking**:
   - Viticulture activities log
   - Resource allocation
   - Task scheduling
   - Weather impact analysis

### Harvests App
1. **Planning**:
   - Schedule optimization
   - Resource allocation
   - Yield predictions
   - Quality targets

2. **Execution**:
   - Real-time data collection
   - Quality measurements
   - Transport logistics
   - Batch tracking

### Cellars App
1. **Storage Management**:
   - Location tracking
   - Environmental monitoring
   - Capacity planning
   - Movement history

2. **Aging Process**:
   - Timeline tracking
   - Quality checkpoints
   - Tasting notes
   - Condition alerts

### Packaging App
1. **Production Line**:
   - Bottling workflow
   - Label application
   - Quality control
   - Batch tracking

2. **Materials Management**:
   - Inventory tracking
   - Supplier integration
   - Quality standards
   - Waste reduction

### Inventory App
1. **Core Functionality**:
   - Track production batches (vineyard → harvest → tank → bottle)
   - Monitor stock levels across all stages
   - Set organization-specific pricing
   - Generate stock reports

2. **Integration Points**:
   - Sync with vineyard data
   - Track harvest batches
   - Monitor cellar storage
   - Link with packaging operations
   - Optional webshop integration

### Sales App
1. **Core Functionality**:
   - Record all sales (direct, wholesale, retail)
   - Generate invoices and receipts
   - Customer relationship management
   - Payment tracking and reconciliation

2. **Integration Points**:
   - Real-time inventory updates
   - Customer database management
   - Financial reporting
   - Optional webshop integration

### Optional Webshop
1. **Global Marketplace**:
   - Multi-organization catalog
   - Advanced filtering
   - Organization storefronts
   - Custom branding

2. **Payment Processing**:
   - Stripe Connect integration
   - Direct organization payments
   - Secure transactions
   - Webhook handling

## Technical Decisions

1. **Single Database**
   - Simpler deployment and maintenance
   - Efficient resource utilization
   - Easy data aggregation across tenants

2. **Role-Based Access**
   - Owner: Full control of organization
   - Admin: Manage organization data
   - Member: View and use organization data

3. **Data Validation**
   - Model-level organization validation
   - Form-level filtering and validation
   - Database-level constraints

## Error Handling
1. **Organization Context**
   - Redirect to organization selection if missing
   - Clear error messages for access issues
   - Validation errors for cross-organization operations

2. **Data Access**
   - 404 for non-existent or inaccessible objects
   - Permission denied for unauthorized access
   - Validation errors for invalid operations

## Technical Patterns

### Data Access
1. **Multi-tenancy**:
   - Organization-based filtering
   - Data isolation
   - Cross-organization features
   - Permission management

2. **Caching Strategy**:
   - View-level caching
   - Query optimization
   - Cache invalidation
   - Real-time updates

### Security
1. **Authentication**:
   - Role-based access
   - Organization context
   - Session management
   - API security

2. **Data Protection**:
   - Encryption at rest
   - Secure communications
   - Audit logging
   - Backup strategy

### UI/UX
1. **Components**:
   - Consistent styling
   - Responsive design
   - Interactive elements
   - Status indicators

2. **Workflows**:
   - User journey mapping
   - Error handling
   - Progress tracking
   - Feedback systems
