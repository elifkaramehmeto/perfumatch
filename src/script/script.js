// PerfuMatch JavaScript - Basitleştirilmiş Versiyon
console.log('🎯 PerfuMatch JavaScript yüklendi!');
console.log('📝 PostgreSQL veritabanı entegrasyonu aktif');
console.log('🔗 API endpoint\'leri hazır');

// Global değişkenler
let allPerfumes = [];
let currentFilter = 'all';
let currentSearchTerm = '';
let currentSearchType = 'name';
let currentFamily = 'all';
let selectedNotes = [];
let allNotes = [];

// Sayfa yüklendiğinde çalışacak fonksiyon
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 Sayfa yüklendi, lüks parfümler getiriliyor...');
    loadLuxuryPerfumes();
    loadNotes();
    loadFamilies();
    
    // Enter tuşu ile arama
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchPerfumes();
        }
    });
    
    // Family filter değişikliği
    document.getElementById('familyFilter').addEventListener('change', function() {
        currentFamily = this.value;
        applyFilters();
    });
});

// Lüks parfümleri yükle
async function loadLuxuryPerfumes() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/luxury-perfumes');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        allPerfumes = data.perfumes || [];
        
        console.log(`✅ ${allPerfumes.length} lüks parfüm yüklendi`);
        displayPerfumes(allPerfumes);
        
    } catch (error) {
        console.error('❌ Lüks parfümler yüklenirken hata:', error);
        showError('Lüks parfümler yüklenirken bir hata oluştu');
    } finally {
        showLoading(false);
    }
}

// Notaları yükle
async function loadNotes() {
    try {
        const response = await fetch('/api/notes');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // API'den gelen format kontrol et
        if (Array.isArray(data)) {
            // Database API format: array of note objects
            allNotes = data.map(note => note.name || note);
        } else if (data.notes) {
            // JSON file API format: {notes: [...], total: ...}
            allNotes = data.notes;
        } else {
            allNotes = [];
        }
        
        console.log(`✅ ${allNotes.length} nota yüklendi`);
        
    } catch (error) {
        console.error('❌ Notalar yüklenirken hata:', error);
    }
}

// Aileleri yükle ve dropdown'u güncelle
async function loadFamilies() {
    try {
        const response = await fetch('/api/families');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('🔍 Families API response:', data);
        
        // API'den gelen format kontrol et
        let families = [];
        if (Array.isArray(data) && data.length > 0) {
            // Database API format: array of objects with name property
            families = data.map(family => {
                // family is an object with name property
                const familyName = family.name || family;
                console.log('🔍 Processing family:', family, 'Name:', familyName);
                return {
                    value: familyName.toLowerCase(),
                    label: familyName,
                    emoji: getFamilyEmoji(familyName)
                };
            }).filter(family => family.label); // Filter out any invalid entries
        } else if (data.families && data.families.length > 0) {
            // JSON file API format: {families: [...], total: ...}
            families = data.families.map(family => ({
                value: family.toLowerCase(),
                label: family,
                emoji: getFamilyEmoji(family)
            }));
        } else {
            // If no families found, try the database server directly
            console.log('⚠️ No families found, trying database server on port 5000...');
            try {
                const dbResponse = await fetch('http://127.0.0.1:4421/api/families');
                if (dbResponse.ok) {
                    const dbData = await dbResponse.json();
                    console.log('🔍 Database families response:', dbData);
                    if (Array.isArray(dbData) && dbData.length > 0) {
                        families = dbData.map(family => ({
                            value: family.name.toLowerCase(),
                            label: family.name,
                            emoji: getFamilyEmoji(family.name)
                        }));
                        console.log('✅ Families loaded from database server');
                    }
                }
            } catch (dbError) {
                console.log('❌ Database server not available:', dbError.message);
            }
        }
        
        console.log('🔍 Final processed families:', families);
        
        // Dropdown'u güncelle
        const familySelect = document.getElementById('familyFilter');
        
        if (!familySelect) {
            console.error('❌ Family select element not found');
            return;
        }
        
        // Mevcut seçenekleri temizle (ilk seçenek hariç)
        while (familySelect.children.length > 1) {
            familySelect.removeChild(familySelect.lastChild);
        }
        
        // Yeni seçenekleri ekle
        families.forEach(family => {
            const option = document.createElement('option');
            option.value = family.value;
            option.textContent = `${family.emoji} ${family.label}`;
            familySelect.appendChild(option);
        });
        
        console.log(`✅ ${families.length} aile dropdown'a eklendi`);
        
    } catch (error) {
        console.error('❌ Aileler yüklenirken hata:', error);
    }
}

