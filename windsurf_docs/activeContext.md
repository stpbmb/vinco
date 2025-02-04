# Active Context

## Current Work
Implementing multi-tenancy architecture to support multiple organizations in the wine production management system, and planning the implementation of standalone apps and an optional webshop.

### Recent Changes
1. Created organizations app with:
   - Organization and OrganizationUser models for tenant management
   - Organization selection views and middleware
   - Role-based access control (owner, admin, member)

2. Added tenant awareness to all models:
   - Created TenantModel base class in core app
   - Updated all models to inherit from TenantModel
   - Added organization field and validation
   - Models updated: Vineyard, Supplier, Harvest, Tank, Bottle, Box, etc.

3. Implemented tenant data isolation:
   - Added TenantMiddleware for request processing
   - Created TenantRouter for database operations
   - Added TenantViewMixin for view-level filtering
   - Created TenantFormMixin for form-level filtering

4. Fixed redirect loops between dashboard and organization selection by:
   - Centralizing organization context handling in TenantMiddleware
   - Adding session verification and transaction safety
   - Simplifying TenantViewMixin to avoid conflicts
   - Improving error handling and logging

### Core Apps
1. **Vineyards App**:
   - Manage vineyard blocks and plots
   - Track viticulture operations
   - Monitor soil and climate data

2. **Harvests App**:
   - Plan and track harvest operations
   - Record grape collection data
   - Quality assessment tracking

3. **Cellars App**:
   - Monitor wine aging process
   - Track cellar conditions
   - Manage storage locations

4. **Packaging App**:
   - Handle bottling operations
   - Manage label designs
   - Track packaging materials

5. **Inventory App**:
   - Track wine stock across all stages
   - Monitor production batches
   - Set organization-specific pricing
   - Real-time stock management
   - Integration with production data

6. **Sales App**:
   - Record direct sales (B2B/B2C)
   - Generate invoices and receipts
   - Manage customer relationships
   - Track payments and transactions
   - Sales analytics and reporting

7. **Tasks App**:
   - Cross-module task management
   - Task assignment and tracking
   - Due date monitoring
   - Priority management
   - Task status updates
   - Integration with all production modules

8. **Settings App**:
   - Organization profile management
   - User account administration
   - Role and permission management
   - Organization preferences
   - User invitation system
   - Audit logging

### Optional Webshop Implementation
1. **Global Marketplace**:
   - Display products from all organizations
   - Advanced filtering (organization, wine type, region)
   - Organization-specific storefronts
   - Custom branding per organization

2. **Direct Payment System**:
   - Stripe Connect integration
   - Organization-specific payment processing
   - Secure payment handling
   - Transaction monitoring

### Next Steps
1. Update remaining templates to handle organization context
2. Add organization switching functionality in the UI
3. Implement data migration strategy for existing records
4. Create Settings app infrastructure
   - Organization profile management
   - User management interface
   - Permission system UI
   - Settings views and forms
5. Create organization management views
6. Implement Inventory app core features
7. Develop Sales app functionality
8. Create Tasks app infrastructure
9. Set up optional webshop infrastructure (if needed)
10. Integrate Stripe Connect for organizations (if webshop enabled)
11. Comprehensive testing of all components

## Design Patterns
- Using wine-themed colors (wine-600, wine-700) for primary actions
- Consistent spacing and typography using Tailwind's utility classes
- Modern UI components with hover states
- Responsive design for all screen sizes
- Custom form styles with validation feedback
- Consistent table layouts with status indicators
- Interactive data visualization components
