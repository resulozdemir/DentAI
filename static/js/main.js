// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Add JavaScript functionality here
    
    // Example: Preview uploaded image
    const fileInput = document.getElementById('xray_image');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const fileReader = new FileReader();
            fileReader.onload = function() {
                const preview = document.createElement('div');
                preview.className = 'image-preview';
                preview.innerHTML = `<img src="${fileReader.result}" alt="X-Ray Preview">`;
                
                // Remove any existing preview
                const existingPreview = document.querySelector('.image-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                // Insert preview after the file input
                fileInput.parentNode.insertBefore(preview, fileInput.nextSibling);
            };
            fileReader.readAsDataURL(event.target.files[0]);
        });
    }
    
    // Print results button
    const printButton = document.getElementById('printResults');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }

    // Modal işlemleri (varsa)
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteButton = document.getElementById('confirmDelete');
    const cancelDeleteButton = document.getElementById('cancelDelete');
    let recordIdToDelete = null;

    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            recordIdToDelete = this.getAttribute('data-record-id');
            if (deleteModal) {
                deleteModal.style.display = 'block';
            }
        });
    });

    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', function() {
            if (deleteModal) {
                deleteModal.style.display = 'none';
            }
            recordIdToDelete = null;
        });
    }

    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', function() {
            if (recordIdToDelete) {
                // Silme işlemini tetikleyecek formu oluştur veya isteği gönder
                const form = document.createElement('form');
                form.method = 'POST';
                // URL'yi dinamik olarak oluştur
                form.action = `/delete_record/${recordIdToDelete}`;

                document.body.appendChild(form);
                form.submit();
            }
            if (deleteModal) {
                deleteModal.style.display = 'none';
            }
        });
    }

    // Modal dışına tıklanınca kapatma
    window.addEventListener('click', function(event) {
        if (event.target == deleteModal) {
            deleteModal.style.display = 'none';
            recordIdToDelete = null;
        }
    });

    // Diğer JavaScript kodları buraya eklenebilir
    console.log("Main JavaScript dosyası yüklendi.");
});