// Aile için emoji döndür
function getFamilyEmoji(familyName) {
    const name = familyName.toLowerCase();
    if (name.includes('floral') || name.includes('çiçek')) return '🌸';
    if (name.includes('woody') || name.includes('odun')) return '🌳';
    if (name.includes('oriental')) return '🌟';
    if (name.includes('fresh') || name.includes('taze')) return '🌿';
    if (name.includes('fruity') || name.includes('meyve')) return '🍎';
    if (name.includes('gourmand') || name.includes('gurme')) return '🍰';
    if (name.includes('chypre')) return '🍃';
    if (name.includes('fougere')) return '🌾';
    return '🌺';
}

// Parfümleri göster
function displayPerfumes(perfumes) {
    const grid = document.getElementById('perfumesGrid');
    
    if (!perfumes || perfumes.length === 0) {
        grid.innerHTML = '<div class="no-results">Parfüm bulunamadı</div>';
        return;
    }
    
    grid.innerHTML = perfumes.map(perfume => createPerfumeCard(perfume)).join('');
}

// Parfüm kartı oluştur
function createPerfumeCard(perfume) {
    const genderClass = perfume.gender ? perfume.gender.toLowerCase() : 'unisex';
    const brandName = perfume.brand?.name || perfume.brand || 'Bilinmeyen Marka';
    
    // Notaları düzenle - API'den gelen format kontrol et
    let allNotes = [];
    if (perfume.notes) {
        if (perfume.notes.top) {
            allNotes = allNotes.concat(perfume.notes.top.map(note => 
                typeof note === 'object' ? note.name : note
            ));
        }
        if (perfume.notes.middle) {
            allNotes = allNotes.concat(perfume.notes.middle.map(note => 
                typeof note === 'object' ? note.name : note
            ));
        }
        if (perfume.notes.base) {
            allNotes = allNotes.concat(perfume.notes.base.map(note => 
                typeof note === 'object' ? note.name : note
            ));
        }
    }
    
    return `
        <div class="perfume-card">
            <div class="perfume-image">🌸</div>
            <div class="perfume-brand">${brandName}</div>
            <div class="perfume-name">${perfume.name || 'İsimsiz Parfüm'}</div>
            <div class="perfume-price">${formatPrice(perfume.price)}</div>
            <div class="perfume-gender ${genderClass}">${getGenderText(perfume.gender)}</div>
            ${allNotes.length > 0 ? `
                <div class="perfume-notes">
                    <div class="notes-title">Notalar:</div>
                    <div class="notes-list">
                        ${allNotes.slice(0, 5).map(note => `<span class="note-tag">${note}</span>`).join('')}
                        ${allNotes.length > 5 ? '<span class="note-tag">+' + (allNotes.length - 5) + ' daha</span>' : ''}
                    </div>
                </div>
            ` : ''}
            <div class="card-actions" style="margin-top: 1rem; display: flex; gap: 0.5rem;">
                <button onclick="findAlternatives(${perfume.id})" class="action-btn primary" style="flex: 1; padding: 8px 12px; background: #8b4513; color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s ease;">
                    🔍 Alternatifler
                </button>
                <button onclick="viewPerfumeDetail(${perfume.id}, 'luxury')" class="action-btn secondary" style="flex: 1; padding: 8px 12px; background: #6c757d; color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s ease;">
                    📋 Detaylar
                </button>
            </div>
        </div>
    `;
}

