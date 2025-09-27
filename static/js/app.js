// Advanced LeetCode Leaderboard - JavaScript Enhancement

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Add animation classes to elements
    addAnimations();
    
    // Setup auto-refresh functionality
    setupAutoRefresh();
    
    // Setup tooltips and popovers
    setupBootstrapComponents();
    
    // Setup dynamic interactions
    setupDynamicInteractions();
});

function initializeApp() {
    console.log('🚀 Advanced LeetCode Leaderboard initialized');
    
    // Add loading animations to buttons
    setupButtonAnimations();
    
    // Setup table interactions
    setupTableInteractions();
    
    // Setup progress bar animations
    animateProgressBars();
}

function addAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Add slide-in animations to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        row.style.animationDelay = `${index * 0.05}s`;
        row.classList.add('slide-in-left');
    });
}

function setupAutoRefresh() {
    // Add auto-refresh toggle
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const autoRefreshItem = document.createElement('li');
        autoRefreshItem.className = 'nav-item';
        autoRefreshItem.innerHTML = `
            <div class="nav-link">
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="autoRefresh">
                    <label class="form-check-label" for="autoRefresh">
                        <small>Auto-refresh</small>
                    </label>
                </div>
            </div>
        `;
        navbar.appendChild(autoRefreshItem);
        
        // Setup auto-refresh functionality
        const autoRefreshCheckbox = document.getElementById('autoRefresh');
        let refreshInterval;
        
        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(() => {
                    if (window.location.pathname === '/') {
                        showToast('Refreshing leaderboard...', 'info');
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                }, 300000); // Refresh every 5 minutes
                showToast('Auto-refresh enabled (5 minutes)', 'success');
            } else {
                clearInterval(refreshInterval);
                showToast('Auto-refresh disabled', 'warning');
            }
        });
    }
}

function setupBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers  
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function setupButtonAnimations() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

function setupTableInteractions() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        // Add hover effects
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.zIndex = '10';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.zIndex = '1';
        });
        
        // Add click to view details
        const usernameCell = row.querySelector('a[href*="/user/"]');
        if (usernameCell) {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(e) {
                if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
                    usernameCell.click();
                }
            });
        }
    });
}

function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    // Intersection Observer for progressive loading
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                
                setTimeout(() => {
                    progressBar.style.width = width;
                }, 100);
                
                observer.unobserve(progressBar);
            }
        });
    });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

function setupDynamicInteractions() {
    // Add dynamic sorting indicators
    const sortLinks = document.querySelectorAll('.dropdown-item[href*="sort_by"]');
    sortLinks.forEach(link => {
        link.addEventListener('click', function() {
            showToast('Sorting leaderboard...', 'info');
        });
    });
    
    // Add confirmation dialogs for destructive actions
    const deleteButtons = document.querySelectorAll('a[href*="/remove_user/"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const username = this.getAttribute('href').split('/').pop();
            
            showConfirmDialog(
                'Remove User',
                `Are you sure you want to remove ${username} from the leaderboard?`,
                'danger',
                () => {
                    window.location.href = this.getAttribute('href');
                }
            );
        });
    });
    
    // Add loading states for update buttons
    const updateButtons = document.querySelectorAll('a[href*="/update_user/"], a[href="/update_all"]');
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-hourglass-split loading"></i> Updating...';
            this.classList.add('disabled');
            
            // Show toast
            showToast('Updating user data... This may take a few moments.', 'info');
        });
    });
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1050';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    
    // Initialize and show toast
    const toast = new bootstrap.Toast(toastElement, {
        delay: type === 'info' ? 5000 : 3000
    });
    toast.show();
    
    // Remove element after hiding
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function showConfirmDialog(title, message, type, callback) {
    // Create modal
    const modalId = 'confirmModal';
    let modal = document.getElementById(modalId);
    
    if (modal) {
        modal.remove();
    }
    
    const modalHTML = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content bg-secondary text-white">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-light" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-${type}" id="confirmAction">Confirm</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    modal = document.getElementById(modalId);
    
    // Setup event listeners
    document.getElementById('confirmAction').addEventListener('click', function() {
        callback();
        bootstrap.Modal.getInstance(modal).hide();
    });
    
    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Clean up after modal is hidden
    modal.addEventListener('hidden.bs.modal', function() {
        modal.remove();
    });
}

// Search functionality
function setupSearch() {
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control';
    searchInput.placeholder = 'Search users...';
    searchInput.style.maxWidth = '200px';
    
    const navbarNav = document.querySelector('.navbar-nav');
    if (navbarNav) {
        const searchItem = document.createElement('li');
        searchItem.className = 'nav-item me-2';
        searchItem.appendChild(searchInput);
        navbarNav.insertBefore(searchItem, navbarNav.firstChild);
    }
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const tableRows = document.querySelectorAll('tbody tr');
        
        tableRows.forEach(row => {
            const username = row.querySelector('a').textContent.toLowerCase();
            if (username.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

// Performance monitoring
function trackPerformance() {
    // Track page load time
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`⚡ Page loaded in ${Math.round(loadTime)}ms`);
        
        if (loadTime > 3000) {
            showToast('Page loaded slowly. Consider refreshing if data seems outdated.', 'warning');
        }
    });
}

// Initialize additional features
document.addEventListener('DOMContentLoaded', function() {
    setupSearch();
    trackPerformance();
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + R: Refresh page
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        showToast('Refreshing...', 'info');
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }
    
    // Ctrl + A: Go to add user page
    if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        window.location.href = '/add_user';
    }
    
    // Escape: Close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            bootstrap.Modal.getInstance(modal)?.hide();
        });
    }
});