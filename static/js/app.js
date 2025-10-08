// Advanced LeetCode Leaderboard - JavaScript Enhancement

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Add animation classes to elements
    addAnimations();
    
    // Setup auto-refresh functionality
    setupAutoRefresh();
    
    // Setup real-time data fetching
    setupLiveDataFetching();
    
    // Setup tooltips and popovers
    setupBootstrapComponents();
    
    // Setup dynamic interactions
    setupDynamicInteractions();
});

function setupLiveDataFetching() {
    // Add refresh buttons to the navbar
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const refreshContainer = document.createElement('li');
        refreshContainer.className = 'nav-item dropdown';
        refreshContainer.innerHTML = `
            <button class="nav-link btn btn-link dropdown-toggle" id="refreshDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-sync-alt" id="refreshIcon"></i>
                <span class="d-none d-md-inline ms-1">Refresh Data</span>
            </button>
            <ul class="dropdown-menu" aria-labelledby="refreshDropdown">
                <li><a class="dropdown-item" href="#" onclick="fetchLiveData()">
                    <i class="fas fa-bolt text-warning me-2"></i>Quick Refresh
                    <small class="text-muted d-block">Instant update from cache</small>
                </a></li>
                <li><a class="dropdown-item" href="#" onclick="triggerFullUpdate()">
                    <i class="fas fa-cloud-download-alt text-primary me-2"></i>Full Update
                    <small class="text-muted d-block">Fresh data from LeetCode (~2-3 min)</small>
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-muted" href="#">
                    <i class="fas fa-clock me-2"></i>Auto-refresh: Every 2 hours
                </a></li>
            </ul>
        `;
        navbar.appendChild(refreshContainer);
    }
    
    // Automatically fetch fresh data when page loads (only on main page)
    if (window.location.pathname === '/' || window.location.pathname === '') {
        // Add loading indicator
        showLoadingState();
        
        // Fetch fresh data after a short delay
        setTimeout(() => {
            fetchLiveData(true); // true = silent mode (no toast)
        }, 1000);
    }
}

function fetchLiveData(silent = false) {
    const refreshIcon = document.getElementById('refreshIcon');
    const refreshDropdown = document.getElementById('refreshDropdown');
    
    if (!silent) {
        showToast('Fetching fresh LeetCode data...', 'info');
    }
    
    // Add spinning animation to refresh icon
    if (refreshIcon) {
        refreshIcon.classList.add('fa-spin');
    }
    
    if (refreshDropdown) {
        refreshDropdown.disabled = true;
    }
    
    // Show loading state on leaderboard
    showLoadingState();
    
    fetch('/api/live-data')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the leaderboard with fresh data
                updateLeaderboardDisplay(data.leaderboard, data.stats);
                
                if (!silent) {
                    const updatedCount = data.updated_users ? data.updated_users.length : 0;
                    const failedCount = data.failed_users ? data.failed_users.length : 0;
                    
                    let message = `Updated ${updatedCount} users successfully!`;
                    if (failedCount > 0) {
                        message += ` (${failedCount} failed)`;
                    }
                    
                    showToast(message, failedCount > 0 ? 'warning' : 'success');
                }
                
                // Update last updated time
                updateLastUpdatedTime(data.timestamp);
                
            } else {
                if (!silent) {
                    showToast('Failed to fetch fresh data: ' + data.message, 'error');
                }
                console.error('Live data fetch failed:', data.message);
            }
        })
        .catch(error => {
            if (!silent) {
                showToast('Error fetching live data. Please try again.', 'error');
            }
            console.error('Error fetching live data:', error);
        })
        .finally(() => {
            // Remove loading states
            hideLoadingState();
            
            if (refreshIcon) {
                refreshIcon.classList.remove('fa-spin');
            }
            
            if (refreshDropdown) {
                refreshDropdown.disabled = false;
            }
        });
}

function triggerFullUpdate() {
    const refreshIcon = document.getElementById('refreshIcon');
    const refreshDropdown = document.getElementById('refreshDropdown');
    
    showToast('🚀 Triggering full leaderboard update...', 'info');
    
    // Add spinning animation to refresh icon
    if (refreshIcon) {
        refreshIcon.classList.add('fa-spin');
    }
    
    if (refreshDropdown) {
        refreshDropdown.disabled = true;
    }
    
    // Show loading state on leaderboard
    showLoadingState();
    
    fetch('/api/trigger-update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('✅ ' + data.message, 'success');
                
                // Optionally refresh the current display after a delay
                setTimeout(() => {
                    showToast('🔄 Auto-refreshing display with updated data...', 'info');
                    fetchLiveData(true); // silent refresh to show updated data
                }, 3000);
                
            } else {
                showToast('❌ ' + data.message, 'error');
                console.error('Full update failed:', data.message);
            }
        })
        .catch(error => {
            showToast('❌ Failed to trigger update: ' + error.message, 'error');
            console.error('Full update error:', error);
        })
        .finally(() => {
            // Remove loading states
            hideLoadingState();
            
            if (refreshIcon) {
                refreshIcon.classList.remove('fa-spin');
            }
            
            if (refreshDropdown) {
                refreshDropdown.disabled = false;
            }
        });
}