// Nota filtrelerini göster/gizle
function toggleNotesFilter() {
    const container = document.getElementById('notesFilterContainer');
    const toggle = document.getElementById('notesToggle');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        toggle.textContent = '📝 Notaları Gizle';
        displayNotesFilter();
    } else {
        container.style.display = 'none';
        toggle.textContent = '📝 Notalar';
    }
}

// Nota filtrelerini göster
function displayNotesFilter() {
    const notesGrid = document.getElementById('notesGrid');
    
    if (allNotes.length === 0) {
        notesGrid.innerHTML = '<div class="loading-notes">Notalar yükleniyor...</div>';
        return;
    }
    
    // En popüler notaları seç (ilk 30 nota)
    const popularNotes = allNotes.slice(0, 30);
    
    notesGrid.innerHTML = popularNotes.map(note => `
        <label class="note-checkbox ${selectedNotes.includes(note) ? 'selected' : ''}" onclick="toggleNote('${note}')">
            <input type="checkbox" ${selectedNotes.includes(note) ? 'checked' : ''} onchange="event.stopPropagation()">
            ${note}
        </label>
    `).join('');
}

// Nota seçimini değiştir
function toggleNote(note) {
    if (selectedNotes.includes(note)) {
        selectedNotes = selectedNotes.filter(n => n !== note);
    } else {
        selectedNotes.push(note);
    }
    
    displayNotesFilter();
    applyFilters();
}

// Seçili notaları temizle
function clearSelectedNotes() {
    selectedNotes = [];
    displayNotesFilter();
    applyFilters();
}

// Arama fonksiyonu
function searchPerfumes() {
    const searchInput = document.getElementById('searchInput');
    const searchType = document.getElementById('searchType');
    
    const searchTerm = searchInput.value.trim();
    const searchTypeValue = searchType.value;
    
    currentSearchTerm = searchTerm;
    currentSearchType = searchTypeValue;
    
    if (!searchTerm && selectedNotes.length === 0 && currentFamily === 'all') {
        // Eğer hiç filtre yoksa, tüm parfümleri göster
        displayPerfumes(allPerfumes);
        return;
    }
    
    console.log(`🔍 Arama/Filtreleme uygulanıyor...`);
    applyFilters();
}

// Tüm filtreleri temizle
function clearAllFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('familyFilter').value = 'all';
    currentSearchTerm = '';
    currentFamily = 'all';
    selectedNotes = [];
    
    // Nota filtrelerini gizle
    const container = document.getElementById('notesFilterContainer');
    const toggle = document.getElementById('notesToggle');
    container.style.display = 'none';
    toggle.textContent = '📝 Notalar';
    
    displayPerfumes(allPerfumes);
    console.log('🧹 Tüm filtreler temizlendi');
}

// Backward compatibility - alias for clearAllFilters
function clearSearch() {
    clearAllFilters();
}

