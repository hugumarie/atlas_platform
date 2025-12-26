// JavaScript principal pour la plateforme Patrimoine Pro

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation générale
    initializeTooltips();
    initializePopovers();
    setupFormValidation();
    
    // Animations au scroll
    setupScrollAnimations();
});

/**
 * Initialise les tooltips Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialise les popovers Bootstrap
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Configuration de la validation des formulaires
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Animations au défilement
 */
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);

    // Observer les cartes et sections
    const animatedElements = document.querySelectorAll('.card, .stat-card, section');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Fonctions utilitaires pour les graphiques
 */
const ChartUtils = {
    // Configuration par défaut des couleurs
    colors: {
        primary: '#0066cc',
        secondary: '#28a745',
        warning: '#ffc107',
        danger: '#dc3545',
        info: '#17a2b8',
        success: '#28a745'
    },

    // Palette de couleurs pour les graphiques en secteurs
    pieColors: [
        '#FF6384',
        '#36A2EB', 
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#C9CBCF'
    ],

    /**
     * Crée un graphique en secteurs
     */
    createPieChart: function(ctx, data, options = {}) {
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value.toLocaleString()}€ (${percentage}%)`;
                        }
                    }
                }
            }
        };

        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: this.pieColors.slice(0, data.labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: { ...defaultOptions, ...options }
        });
    },

    /**
     * Crée un graphique en barres
     */
    createBarChart: function(ctx, data, options = {}) {
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + '€';
                        }
                    }
                }
            }
        };

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.values,
                    backgroundColor: this.colors.primary,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: { ...defaultOptions, ...options }
        });
    }
};

/**
 * Utilitaires pour le formatage
 */
const FormatUtils = {
    /**
     * Formate un nombre en euros
     */
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },

    /**
     * Formate un pourcentage
     */
    formatPercent: function(value, decimals = 1) {
        return `${value.toFixed(decimals)}%`;
    },

    /**
     * Formate une date
     */
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    }
};

/**
 * Gestionnaire des notifications toast
 */
const ToastManager = {
    /**
     * Affiche une notification toast
     */
    show: function(message, type = 'info', duration = 5000) {
        const toastContainer = this.getOrCreateContainer();
        const toast = this.createToast(message, type);
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
        
        bsToast.show();
        
        // Supprime le toast après affichage
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    },

    /**
     * Obtient ou crée le conteneur des toasts
     */
    getOrCreateContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    /**
     * Crée un élément toast
     */
    createToast: function(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        return toast;
    }
};

/**
 * Utilitaires AJAX
 */
const AjaxUtils = {
    /**
     * Requête GET
     */
    get: function(url, callback, errorCallback) {
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => {
            console.error('Erreur:', error);
            if (errorCallback) errorCallback(error);
        });
    },

    /**
     * Requête POST
     */
    post: function(url, data, callback, errorCallback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => {
            console.error('Erreur:', error);
            if (errorCallback) errorCallback(error);
        });
    }
};

/**
 * Gestionnaire de loading spinner
 */
const LoadingManager = {
    /**
     * Affiche un spinner de chargement
     */
    show: function(container) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.id = 'loading-spinner';
        
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (container) {
            container.appendChild(spinner);
        }
    },

    /**
     * Cache le spinner de chargement
     */
    hide: function() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
};

// Export des utilitaires pour utilisation globale
window.ChartUtils = ChartUtils;
window.FormatUtils = FormatUtils;
window.ToastManager = ToastManager;
window.AjaxUtils = AjaxUtils;
window.LoadingManager = LoadingManager;