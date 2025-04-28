document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-btn');
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    let deleteForm;

    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const targetButton = event.currentTarget;
            const deleteUrl = targetButton.getAttribute('data-delete-url');

            // Create form dynamically
            deleteForm = document.createElement('form');
            deleteForm.method = 'POST';
            deleteForm.action = deleteUrl; // Use the full URL from the button
            deleteForm.style.display = 'none'; // Hide the form

            // Add CSRF token if needed (assuming Flask-WTF is used)
            const csrfTokenInput = document.querySelector('input[name="csrf_token"]'); // Adjust selector if needed
            if (csrfTokenInput) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = csrfTokenInput.value;
                deleteForm.appendChild(csrfInput);
            }

            document.body.appendChild(deleteForm);
            deleteModal.style.display = 'flex';
        });
    });

    confirmDeleteBtn.addEventListener('click', () => {
        if (deleteForm) {
            deleteForm.submit();
        }
        deleteModal.style.display = 'none';
    });

    cancelDeleteBtn.addEventListener('click', () => {
        if (deleteForm) {
            document.body.removeChild(deleteForm); // Remove the form if cancelled
            deleteForm = null;
        }
        deleteModal.style.display = 'none';
    });

    window.addEventListener('click', (event) => {
        if (event.target == deleteModal) {
            if (deleteForm) {
                document.body.removeChild(deleteForm);
                deleteForm = null;
            }
            deleteModal.style.display = 'none';
        }
    });

    console.log("Records JavaScript loaded and modal listeners attached.");
}); 