// Tüm filtreleri uygula (API kullanarak)
async function applyFilters() {
    try {
        showLoading(true);
        
        // Eğer hiç filtre yoksa, lüks parfümleri göster
        if (!currentSearchTerm && selectedNotes.length === 0 && currentFamily === 'all') {
            loadLuxuryPerfumes();
            return;
        }
        
        // Arama terimi oluştur
        let searchTerm = currentSearchTerm;
        let searchType = currentSearchType;
        
        // Eğer notalar seçilmişse, nota araması yap
        if (selectedNotes.length > 0) {
            searchTerm = selectedNotes.join(', ');
            searchType = 'notes';
        }
        
        // Eğer aile seçilmişse ve arama terimi yoksa, aile araması yap
        if (currentFamily !== 'all' && !searchTerm) {
            searchTerm = currentFamily;
            searchType = 'family';
        }
        
        if (!searchTerm) {
            displayPerfumes([]);
            return;
        }
        
        console.log(`🔍 Arama yapılıyor: "${searchTerm}" (${searchType})`);
        
        // İlk olarak mevcut sunucuyu dene
        let response = await fetch('/api/perfume/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                searchTerm: searchTerm,
                searchType: searchType,
                gender: currentFilter,
                limit: 50
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        let data = await response.json();
        let filteredPerfumes = data.results || [];
        
        // Eğer sonuç yoksa ve database server'ı denemediyse, onu dene
        if (filteredPerfumes.length === 0 && window.location.port !== '5000') {
            console.log('⚠️ No results found, trying database server on port 5000...');
            try {
                const dbResponse = await fetch('http://127.0.0.1:4421/api/perfume/search', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        searchTerm: searchTerm,
                        searchType: searchType,
                        gender: currentFilter,
                        limit: 50
                    })
                });
                
                if (dbResponse.ok) {
                    const dbData = await dbResponse.json();
                    filteredPerfumes = dbData.results || [];
                    console.log(`✅ Database server returned ${filteredPerfumes.length} results`);
                }
            } catch (dbError) {
                console.log('❌ Database server not available:', dbError.message);
            }
        }
        
        // Aile filtresi uygula (eğer API'de desteklenmiyorsa)
        if (currentFamily !== 'all' && searchType !== 'family') {
            filteredPerfumes = filteredPerfumes.filter(perfume => {
                const perfumeFamily = perfume.family?.name?.toLowerCase() || '';
                return perfumeFamily.includes(currentFamily.toLowerCase());
            });
        }
        
        console.log(`🔍 Filtre sonucu: ${filteredPerfumes.length} parfüm`);
        displayPerfumes(filteredPerfumes);
        
    } catch (error) {
        console.error('❌ Filtreleme sırasında hata:', error);
        showError('Filtreleme sırasında bir hata oluştu');
    } finally {
        showLoading(false);
    }
}

// Cinsiyet filtreleme
function filterPerfumes(gender) {
    currentFilter = gender;
    
    // Aktif buton stilini güncelle
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    console.log(`🔍 ${gender} filtresi uygulandı`);
    applyFilters();
}

// Alternatif parfümleri bul
async function findAlternatives(perfumeId) {
    try {
        showLoading(true);
        
        const response = await fetch('/api/find-alternatives', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                luxury_perfume_id: perfumeId,
                min_similarity: 0.3,
                max_results: 10
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.luxury_perfume && data.alternatives !== undefined) {
            showAlternatives(data.luxury_perfume, data.alternatives);
        } else {
            showError(data.error || 'Alternatifler bulunamadı');
        }
        
    } catch (error) {
        console.error('❌ Alternatifler aranırken hata:', error);
        showError('Alternatifler aranırken bir hata oluştu');
    } finally {
        showLoading(false);
    }
}

// Alternatifleri göster
function showAlternatives(luxuryPerfume, alternatives) {
    const section = document.getElementById('alternativesSection');
    
    if (!alternatives || alternatives.length === 0) {
        section.innerHTML = `
            <div class="alternatives-title">Alternatif Bulunamadı</div>
            <div class="no-results">
                ${luxuryPerfume.name} için uygun alternatif bulunamadı.
                <br><br>
                <button class="back-button" onclick="showPerfumeGrid()">
                    ← Lüks Parfümlere Dön
                </button>
            </div>
        `;
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
        return;
    }
    
    section.innerHTML = `
        <div class="alternatives-title">
            ${luxuryPerfume.name} için ${alternatives.length} Alternatif Bulundu
        </div>
        
        <div class="luxury-perfume-info">
            <h3>🌟 ${luxuryPerfume.brand?.name || luxuryPerfume.brand} - ${luxuryPerfume.name}</h3>
            <p><strong>Fiyat:</strong> ${formatPrice(luxuryPerfume.price)}</p>
            <p><strong>Cinsiyet:</strong> ${getGenderText(luxuryPerfume.gender)}</p>
        </div>
        
        <div class="alternatives-grid">
            ${alternatives.map(alt => createAlternativeCard(alt, luxuryPerfume.price)).join('')}
        </div>
        
        <button class="back-button" onclick="showPerfumeGrid()">
            ← Lüks Parfümlere Dön
        </button>
    `;
    
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
    
    console.log(`✅ ${alternatives.length} alternatif gösterildi`);
}

