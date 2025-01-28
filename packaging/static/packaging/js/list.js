document.addEventListener('DOMContentLoaded', function() {
    // Handle clickable rows
    const rows = document.querySelectorAll('.clickable-row');
    rows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on a button or link
            if (e.target.tagName === 'A' || e.target.tagName === 'BUTTON' || 
                e.target.closest('a') || e.target.closest('button')) {
                return;
            }
            window.location.href = this.dataset.href;
        });

        // Add hover effect
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(0, 123, 255, 0.1)';
        });

        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Handle stock alerts
    const stockBadges = document.querySelectorAll('.stock-badge');
    stockBadges.forEach(badge => {
        const stock = parseInt(badge.dataset.stock);
        const minStock = parseInt(badge.dataset.minStock);
        
        if (stock <= minStock) {
            badge.classList.add('bg-danger');
            badge.title = 'Stock is at or below minimum level';
        } else {
            badge.classList.add('bg-success');
            badge.title = 'Stock level is good';
        }
    });
});
