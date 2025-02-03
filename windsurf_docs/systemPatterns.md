# System Patterns

## Architecture Overview

### Multi-Tenancy Architecture
The system uses a single-database multi-tenancy approach with the following components:

1. **Core Components**
   - `Organization` model: Represents tenant organizations
   - `OrganizationUser` model: Links users to organizations with roles
   - `TenantModel`: Base class for all tenant-aware models
   - `TenantMiddleware`: Handles organization context in requests
   - `TenantRouter`: Manages database operations
   - `TenantViewMixin`: Provides organization-based filtering in views
   - `TenantFormMixin`: Handles organization context in forms

2. **Data Isolation**
   - Each model inherits from `TenantModel`
   - All queries are automatically filtered by organization
   - Related objects must belong to the same organization
   - Forms filter choices by organization

3. **Access Control**
   - Users can belong to multiple organizations
   - Role-based permissions within organizations
   - Organization selection required for access

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
