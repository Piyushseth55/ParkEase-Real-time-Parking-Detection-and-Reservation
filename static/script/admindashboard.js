
    document.getElementById('confirmButton').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('.row-checkbox:checked');
        const idsToRemove = Array.from(checkboxes).map(cb => cb.getAttribute('data-id'));
        
        if (idsToRemove.length === 0) {
            alert('No rows selected for removal!');
            return;
        }
        
        // Send the IDs to the server
        fetch('/confirm_checked_rows', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: idsToRemove }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selected rows removed successfully!');
                location.reload(); // Reload the page to reflect changes
            } else {
                alert('Error removing rows.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error removing rows.');
        });
    });


    document.getElementById('removeButton').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('.row-checkbox:checked');
        const idsToRemove = Array.from(checkboxes).map(cb => cb.getAttribute('data-id'));
        
        if (idsToRemove.length === 0) {
            alert('No rows selected for removal!');
            return;
        }
        
        // Send the IDs to the server
        fetch('/remove_checked_rows', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ ids: idsToRemove }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Selected rows removed successfully!');
                location.reload(); // Reload the page to reflect changes
            } else {
                alert('Error removing rows.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('Error removing rows.');
        });
    });