/**
 * Pharmacy Modal Forms JavaScript Library
 * Handles all pharmacy-related modal operations with AJAX submissions
 */

// ============================================================================
// MEDICATION MANAGEMENT
// ============================================================================

function submitMedicationForm(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    clearValidationErrors(formId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Redirect if URL provided
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// ============================================================================
// BATCH MANAGEMENT
// ============================================================================

function submitBatchForm(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    clearValidationErrors(formId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// ============================================================================
// PRESCRIPTION MANAGEMENT
// ============================================================================

function submitPrescriptionForm(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    clearValidationErrors(formId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

function dispensePrescription(prescriptionId) {
    if (!confirm('Are you sure you want to dispense this prescription?')) {
        return;
    }
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = `/pharmacy/ajax/prescription/${prescriptionId}/dispense/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while dispensing the prescription.', 'error');
    });
}

// ============================================================================
// STOCK ADJUSTMENT
// ============================================================================

function submitStockAdjustmentForm(formId, batchId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = `/pharmacy/ajax/stock/adjustment/${batchId}/`;
    
    clearValidationErrors(formId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// ============================================================================
// SUPPLIER MANAGEMENT
// ============================================================================

function submitSupplierForm(formId, url) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    clearValidationErrors(formId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            const modalElement = form.closest('.modal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                location.reload();
            }
        } else {
            displayFormErrors(data.errors, formId);
            if (data.message) {
                showToast(data.message, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred. Please try again.', 'error');
    });
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

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

function displayFormErrors(errors, formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    for (const [fieldName, errorMessages] of Object.entries(errors)) {
        const field = form.querySelector(`[name=${fieldName}]`);
        if (field) {
            field.classList.add('is-invalid');
            
            // Remove existing error message
            const existingError = field.parentNode.querySelector('.invalid-feedback');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = Array.isArray(errorMessages) ? errorMessages.join(' ') : errorMessages;
            field.parentNode.appendChild(errorDiv);
        }
    }
    
    // Scroll to first error
    const firstError = form.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'bg-success' : type === 'error' ? 'bg-danger' : 'bg-info';
    
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white">
                <strong class="me-auto">${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

// ============================================================================
// MODAL RESET HANDLERS
// ============================================================================

// Reset form when modal is hidden
document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
                clearValidationErrors(form.id);
            }
        });
    });
});
