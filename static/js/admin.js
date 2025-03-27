document.addEventListener('DOMContentLoaded', function () {
    const intentsTableBody = document.querySelector('#intentsTable tbody');
    const editModal = document.getElementById('editModal');
    const editIntentForm = document.getElementById('editIntentForm');
    const closeModal = document.querySelector('.close');
    const cancelBtn = document.querySelector('.cancel-btn');

    // Fungsi untuk mendapatkan semua intents dari API
    async function fetchIntents() {
        try {
            const response = await fetch('/intents');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const intents = await response.json();
            renderIntents(intents);
        } catch (error) {
            console.error('Error fetching intents:', error);
            alert('Gagal memuat data. Silakan coba lagi.');
        }
    }

    // Fungsi untuk merender intents ke dalam tabel
    function renderIntents(intents) {
        intentsTableBody.innerHTML = '';
        intents.forEach(intent => {
            const row = document.createElement('tr');

            const tagCell = document.createElement('td');
            tagCell.textContent = intent.tag;
            row.appendChild(tagCell);

            const patternsCell = document.createElement('td');
            patternsCell.textContent = intent.patterns.length > 0 ? intent.patterns[0] : 'Tidak ada pattern';
            row.appendChild(patternsCell);

            const responsesCell = document.createElement('td');
            responsesCell.textContent = intent.responses.length > 0 ? intent.responses[0] : 'Tidak ada respon';
            row.appendChild(responsesCell);

            const actionsCell = document.createElement('td');
            const editButton = document.createElement('button');
            editButton.textContent = 'Edit Respon';
            editButton.classList.add('edit');
            editButton.addEventListener('click', () => openEditModal(intent));

            actionsCell.appendChild(editButton);
            row.appendChild(actionsCell);

            intentsTableBody.appendChild(row);
        });
    }

    // Fungsi untuk membuka modal edit
    function openEditModal(intent) {
        document.getElementById('editTag').value = intent.tag;
        document.getElementById('displayTag').textContent = intent.tag;
        
        const patternsText = intent.patterns.join('\n');
        document.getElementById('displayPatterns').textContent = patternsText;
        
        document.getElementById('editResponses').value = intent.responses.join('\n');
        editModal.style.display = 'block';
    }

    // Fungsi untuk menutup modal edit
    function closeEditModal() {
        editModal.style.display = 'none';
    }

    closeModal.onclick = closeEditModal;
    cancelBtn.onclick = closeEditModal;

    window.onclick = function (event) {
        if (event.target === editModal) {
            closeEditModal();
        }
    };

    // Event listener untuk form edit intent
    editIntentForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const tag = document.getElementById('editTag').value;
        const rawResponses = document.getElementById('editResponses').value;

        const responses = rawResponses.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        try {
            const response = await fetch(`/intents/${tag}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ responses })
            });

            if (!response.ok) {
                throw new Error('Update gagal');
            }

            fetchIntents();
            closeEditModal();
            alert('Respon berhasil diperbarui!');
        } catch (error) {
            console.error('Error updating intent:', error);
            alert('Gagal memperbarui respon. Silakan coba lagi.');
        }
    });

    // Fetch intents saat halaman dimuat
    fetchIntents();
});