/**
 * Modal Forms Library - Reusable AJAX Form Handler
 * PhysioNutrition Clinic Management System
 * 
 * This library provides reusable functions for handling modal forms
 * with AJAX submissions, validation, and error handling.
 */

// ==================== CORE AJAX FORM HANDLER ====================

/**
 * Submit a form via AJAX from within a modal
 * @param {string} formId - ID of the form element
 * @param {string} modalId - ID of the modal element
 * @param {function} onSuccess - Optional callback function on success
 * @param {function} onError - Optional callback function on error
 */
function submitModalForm(formId, modalId, onSuccess, onError) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Clear previous errors
    clearValidationErrors(formId);
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
        
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Show success message
            showToast(data.message, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
            if (modal) {
                modal.hide();
            }
            
            // Call custom success callback if provided
            if (onSuccess && typeof onSuccess === 'function') {
                onSuccess(data);
            } else if (data.redirect_url) {
                // Default: redirect to the URL provided
                window.location.href = data.redirect_url;
            } else {
                // Default: reload the page
                window.location.reload();
            }
        } else {
            // Show field errors
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
            
            // Call custom error callback if provided
            if (onError && typeof onError === 'function') {
                onError(data);
            }
        }
    })
    .catch(error => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
        
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
        
        if (onError && typeof onError === 'function') {
            onError(error);
        }
    });
}

// ==================== VALIDATION HELPERS ====================

/**
 * Clear all validation errors from a form
 * @param {string} formId - ID of the form element
 */
function clearValidationErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.querySelectorAll('.is-invalid').forEach(element => {
        element.classList.remove('is-invalid');
    });
    
    form.querySelectorAll('.invalid-feedback').forEach(element => {
        element.remove();
    });
}

/**
 * Display validation errors for form fields
 * @param {object} errors - Object with field names as keys and error arrays as values
 * @param {string} formId - ID of the form element
 */
function displayFormErrors(errors, formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    for (const [fieldName, errorMessages] of Object.entries(errors)) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('is-invalid');
            
            // Remove existing error message
            const existingError = field.parentNode.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            errorDiv.textContent = Array.isArray(errorMessages) 
                ? errorMessages.join(' ') 
                : errorMessages;
            
            // Insert after the field or its parent form-group
            const formGroup = field.closest('.mb-3, .form-group');
            if (formGroup) {
                formGroup.appendChild(errorDiv);
            } else {
                field.parentNode.appendChild(errorDiv);
            }
        }
    }
    
    // Scroll to first error
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// ==================== TOAST NOTIFICATIONS ====================

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast: 'success', 'error', 'warning', 'info'
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Map type to Bootstrap color classes
    const colorMap = {
        'success': 'bg-success text-white',
        'error': 'bg-danger text-white',
        'warning': 'bg-warning text-dark',
        'info': 'bg-info text-white'
    };
    
    const iconMap = {
        'success': 'bi-check-circle-fill',
        'error': 'bi-exclamation-triangle-fill',
        'warning': 'bi-exclamation-circle-fill',
        'info': 'bi-info-circle-fill'
    };
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center ${colorMap[type] || 'bg-secondary text-white'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="bi ${iconMap[type] || 'bi-info-circle-fill'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast using Bootstrap
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// ==================== MODAL HELPERS ====================

/**
 * Reset form when modal is closed
 * @param {string} modalId - ID of the modal element
 * @param {string} formId - ID of the form element
 */
function setupModalReset(modalId, formId) {
    const modal = document.getElementById(modalId);
    const form = document.getElementById(formId);
    
    if (modal && form) {
        modal.addEventListener('hidden.bs.modal', function() {
            form.reset();
            clearValidationErrors(formId);
        });
    }
}

/**
 * Load data into form fields
 * @param {string} formId - ID of the form element
 * @param {object} data - Object with field names as keys and values
 */
function loadFormData(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    for (const [fieldName, value] of Object.entries(data)) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            if (field.type === 'checkbox') {
                field.checked = value;
            } else if (field.type === 'radio') {
                const radio = form.querySelector(`[name="${fieldName}"][value="${value}"]`);
                if (radio) radio.checked = true;
            } else {
                field.value = value;
            }
        }
    }
}

