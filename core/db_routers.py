class TenantRouter:
    """
    Database router that handles tenant-specific database operations.
    """
    def db_for_read(self, model, **hints):
        """
        Point all read operations to the appropriate database.
        For now, we're using a single database, but this can be extended
        to support multiple databases per tenant.
        """
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Point all write operations to the appropriate database.
        For now, we're using a single database, but this can be extended
        to support multiple databases per tenant.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations only if both objects are in the same organization.
        """
        if hasattr(obj1, 'organization') and hasattr(obj2, 'organization'):
            return obj1.organization_id == obj2.organization_id
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure all migrations are run on the appropriate database.
        """
        return True
