function sortByDay(jadwals) {
    const dayOrder = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU', 'MINGGU'];
    
    return jadwals.sort((a, b) => {
        const dayA = a.hari.toUpperCase();
        const dayB = b.hari.toUpperCase();
        
        if (dayOrder.indexOf(dayA) < dayOrder.indexOf(dayB)) return -1;
        if (dayOrder.indexOf(dayA) > dayOrder.indexOf(dayB)) return 1;
        
        if (a.jam_mulai < b.jam_mulai) return -1;
        if (a.jam_mulai > b.jam_mulai) return 1;
        
        if (a.semester < b.semester) return -1;
        if (a.semester > b.semester) return 1;
        
        return 0;
    });
}

async function loadJadwal(searchQuery = '', semesterFilter = '') {
    try {
        const semesterRes = await fetch('/get-semester');
        const semesterData = await semesterRes.json();
        
        let url = '/jadwal';
        if (searchQuery || semesterFilter) {
            const params = new URLSearchParams();
            if (searchQuery) params.append('search', searchQuery);
            if (semesterFilter) params.append('semester', semesterFilter);
            url += `?${params.toString()}`;
        }
        
        const res = await fetch(url);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        let jadwals = await res.json();
        
        jadwals = sortByDay(jadwals);
        
        const tbody = document.querySelector("#jadwalTable tbody");
        tbody.innerHTML = '';

        if (jadwals.length === 0) {
            let message = `Tidak ada data jadwal kuliah untuk semester ${semesterData.semester_type}`;
            if (semesterFilter) message += ` (Semester ${semesterFilter})`;
            if (searchQuery) message += ` dengan kriteria pencarian "${searchQuery}"`;
            message += '.';
            tbody.innerHTML = `<tr><td colspan="11" class="text-center">${message}</td></tr>`;
            return;
        }

        jadwals.forEach(j => {
            tbody.innerHTML += `
                <tr>
                    <td>${j.hari}</td>
                    <td>${j.semester}</td>
                    <td>${j.jurusan}</td>
                    <td>${j.kelas}</td>
                    <td>${j.mata_kuliah}</td>
                    <td>${j.jam_mulai}</td>
                    <td>${j.jam_selesai}</td>
                    <td>${j.dosen}</td>
                    <td>${j.ruangan}</td>
                    <td>${j.semester_type}</td>
                    <td>
                        <button class="btn btn-sm btn-warning" onclick="editJadwal(${j.id_jadwal})">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteJadwal(${j.id_jadwal})">Hapus</button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error('Error loading jadwal:', error);
        alert('Gagal memuat jadwal: ' + error.message);
    }
}

async function editJadwal(id) {
    try {
        const res = await fetch(`/jadwal/${id}`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();

        document.getElementById("form-title").innerText = "Edit Jadwal";
        document.getElementById("id_jadwal").value = data.id_jadwal;
        document.getElementById("hari").value = data.hari;
        document.getElementById("semester").value = data.semester;
        document.getElementById("jurusan").value = data.jurusan;
        document.getElementById("kelas").value = data.kelas;
        document.getElementById("mata_kuliah").value = data.mata_kuliah;
        document.getElementById("jam_mulai").value = data.jam_mulai;
        document.getElementById("jam_selesai").value = data.jam_selesai;
        document.getElementById("dosen").value = data.dosen;
        document.getElementById("ruangan").value = data.ruangan;
    } catch (error) {
        console.error('Error fetching jadwal for edit:', error);
        alert('Gagal mengambil data jadwal untuk diedit: ' + error.message);
    }
}

async function deleteJadwal(id) {
    if (confirm("Apakah Anda yakin ingin menghapus jadwal ini?")) {
        try {
            const res = await fetch(`/jadwal/${id}`, { method: 'DELETE' });
            const responseData = await res.json();
            if (!res.ok) {
                throw new Error(responseData.error || `HTTP error! status: ${res.status}`);
            }
            alert(responseData.message);
            loadJadwal();
        } catch (error) {
            console.error('Error deleting jadwal:', error);
            alert('Gagal menghapus jadwal: ' + error.message);
        }
    }
}

document.getElementById("jadwalForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const id = document.getElementById("id_jadwal").value;
    const data = {
        hari: document.getElementById("hari").value,
        semester: parseInt(document.getElementById("semester").value),
        jurusan: document.getElementById("jurusan").value,
        kelas: document.getElementById("kelas").value,
        mata_kuliah: document.getElementById("mata_kuliah").value,
        jam_mulai: document.getElementById("jam_mulai").value,
        jam_selesai: document.getElementById("jam_selesai").value,
        dosen: document.getElementById("dosen").value,
        ruangan: document.getElementById("ruangan").value,
        semester_type: document.getElementById("semesterSwitch").checked ? 'genap' : 'ganjil'
    };

    if (isNaN(data.semester) || data.semester < 1 || data.semester > 8) {
        alert("Semester harus angka antara 1 sampai 8.");
        return;
    }
    
    if (!['Reguler', 'Ekstensi', 'Reguler dan Ekstensi'].includes(data.kelas)) {
        alert("Kelas hanya boleh 'Reguler', 'Ekstensi', atau 'Reguler dan Ekstensi'.");
        return;
    }

    const url = id ? `/jadwal/${id}` : '/jadwal';
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const responseData = await res.json();
        if (!res.ok) {
            throw new Error(responseData.error || `HTTP error! status: ${res.status}`);
        }
        
        alert(responseData.message);
        this.reset();
        document.getElementById("id_jadwal").value = '';
        document.getElementById("form-title").innerText = "Tambah Jadwal";
        loadJadwal();
    } catch (error) {
        console.error('Error saving jadwal:', error);
        alert('Gagal menyimpan jadwal: ' + error.message);
    }
});

document.getElementById("cancelEdit").addEventListener("click", function() {
    document.getElementById("jadwalForm").reset();
    document.getElementById("id_jadwal").value = '';
    document.getElementById("form-title").innerText = "Tambah Jadwal";
});

async function checkSemester() {
    try {
        const res = await fetch('/get-semester');
        const data = await res.json();
        const switchElement = document.getElementById('semesterSwitch');
        const labelElement = document.getElementById('semesterLabel');
        
        if (data.semester_type === 'ganjil') {
            switchElement.checked = false;
            labelElement.textContent = 'Semester Ganjil';
        } else {
            switchElement.checked = true;
            labelElement.textContent = 'Semester Genap';
        }
    } catch (error) {
        console.error('Error checking semester:', error);
    }
}

document.getElementById('semesterSwitch').addEventListener('change', async function() {
    const semesterType = this.checked ? 'genap' : 'ganjil';
    const labelElement = document.getElementById('semesterLabel');
    
    try {
        const res = await fetch('/set-semester', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ semester_type: semesterType })
        });
        
        if (res.ok) {
            labelElement.textContent = this.checked ? 'Semester Genap' : 'Semester Ganjil';
            loadJadwal();
        }
    } catch (error) {
        console.error('Error setting semester:', error);
    }
});

let debounceTimeout;
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        const searchQuery = this.value.trim();
        const semesterFilter = document.getElementById('searchSemester').value;
        if (searchQuery.toLowerCase().includes('jadwal kuliah')) {
            searchWithChatbot(searchQuery, semesterFilter);
        } else {
            loadJadwal(searchQuery, semesterFilter);
        }
    }, 300);
});

document.getElementById('searchSemester').addEventListener('change', function() {
    const searchQuery = document.getElementById('searchInput').value.trim();
    const semesterFilter = this.value;
    if (searchQuery.toLowerCase().includes('jadwal kuliah')) {
        searchWithChatbot(searchQuery, semesterFilter);
    } else {
        loadJadwal(searchQuery, semesterFilter);
    }
});

document.getElementById('searchButton').addEventListener('click', async function() {
    const searchQuery = document.getElementById('searchInput').value.trim();
    const semesterFilter = document.getElementById('searchSemester').value;
    if (searchQuery.toLowerCase().includes('jadwal kuliah')) {
        searchWithChatbot(searchQuery, semesterFilter);
    } else {
        loadJadwal(searchQuery, semesterFilter);
    }
});

async function searchWithChatbot(query, semesterFilter = '') {
    try {
        // Tambahkan semester ke kueri jika ada filter semester
        let finalQuery = query;
        if (semesterFilter && !query.toLowerCase().includes('semester')) {
            finalQuery = `${query} semester ${semesterFilter}`;
        }
        
        const res = await fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `message=${encodeURIComponent(finalQuery)}`
        });
        const data = await res.json();
        const searchResult = document.getElementById('searchResult');
        searchResult.style.display = 'block';
        searchResult.innerHTML = `<pre>${data.response}</pre>`;
        loadJadwal(); // Kosongkan tabel jika menggunakan chatbot
    } catch (error) {
        console.error('Error fetching chatbot response:', error);
        alert('Gagal mendapatkan respons: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadJadwal();
    checkSemester();
});