/**
 * Enable/disable form fields based on a condition
 * @param {string} formId - ID of the form element
 * @param {boolean} disabled - Whether to disable fields
 */
function toggleFormFields(formId, disabled) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const fields = form.querySelectorAll('input, select, textarea, button');
    fields.forEach(field => {
        field.disabled = disabled;
    });
}

// ==================== CONFIRMATION DIALOGS ====================

/**
 * Show confirmation dialog before action
 * @param {string} message - Confirmation message
 * @param {function} onConfirm - Callback function if confirmed
 * @param {function} onCancel - Optional callback function if cancelled
 */
function confirmAction(message, onConfirm, onCancel) {
    if (confirm(message)) {
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
    } else {
        if (onCancel && typeof onCancel === 'function') {
            onCancel();
        }
    }
}

/**
 * Show Bootstrap confirmation modal
 * @param {string} title - Modal title
 * @param {string} message - Confirmation message
 * @param {function} onConfirm - Callback function if confirmed
 * @param {object} options - Optional settings: confirmText, cancelText, confirmClass
 */
function showConfirmModal(title, message, onConfirm, options = {}) {
    const confirmText = options.confirmText || 'Confirm';
    const cancelText = options.cancelText || 'Cancel';
    const confirmClass = options.confirmClass || 'btn-primary';
    
    // Create modal HTML
    const modalId = 'confirmModal-' + Date.now();
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">${cancelText}</button>
                        <button type="button" class="btn ${confirmClass}" id="${modalId}-confirm">${confirmText}</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = modalHtml;
    document.body.appendChild(modalContainer);
    
    const modalElement = document.getElementById(modalId);
    const confirmButton = document.getElementById(`${modalId}-confirm`);
    
    // Setup confirm button
    confirmButton.addEventListener('click', function() {
        if (onConfirm && typeof onConfirm === 'function') {
            onConfirm();
        }
        const modal = bootstrap.Modal.getInstance(modalElement);
        modal.hide();
    });
    
    // Show modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Remove modal from DOM after it's hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        modalContainer.remove();
    });
}

// ==================== FORM FIELD HELPERS ====================

/**
 * Setup dependent field enabling/disabling
 * @param {string} triggerFieldId - ID of the trigger field
 * @param {array} dependentFieldIds - Array of dependent field IDs
 */
function setupDependentFields(triggerFieldId, dependentFieldIds) {
    const triggerField = document.getElementById(triggerFieldId);
    if (!triggerField) return;
    
    const updateDependents = () => {
        const isEnabled = triggerField.type === 'checkbox' 
            ? triggerField.checked 
            : triggerField.value !== '';
        
        dependentFieldIds.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.disabled = !isEnabled;
                if (!isEnabled) {
                    field.value = '';
                }
            }
        });
    };
    
    // Initial state
    updateDependents();
    
    // Update on change
    triggerField.addEventListener('change', updateDependents);
    triggerField.addEventListener('input', updateDependents);
}

/**
 * Setup form auto-save
 * @param {string} formId - ID of the form element
 * @param {string} storageKey - LocalStorage key for saving data
 * @param {number} debounceMs - Debounce delay in milliseconds
 */
function setupFormAutoSave(formId, storageKey, debounceMs = 1000) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    let saveTimeout;
    
    const saveFormData = () => {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
        localStorage.setItem(storageKey, JSON.stringify(data));
    };
    
    const debouncedSave = () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(saveFormData, debounceMs);
    };
    
    // Save on input change
    form.addEventListener('input', debouncedSave);
    form.addEventListener('change', debouncedSave);
    
    // Load saved data on page load
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            loadFormData(formId, data);
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }
    
    // Clear saved data on successful submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

// ==================== EXPORT FUNCTIONS ====================

// Make functions available globally
window.modalForms = {
    submitModalForm,
    clearValidationErrors,
    displayFormErrors,
    showToast,
    setupModalReset,
    loadFormData,
    toggleFormFields,
    confirmAction,
    showConfirmModal,
    setupDependentFields,
    setupFormAutoSave
};
