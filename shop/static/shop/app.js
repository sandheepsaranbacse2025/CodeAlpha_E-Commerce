// E-Commerce Store Shared Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
    // Initialize common items
    window.syncAuthNav();
    window.syncCartBadge();
});

// 1. Alert / Toast Notification System
window.showNotification = function(message, type = 'success') {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    let icon = '<i class="fa-solid fa-circle-check"></i>';
    if (type === 'error') {
        icon = '<i class="fa-solid fa-triangle-exclamation"></i>';
    } else if (type === 'warning') {
        icon = '<i class="fa-solid fa-circle-info"></i>';
    }

    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            ${icon}
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;

    container.appendChild(notification);

    // Close button event
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });

    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
};

// 2. Synchronize User Session & Header Navigation
window.syncAuthNav = async function() {
    const authSection = document.getElementById('auth-nav-section');
    const ordersLink = document.getElementById('nav-orders-link');
    if (!authSection) return;

    try {
        const res = await fetch('/api/auth-status/');
        const data = await res.json();

        if (data.authenticated) {
            // User is logged in
            authSection.innerHTML = `
                <div class="user-menu" id="user-profile-menu">
                    <i class="fa-solid fa-user-circle" style="font-size: 1.25rem; color: var(--accent);"></i>
                    <span class="user-name">${data.user.username}</span>
                    <button class="btn btn-secondary" onclick="window.logoutUser()" style="padding: 0.4rem 0.8rem; font-size: 0.8rem; margin-left: 0.5rem;">
                        <i class="fa-solid fa-right-from-bracket"></i>
                    </button>
                </div>
            `;
            if (ordersLink) ordersLink.style.display = 'block';
        } else {
            // Guest User
            authSection.innerHTML = `
                <a href="/login/" class="btn btn-secondary" style="padding: 0.5rem 1rem; font-size: 0.85rem;">Login</a>
                <a href="/register/" class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.85rem;">Register</a>
            `;
            if (ordersLink) ordersLink.style.display = 'none';
        }
    } catch (error) {
        console.error('Error syncing auth state:', error);
    }
};

// 3. Synchronize Cart Item Quantity Badge
window.syncCartBadge = async function() {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;

    try {
        const res = await fetch('/api/cart/');
        if (res.status === 401) {
            // Guest users - hide badge
            badge.style.display = 'none';
            return;
        }

        const data = await res.json();
        const items = data.cart || [];
        
        // Sum up total quantity
        const totalQty = items.reduce((sum, item) => sum + item.quantity, 0);

        if (totalQty > 0) {
            badge.textContent = totalQty;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    } catch (error) {
        console.error('Error syncing cart badge:', error);
    }
};

// 4. Global Action to Add Items to Cart
window.addToCart = async function(productId, quantity = 1) {
    try {
        const authRes = await fetch('/api/auth-status/');
        const authData = await authRes.json();
        
        if (!authData.authenticated) {
            window.showNotification('Please log in to add items to your cart.', 'error');
            // Redirect to login page with query param
            setTimeout(() => {
                window.location.href = `/login/?next=${encodeURIComponent(window.location.pathname)}`;
            }, 1500);
            return false;
        }

        const res = await fetch('/api/cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        const data = await res.json();

        if (res.ok) {
            window.showNotification(data.message || 'Product added to cart!', 'success');
            await window.syncCartBadge();
            return true;
        } else {
            window.showNotification(data.error || 'Failed to add item to cart.', 'error');
            return false;
        }

    } catch (error) {
        console.error('Error adding to cart:', error);
        window.showNotification('An error occurred. Please try again.', 'error');
        return false;
    }
};

// 5. Global Action to Logout
window.logoutUser = async function() {
    try {
        const res = await fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (res.ok) {
            window.showNotification('You have logged out.', 'success');
            await window.syncAuthNav();
            await window.syncCartBadge();
            // Redirect to shop root after short delay
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } else {
            window.showNotification('Logout failed.', 'error');
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.showNotification('Failed to connect to server.', 'error');
    }
};