function updateLeaderboardDisplay(leaderboard, stats) {
    // Update the main leaderboard table
    const tableBody = document.querySelector('#leaderboard-table tbody');
    if (tableBody && leaderboard) {
        // Clear existing rows
        tableBody.innerHTML = '';
        
        // Add new rows
        leaderboard.forEach((user, index) => {
            const row = createLeaderboardRow(user, index + 1);
            tableBody.appendChild(row);
        });
        
        // Re-apply animations and interactions
        setupTableInteractions();
    }
    
    // Update stats cards
    if (stats) {
        updateStatsCards(stats);
    }
}

function createLeaderboardRow(user, position) {
    const row = document.createElement('tr');
    row.className = 'slide-in-left';
    row.style.animationDelay = `${position * 0.05}s`;
    
    // Position emoji
    let positionEmoji = position <= 3 ? 
        ['🥇', '🥈', '🥉'][position - 1] : 
        `${position}.`;
    
    // Activity indicator
    const weeklyTotal = user.weekly_total || 0;
    let activity = weeklyTotal >= 10 ? '🔥 Very Active' :
                   weeklyTotal >= 5 ? '✅ Active' :
                   weeklyTotal >= 1 ? '⚡ Some' : '😴 Quiet';
    
    // Format ranking
    const rankingStr = user.ranking > 0 ? `#${user.ranking.toLocaleString()}` : 'N/A';
    
    // Format last updated
    let timeStr = 'Just now';
    try {
        const lastUpdated = new Date(user.last_updated);
        timeStr = lastUpdated.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric' });
    } catch (e) {
        timeStr = 'Unknown';
    }
    
    row.innerHTML = `
        <td><strong>${positionEmoji}</strong></td>
        <td>
            <a href="/user/${user.username}" class="text-decoration-none">
                <strong>${user.username}</strong>
            </a>
        </td>
        <td><strong>${user.weekly_base_score || 0}</strong></td>
        <td>${user.weekly_easy || 0}/${user.weekly_medium || 0}/${user.weekly_hard || 0}</td>
        <td><strong>${user.base_score || 0}</strong></td>
        <td>${user.easy || 0}/${user.medium || 0}/${user.hard || 0}</td>
        <td>${rankingStr}</td>
        <td>${activity}</td>
        <td>${timeStr}</td>
    `;
    
    return row;
}

function updateStatsCards(stats) {
    // Update various stats elements if they exist
    const elements = {
        'total-users': stats.total_users,
        'weekly-problems': stats.weekly_problems,
        'weekly-score': stats.weekly_score,
        'avg-weekly-score': stats.avg_weekly_score
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.textContent = typeof value === 'number' ? value.toLocaleString() : value;
        }
    });
    
    // Update leader info if available
    if (stats.leader) {
        const leaderElement = document.getElementById('weekly-leader');
        if (leaderElement) {
            leaderElement.textContent = `${stats.leader.username} (${stats.leader.weekly_base_score || 0} pts)`;
        }
    }
}

function showLoadingState() {
    const tableBody = document.querySelector('#leaderboard-table tbody');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading fresh data...</span>
                    </div>
                    <div class="mt-2">Fetching latest LeetCode data...</div>
                </td>
            </tr>
        `;
    }
}

function hideLoadingState() {
    // Loading state will be replaced by updateLeaderboardDisplay
}

function updateLastUpdatedTime(timestamp) {
    const timeElement = document.getElementById('last-updated-time');
    if (timeElement) {
        try {
            const date = new Date(timestamp);
            timeElement.textContent = date.toLocaleString();
        } catch (e) {
            timeElement.textContent = 'Just now';
        }
    }
}

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

// Utility Functions
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type}" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: type === 'error' ? 7000 : 4000
    });
    
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function showConfirmDialog(title, message, type = 'danger', onConfirm) {
    // Create modal if it doesn't exist
    let confirmModal = document.getElementById('confirm-modal');
    if (!confirmModal) {
        const modalHtml = `
            <div class="modal fade" id="confirm-modal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content bg-dark text-light">
                        <div class="modal-header">
                            <h5 class="modal-title" id="confirm-modal-title"></h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="confirm-modal-body"></div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn" id="confirm-modal-confirm">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        confirmModal = document.getElementById('confirm-modal');
    }
    
    // Update modal content
    document.getElementById('confirm-modal-title').textContent = title;
    document.getElementById('confirm-modal-body').textContent = message;
    
    const confirmButton = document.getElementById('confirm-modal-confirm');
    confirmButton.className = `btn btn-${type}`;
    confirmButton.textContent = 'Confirm';
    
    // Set up confirm handler
    confirmButton.onclick = function() {
        if (onConfirm) onConfirm();
        bootstrap.Modal.getInstance(confirmModal).hide();
    };
    
    // Show modal
    new bootstrap.Modal(confirmModal).show();
}