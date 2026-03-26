document.addEventListener('DOMContentLoaded', function() {
    const notifyModal = document.getElementById('notifyModal');
    
    if (notifyModal) {
        notifyModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            
            // extract info from data
            const name = button.getAttribute('data-name');
            const email = button.getAttribute('data-email');
            const total = button.getAttribute('data-total');
            const utilities = button.getAttribute('data-utilities');
            const expenses = button.getAttribute('data-expenses');
            const subscriptions = button.getAttribute('data-subscriptions');
            
            // update the hidden inputs
            document.getElementById('notify-name').value = name;
            document.getElementById('notify-email').value = email;
            document.getElementById('notify-total').value = total;
            document.getElementById('notify-utilities').value = utilities;
            document.getElementById('notify-expenses').value = expenses;
            document.getElementById('notify-subscriptions').value = subscriptions;
            
            // update the visible text
            document.getElementById('notify-display-name').textContent = name;
            document.getElementById('notify-display-total').textContent = '$' + parseFloat(total).toFixed(2);
        });
    }
});