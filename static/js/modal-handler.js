/**
 * Universal Modal Form Handler
 * Handles AJAX form submissions for all modal forms
 */

(function($) {
    'use strict';

    // Initialize when document is ready
    $(document).ready(function() {
        initializeModalForms();
        initializeModalToggles();
    });

    /**
     * Initialize all modal forms with AJAX submission
     */
    function initializeModalForms() {
        $('form[data-modal-form]').each(function() {
            const form = $(this);
            const modalId = form.closest('.modal').attr('id');
            
            form.on('submit', function(e) {
                e.preventDefault();
                submitModalForm(form, modalId);
            });
        });
    }

    /**
     * Initialize modal toggle buttons
     */
    function initializeModalToggles() {
        $('[data-modal-load]').on('click', function(e) {
            e.preventDefault();
            const url = $(this).data('modal-load');
            const targetModal = $(this).data('bs-target');
            
            if (url) {
                loadModalContent(url, targetModal);
            }
        });
    }

    /**
     * Submit form via AJAX
     */
    function submitModalForm(form, modalId) {
        const url = form.attr('action') || window.location.href;
        const method = form.attr('method') || 'POST';
        const formData = new FormData(form[0]);
        
        // Show loading state
        const submitBtn = form.find('button[type="submit"]');
        const originalText = submitBtn.html();
        submitBtn.html('<span class="spinner-border spinner-border-sm"></span> Saving...').prop('disabled', true);
        
        // Clear previous errors
        form.find('.is-invalid').removeClass('is-invalid');
        form.find('.invalid-feedback').remove();
        
        $.ajax({
            url: url,
            method: method,
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Show success message
                    showNotification(response.message || 'Saved successfully!', 'success');
                    
                    // Reload page or update table
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else {
                        setTimeout(function() {
                            location.reload();
                        }, 500);
                    }
                } else {
                    // Handle validation errors
                    handleFormErrors(form, response.errors);
                    submitBtn.html(originalText).prop('disabled', false);
                }
            },
            error: function(xhr) {
                let errorMessage = 'An error occurred. Please try again.';
                
                if (xhr.status === 400 && xhr.responseJSON) {
                    handleFormErrors(form, xhr.responseJSON.errors);
                    errorMessage = xhr.responseJSON.message || errorMessage;
                } else if (xhr.status === 403) {
                    errorMessage = 'Permission denied.';
                } else if (xhr.status === 500) {
                    errorMessage = 'Server error. Please contact support.';
                }
                
                showNotification(errorMessage, 'danger');
                submitBtn.html(originalText).prop('disabled', false);
            }
        });
    }

    /**
     * Load modal content via AJAX
     */
    function loadModalContent(url, targetModal) {
        const modalEl = $(targetModal);
        const modalBody = modalEl.find('.modal-body');
        
        modalBody.html('<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>');
        
        $.ajax({
            url: url,
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(html) {
                modalBody.html(html);
                initializeModalForms(); // Re-initialize forms in loaded content
            },
            error: function() {
                modalBody.html('<div class="alert alert-danger">Failed to load form. Please try again.</div>');
            }
        });
    }

    /**
     * Handle and display form validation errors
     */
    function handleFormErrors(form, errors) {
        if (!errors) return;
        
        $.each(errors, function(fieldName, errorMessages) {
            const field = form.find(`[name="${fieldName}"]`);
            if (field.length) {
                field.addClass('is-invalid');
                
                const errorHtml = Array.isArray(errorMessages) 
                    ? errorMessages.join('<br>')
                    : errorMessages;
                    
                field.after(`<div class="invalid-feedback d-block">${errorHtml}</div>`);
            }
        });
        
        // Scroll to first error
        const firstError = form.find('.is-invalid').first();
        if (firstError.length) {
            firstError[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }

    /**
     * Show notification toast
     */
    function showNotification(message, type) {
        // Remove existing notifications
        $('.notification-toast').remove();
        
        const iconMap = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        
        const icon = iconMap[type] || 'info-circle';
        
        const toast = $(`
            <div class="notification-toast position-fixed top-0 end-0 p-3" style="z-index: 9999;">
                <div class="toast show" role="alert">
                    <div class="toast-header bg-${type} text-white">
                        <i class="bi bi-${icon} me-2"></i>
                        <strong class="me-auto">Notification</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                    </div>
                    <div class="toast-body">
                        ${message}
                    </div>
                </div>
            </div>
        `);
        
        $('body').append(toast);
        
        // Auto-dismiss after 3 seconds
        setTimeout(function() {
            toast.fadeOut(function() {
                $(this).remove();
            });
        }, 3000);
    }

    // Export functions for external use
    window.ModalHandler = {
        submitForm: submitModalForm,
        loadContent: loadModalContent,
        showNotification: showNotification
    };

})(jQuery);