// Alternatif kartı oluştur
function createAlternativeCard(alternative, luxuryPrice) {
    const similarity = Math.round(alternative.similarity_score);
    const savings = luxuryPrice && alternative.price ? luxuryPrice - alternative.price : 0;
    const savingsPercent = luxuryPrice && alternative.price ? Math.round((savings / luxuryPrice) * 100) : 0;
    
    // Notaları düzenle - API'den gelen format: {top: [], middle: [], base: []}
    let allNotes = [];
    if (alternative.notes) {
        if (alternative.notes.top) allNotes = allNotes.concat(alternative.notes.top.map(note => note.name));
        if (alternative.notes.middle) allNotes = allNotes.concat(alternative.notes.middle.map(note => note.name));
        if (alternative.notes.base) allNotes = allNotes.concat(alternative.notes.base.map(note => note.name));
    }
    
    return `
        <div class="alternative-card" onclick="viewPerfumeDetail(${alternative.id}, 'alternative')" style="cursor: pointer;">
            <div class="similarity-badge">${similarity}% Benzer</div>
            <div class="alternative-header">
                <h4>${alternative.brand?.name || alternative.brand} - ${alternative.name}</h4>
            </div>
            <div class="alternative-price">
                ${formatPrice(alternative.price)}
                ${savings > 0 ? `<span class="savings">%${savingsPercent} tasarruf</span>` : ''}
            </div>
            <div class="perfume-gender ${alternative.gender ? alternative.gender.toLowerCase() : 'unisex'}">
                ${getGenderText(alternative.gender)}
            </div>
            ${allNotes.length > 0 ? `
                <div class="perfume-notes">
                    <div class="notes-title">Notalar:</div>
                    <div class="notes-list">
                        ${allNotes.slice(0, 4).map(note => `<span class="note-tag">${note}</span>`).join('')}
                        ${allNotes.length > 4 ? '<span class="note-tag">+' + (allNotes.length - 4) + ' daha</span>' : ''}
                    </div>
                </div>
            ` : ''}
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e9ecef; text-align: center; color: #666; font-size: 0.9rem;">
                📋 Detayları görüntülemek için tıklayın
            </div>
        </div>
    `;
}

// Parfüm detay sayfasına yönlendir
function viewPerfumeDetail(perfumeId, source = 'alternative') {
    window.open(`perfume-detail.html?id=${perfumeId}&source=${source}`, '_blank');
}

// Parfüm grid'ini göster
function showPerfumeGrid() {
    document.getElementById('alternativesSection').style.display = 'none';
    document.querySelector('.filter-section').scrollIntoView({ behavior: 'smooth' });
}

// Yardımcı fonksiyonlar
function formatPrice(price) {
    if (!price) return 'Fiyat belirtilmemiş';
    return `₺${price.toLocaleString('tr-TR')}`;
}

function getGenderText(gender) {
    const genderMap = {
        'men': '👨 Erkek',
        'women': '👩 Kadın',
        'unisex': '🌈 Unisex'
    };
    return genderMap[gender?.toLowerCase()] || '🌈 Unisex';
}

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

function showError(message) {
    console.error('❌ Hata:', message);
    alert('Hata: ' + message);
}

// Hata yakalama
window.addEventListener('error', function(e) {
    console.error('Sayfa hatası:', e.error);
});

// Aile filtresi değiştiğinde
function onFamilyChange() {
    const familySelect = document.getElementById('familyFilter');
    currentFamily = familySelect.value;
    console.log(`🔍 Aile filtresi değişti: ${currentFamily}`);
    applyFilters();
}

// Global fonksiyonları window'a ekle
window.filterPerfumes = filterPerfumes;
window.findAlternatives = findAlternatives;
window.showPerfumeGrid = showPerfumeGrid;
window.searchPerfumes = searchPerfumes;
window.clearSearch = clearSearch;
window.viewPerfumeDetail = viewPerfumeDetail;
window.onFamilyChange = onFamilyChange;