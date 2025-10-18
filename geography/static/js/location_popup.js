// Location popup functionality
class LocationPopup {
    constructor() {
        this.popupShown = sessionStorage.getItem('locationPopupShown') === 'true';
        this.init();
    }
    
    init() {
        // Only show popup if user is authenticated and hasn't seen it this session
        if (this.shouldShowPopup()) {
            this.showLocationPopup();
        }
    }
    
    shouldShowPopup() {
        // Check if user is authenticated (you can customize this logic)
        const isAuthenticated = document.body.classList.contains('user-authenticated') || 
                               document.querySelector('[data-user-authenticated="true"]');
        
        return isAuthenticated && !this.popupShown;
    }
    
    showLocationPopup() {
        // Create popup modal
        const modal = document.createElement('div');
        modal.id = 'locationModal';
        modal.className = 'modal fade';
        modal.setAttribute('data-bs-backdrop', 'static');
        modal.setAttribute('data-bs-keyboard', 'false');
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-map-marker-alt"></i>
                            Enable Location Services
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-4">
                            <i class="fas fa-map-marked-alt fa-3x text-primary mb-3"></i>
                            <h6>Help us show you trending movies in your area!</h6>
                            <p class="text-muted mb-0">
                                We'd like to know your location to show you which movies are popular in your region. 
                                This helps you discover what's trending locally.
                            </p>
                        </div>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle"></i>
                            <small>Your location data is only used to show regional movie trends and is not shared with third parties.</small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="skipLocation">
                            <i class="fas fa-times"></i> Skip for now
                        </button>
                        <button type="button" class="btn btn-primary" id="enableLocation">
                            <i class="fas fa-location-arrow"></i> Enable Location
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Handle button clicks
        document.getElementById('enableLocation').addEventListener('click', () => {
            this.requestLocation();
        });
        
        document.getElementById('skipLocation').addEventListener('click', () => {
            this.skipLocation();
            bootstrapModal.hide();
        });
        
        // Handle modal close
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
    
    requestLocation() {
        const enableBtn = document.getElementById('enableLocation');
        const skipBtn = document.getElementById('skipLocation');
        
        // Update button state
        enableBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
        enableBtn.disabled = true;
        skipBtn.disabled = true;
        
        // Check if geolocation is supported
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by this browser.');
            return;
        }
        
        // Request location
        navigator.geolocation.getCurrentPosition(
            (position) => {
                this.handleLocationSuccess(position.coords);
            },
            (error) => {
                this.handleLocationError(error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000 // 5 minutes
            }
        );
    }
    
    handleLocationSuccess(coords) {
        // Send location data to server
        fetch('/geography/api/set-location/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                latitude: coords.latitude,
                longitude: coords.longitude,
                accuracy: coords.accuracy
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showSuccess(data.region_name);
            } else {
                this.showError(data.message || 'Failed to set location.');
            }
        })
        .catch(error => {
            console.error('Error setting location:', error);
            this.showError('Failed to save location. Please try again.');
        });
    }
    
    handleLocationError(error) {
        let message = 'Unable to get your location. ';
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message += 'Please allow location access and try again.';
                break;
            case error.POSITION_UNAVAILABLE:
                message += 'Location information is unavailable.';
                break;
            case error.TIMEOUT:
                message += 'Location request timed out.';
                break;
            default:
                message += 'An unknown error occurred.';
                break;
        }
        
        this.showError(message);
    }
    
    showSuccess(regionName) {
        const modalBody = document.querySelector('#locationModal .modal-body');
        modalBody.innerHTML = `
            <div class="text-center">
                <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                <h6 class="text-success">Location Set Successfully!</h6>
                <p class="mb-0">You're now connected to the <strong>${regionName}</strong> region.</p>
                <p class="text-muted small mt-2">You can now see trending movies in your area!</p>
            </div>
        `;
        
        // Hide buttons and show close button
        document.querySelector('#locationModal .modal-footer').innerHTML = `
            <button type="button" class="btn btn-success" data-bs-dismiss="modal">
                <i class="fas fa-check"></i> Great!
            </button>
        `;
        
        // Mark popup as shown
        this.markPopupShown();
        
        // Auto close after 2 seconds
        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('locationModal'));
            modal.hide();
        }, 2000);
    }
    
    showError(message) {
        const modalBody = document.querySelector('#locationModal .modal-body');
        modalBody.innerHTML = `
            <div class="text-center">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <h6 class="text-warning">Location Access Failed</h6>
                <p class="text-muted">${message}</p>
            </div>
        `;
        
        // Reset buttons
        document.querySelector('#locationModal .modal-footer').innerHTML = `
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="fas fa-times"></i> Skip for now
            </button>
            <button type="button" class="btn btn-primary" onclick="location.reload()">
                <i class="fas fa-redo"></i> Try Again
            </button>
        `;
    }
    
    skipLocation() {
        this.markPopupShown();
        console.log('User skipped location setting');
    }
    
    markPopupShown() {
        sessionStorage.setItem('locationPopupShown', 'true');
        this.popupShown = true;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
}

// Initialize location popup when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new LocationPopup();
});
