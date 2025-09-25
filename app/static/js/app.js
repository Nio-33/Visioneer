// Visioneer Application JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Character counter for textareas
    const textareas = document.querySelectorAll('textarea[data-max-length]');
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        textarea.parentNode.appendChild(counter);

        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${textarea.value.length}/${maxLength} characters`;
            
            if (remaining < 50) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
            
            if (remaining < 0) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // Image preview for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create or update preview
                    let preview = input.parentNode.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview mt-2';
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <div class="border rounded p-2">
                            <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 150px;">
                            <div class="mt-1">
                                <small class="text-muted">${file.name}</small>
                            </div>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Loading state for buttons
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = button.closest('form');
            if (form && form.checkValidity()) {
                button.disabled = true;
                const originalText = button.innerHTML;
                button.innerHTML = '<span class="loading-spinner me-2"></span>Processing...';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 10000);
            }
        });
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text, element) {
        navigator.clipboard.writeText(text).then(function() {
            // Show success feedback
            const originalText = element.textContent;
            element.textContent = 'Copied!';
            element.classList.add('text-success');
            
            setTimeout(() => {
                element.textContent = originalText;
                element.classList.remove('text-success');
            }, 2000);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
            alert('Failed to copy to clipboard');
        });
    };

    // Debounce function for search inputs
    window.debounce = function(func, wait, immediate) {
        var timeout;
        return function() {
            var context = this, args = arguments;
            var later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    };

    // Search functionality
    const searchInputs = document.querySelectorAll('[data-search-target]');
    searchInputs.forEach(input => {
        const targetSelector = input.getAttribute('data-search-target');
        const targets = document.querySelectorAll(targetSelector);
        
        const searchFunction = debounce(function() {
            const query = input.value.toLowerCase();
            targets.forEach(target => {
                const text = target.textContent.toLowerCase();
                if (text.includes(query)) {
                    target.style.display = '';
                } else {
                    target.style.display = 'none';
                }
            });
        }, 300);
        
        input.addEventListener('input', searchFunction);
    });

    // Progress bar animation
    window.animateProgressBar = function(progressBar, targetWidth, duration = 1000) {
        const startWidth = 0;
        const startTime = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentWidth = startWidth + (targetWidth - startWidth) * progress;
            progressBar.style.width = currentWidth + '%';
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    };

    // Notification system
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, duration);
    };

    // API helper functions
    window.apiRequest = async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API request error:', error);
            throw error;
        }
    };

    // Theme toggle functionality
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }
    }

    console.log('Visioneer application initialized successfully!');
});
