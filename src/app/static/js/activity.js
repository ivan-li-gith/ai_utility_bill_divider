// src/app/static/js/activity.js
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.paid-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const form = this.closest('form');
            const formData = new FormData(form);
            const month = this.dataset.month;
            const name = this.dataset.name;
            
            // Show loading spinner
            const statusIcon = document.getElementById(`status-${month}-${name}`);
            if (statusIcon) {
                statusIcon.innerHTML = '<div class="spinner-border spinner-border-sm text-primary" role="status"></div>';
            }
            
            formData.append('target_name', name);

            fetch(form.action, { 
                method: 'POST', 
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success checkmark
                    if (statusIcon) {
                        statusIcon.innerHTML = '<span class="text-success fw-bold">✓</span>';
                        setTimeout(() => { statusIcon.innerHTML = ''; }, 2000);
                    }
                    
                    // Update the cascading totals on the page dynamically
                    for (const [monthName, roommates] of Object.entries(data.updates)) {
                        for (const [roommateName, values] of Object.entries(roommates)) {
                            const totalElement = document.getElementById(`total-owed-${monthName}-${roommateName}`);
                            if (totalElement) { totalElement.innerText = `$${values.total}`; }
                            
                            const rolloverInput = document.getElementById(`rollover-input-${monthName}-${roommateName}`);
                            if (rolloverInput) { rolloverInput.value = values.rollover; }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error updating status:', error);
                if (statusIcon) {
                    statusIcon.innerHTML = '<span class="text-danger fw-bold">✗</span>';
                }
            });
        });
    });
});