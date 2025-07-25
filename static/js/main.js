// Bu JavaScript dosyası hasta formu üzerindeki görüntü önizleme, sonuç yazdırma ve kayıt silme modalı gibi temel etkileşimleri yönetir.
// Fonksiyonlar:
// 1) X-ray görüntüsü seçildiğinde hasta formunda canlı önizleme oluşturur.
// 2) Sonuç sayfasında 'Yazdır' butonuna basıldığında tarayıcı yazdırma penceresini açar.
// 3) Her bir kayıt kartındaki silme butonu modalını tetikler ve onaylandığında POST isteği göndererek kaydı siler.

document.addEventListener('DOMContentLoaded', function() { 
    const fileInput = document.getElementById('xray_image');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const fileReader = new FileReader();
            fileReader.onload = function() {
                const preview = document.createElement('div');
                preview.className = 'image-preview';
                preview.innerHTML = `<img src="${fileReader.result}" alt="X-Ray Preview">`;
                
                const existingPreview = document.querySelector('.image-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                fileInput.parentNode.insertBefore(preview, fileInput.nextSibling);
            };
            fileReader.readAsDataURL(event.target.files[0]);
        });
    }
    
    const printButton = document.getElementById('printResults');
    if (printButton) {
        printButton.addEventListener('click', function() {
            window.print();
        });
    }

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
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/delete_record/${recordIdToDelete}`;

                document.body.appendChild(form);
                form.submit();
            }
            if (deleteModal) {
                deleteModal.style.display = 'none';
            }
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target == deleteModal) {
            deleteModal.style.display = 'none';
            recordIdToDelete = null;
        }
    });
});
