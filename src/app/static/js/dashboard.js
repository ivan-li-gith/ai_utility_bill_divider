// src/app/static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    
    const notifyModal = document.getElementById('notifyModal');
    
    if (notifyModal) {
        notifyModal.addEventListener('show.bs.modal', function (event) {
            // 1. Button that triggered the modal
            const button = event.relatedTarget;
            
            // 2. Extract info from data-* attributes
            const name = button.getAttribute('data-name');
            const email = button.getAttribute('data-email');
            const total = button.getAttribute('data-total');
            const utilities = button.getAttribute('data-utilities');
            const expenses = button.getAttribute('data-expenses');
            const subscriptions = button.getAttribute('data-subscriptions');
            
            // 3. Update the hidden inputs for the backend
            document.getElementById('notify-name').value = name;
            document.getElementById('notify-email').value = email;
            document.getElementById('notify-total').value = total;
            document.getElementById('notify-utilities').value = utilities;
            document.getElementById('notify-expenses').value = expenses;
            document.getElementById('notify-subscriptions').value = subscriptions;
            
            // 4. Update the visible text so the user knows who they are emailing
            document.getElementById('notify-display-name').textContent = name;
            document.getElementById('notify-display-total').textContent = '$' + parseFloat(total).toFixed(2);
        });
    }
});