/**
 * Fix menu mobile - Résolution du problème de double-clic
 *
 * PROBLÈME RÉSOLU:
 * - Le menu se fermait AVANT que le clic du bouton ne soit traité
 * - L'utilisateur devait cliquer 2 fois (1 pour fermer le menu, 1 pour activer le bouton)
 *
 * SOLUTION:
 * - Pour les modals: fermer le menu via l'événement Bootstrap 'show.bs.modal'
 * - Pour les liens: laisser le navigateur démarrer la navigation PUIS fermer le menu
 */

// Modern hamburger menu toggle
function toggleMobileMenu() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');

    if (hamburger && mobileMenuOverlay) {
        // Toggle active classes
        hamburger.classList.toggle('active');
        mobileMenuOverlay.classList.toggle('active');

        // Prevent body scroll when menu is open
        if (mobileMenuOverlay.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }
}

// Setup mobile menu event listeners
document.addEventListener('DOMContentLoaded', function() {

    // ✅ FIX 1: Pour les liens de navigation classiques
    // Ne pas bloquer immédiatement, laisser le navigateur démarrer la navigation
    document.querySelectorAll('.mobile-menu-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
            if (mobileMenuOverlay && mobileMenuOverlay.classList.contains('active')) {
                // Ne pas empêcher la navigation
                // Fermer le menu après un tout petit délai pour laisser le clic se propager
                setTimeout(() => {
                    toggleMobileMenu();
                }, 10);
            }
        });
    });

    // ✅ FIX 2: Pour le bouton "Prendre RDV" avec modal Bootstrap
    // Utiliser l'événement Bootstrap 'show.bs.modal' au lieu d'écouter le clic
    const appointmentModal = document.getElementById('appointmentModal');
    if (appointmentModal) {
        // Fermer le menu mobile QUAND le modal commence à s'afficher
        appointmentModal.addEventListener('show.bs.modal', function () {
            const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
            const hamburger = document.querySelector('.hamburger');

            if (mobileMenuOverlay && mobileMenuOverlay.classList.contains('active')) {
                // Fermer proprement le menu mobile
                hamburger.classList.remove('active');
                mobileMenuOverlay.classList.remove('active');
                document.body.style.overflow = ''; // Restaurer le scroll
            }
        });
    }

    // ✅ FIX 3: Pour le bouton "Mon espace" (lien normal)
    const monEspaceButton = document.querySelector('.mobile-menu-btn-secondary');
    if (monEspaceButton) {
        monEspaceButton.addEventListener('click', function(e) {
            const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
            if (mobileMenuOverlay && mobileMenuOverlay.classList.contains('active')) {
                // Laisser le navigateur suivre le lien, puis fermer le menu
                setTimeout(() => {
                    toggleMobileMenu();
                }, 10);
            }
        });
    }

    // Close button click (onclick="toggleMobileMenu()" dans le HTML)

    // Fermer en cliquant sur l'overlay (fond noir)
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', function(e) {
            // Seulement si on clique sur l'overlay lui-même, pas ses enfants
            if (e.target === mobileMenuOverlay) {
                toggleMobileMenu();
            }
        });
    }
});
