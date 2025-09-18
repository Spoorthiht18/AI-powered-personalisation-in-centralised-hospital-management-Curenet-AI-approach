/**
 * CureNet AI main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize popovers
    initPopovers();
    
    // Handle form validations
    handleFormValidations();
    
    // Initialize location services
    initLocationServices();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Handle form validations
 */
function handleFormValidations() {
    // Get all forms with the class 'needs-validation'
    const forms = document.querySelectorAll('.needs-validation');
    
    // Add validation event listeners to each form
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize location services to get user's current location
 */
function initLocationServices() {
    const locationButtons = document.querySelectorAll('.get-location-btn');
    
    Array.from(locationButtons).forEach(button => {
        button.addEventListener('click', () => {
            if (navigator.geolocation) {
                button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Getting location...';
                button.disabled = true;
                
                navigator.geolocation.getCurrentPosition(
                    // Success callback
                    (position) => {
                        const latitude = position.coords.latitude;
                        const longitude = position.coords.longitude;
                        
                        // Update hidden inputs if they exist
                        const latInput = document.getElementById('latitude');
                        const longInput = document.getElementById('longitude');
                        
                        if (latInput) latInput.value = latitude;
                        if (longInput) longInput.value = longitude;
                        
                        // Trigger a custom event that other scripts can listen for
                        const locationEvent = new CustomEvent('locationUpdated', {
                            detail: { latitude, longitude }
                        });
                        document.dispatchEvent(locationEvent);
                        
                        // Update button text
                        button.innerHTML = '<i class="fas fa-check-circle me-2"></i> Location updated';
                        
                        // Re-enable after 2 seconds
                        setTimeout(() => {
                            button.innerHTML = '<i class="fas fa-location-dot me-2"></i> Update location';
                            button.disabled = false;
                        }, 2000);
                    },
                    // Error callback
                    (error) => {
                        console.error('Error getting location:', error);
                        
                        let errorMessage = 'Failed to get location';
                        switch (error.code) {
                            case error.PERMISSION_DENIED:
                                errorMessage = 'Location permission denied';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMessage = 'Location information unavailable';
                                break;
                            case error.TIMEOUT:
                                errorMessage = 'Location request timed out';
                                break;
                        }
                        
                        button.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> ' + errorMessage;
                        
                        // Re-enable after 2 seconds
                        setTimeout(() => {
                            button.innerHTML = '<i class="fas fa-location-dot me-2"></i> Get location';
                            button.disabled = false;
                        }, 2000);
                    }
                );
            } else {
                button.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> Geolocation not supported';
            }
        });
    });
}

/**
 * Get CSRF token from cookies for Django
 */
function getCsrfToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Format a date object into a human-readable string
 */
function formatDate(date) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString(undefined, options);
}

/**
 * Display a toast notification
 */
function showToast(message, type = 'success', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    // Create toast content
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toastEl);
    
    // Initialize the toast
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: duration
    });
    
    // Show the toast
    toast.show();
    
    // Remove from DOM after hiding
    toastEl.addEventListener('hidden.bs.toast', function() {
        toastEl.remove();
    });
}

/**
 * Function to set up and initialize video call
 */
function setupVideoCall(roomId, localVideoElement, remoteVideoElement) {
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsPath = `${wsScheme}://${window.location.host}/ws/video_call/${roomId}/`;

    const socket = new WebSocket(wsPath);
    let localStream;
    let peerConnection;

    const configuration = {
        iceServers: [
            {
                urls: 'stun:stun.l.google.com:19302'
            }
        ]
    };

    socket.onopen = () => {
        console.log('Video call WebSocket connected');
        showToast('Video call connected successfully!', 'success');
        
        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
            .then(stream => {
                localStream = stream;
                localVideoElement.srcObject = localStream;

                peerConnection = new RTCPeerConnection(configuration);
                peerConnection.addStream(localStream);

                peerConnection.onicecandidate = event => {
                    if (event.candidate) {
                        socket.send(JSON.stringify({
                            type: 'ice-candidate',
                            candidate: event.candidate
                        }));
                    }
                };

                peerConnection.onaddstream = event => {
                    remoteVideoElement.srcObject = event.stream;
                };

                // Create offer
                peerConnection.createOffer()
                    .then(offer => peerConnection.setLocalDescription(offer))
                    .then(() => {
                        socket.send(JSON.stringify({
                            type: 'offer',
                            offer: peerConnection.localDescription
                        }));
                    });
            })
            .catch(error => {
                console.error('Error accessing media devices:', error);
                showToast('Could not access camera or microphone', 'danger');
            });
    };

    socket.onmessage = event => {
        const message = JSON.parse(event.data);

        if (message.type === 'offer') {
            peerConnection.setRemoteDescription(new RTCSessionDescription(message.offer))
                .then(() => peerConnection.createAnswer())
                .then(answer => peerConnection.setLocalDescription(answer))
                .then(() => {
                    socket.send(JSON.stringify({
                        type: 'answer',
                        answer: peerConnection.localDescription
                    }));
                });
        } else if (message.type === 'answer') {
            peerConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
        } else if (message.type === 'ice-candidate') {
            peerConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
        }
    };

    socket.onclose = () => {
        console.log('Video call WebSocket disconnected');
        showToast('Video call disconnected.', 'warning');
    };

    socket.onerror = error => {
        console.error('WebSocket error:', error);
        showToast('An error occurred with the video call connection.', 'danger');
    };
}

/**
 * Handle offline/online status
 */
window.addEventListener('online', () => {
    showToast('You are back online!', 'success');
});

window.addEventListener('offline', () => {
    showToast('You are offline. Some features may not be available.', 'warning');
}); 