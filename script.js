// Temel değişkenler
let currentSlide = 0;
let activeSearchType = null;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    updateSliderNavigation();
});

// Event listener'ları başlat
function initializeEventListeners() {
    // Arama seçenekleri
    document.getElementById('byName').addEventListener('click', () => showSearch('name'));
    document.getElementById('byNotes').addEventListener('click', () => showSearch('notes'));
    document.getElementById('byFamily').addEventListener('click', () => showSearch('family'));

    // Arama butonları
    document.getElementById('nameSearchBtn').addEventListener('click', performNameSearch);
    document.getElementById('notesSearchBtn').addEventListener('click', performNotesSearch);

    // Popüler tag'ler
    document.querySelectorAll('.popular-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const searchTerm = this.getAttribute('data-search');
            document.getElementById('perfumeNameInput').value = searchTerm;
            performNameSearch();
        });
    });

    // Aile butonları
    document.querySelectorAll('.family-button').forEach(button => {
        button.addEventListener('click', function() {
            // Aktif durumu güncelle
            document.querySelectorAll('.family-button').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const family = this.getAttribute('data-family');
            performFamilySearch(family);
        });
    });

    // Cinsiyet seçimi
    document.querySelectorAll('.gender-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.gender-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Enter tuşu desteği
    document.getElementById('perfumeNameInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performNameSearch();
        }
    });
}

// Arama tipini göster
function showSearch(type) {
    // Tüm arama tiplerini gizle
    document.querySelectorAll('.search-container').forEach(container => {
        container.classList.remove('active');
    });
    
    // Tüm sonuç alanlarını gizle
    document.querySelectorAll('.comparison-area, .results-grid').forEach(area => {
        area.classList.remove('active');
    });

    // Option card'ları güncelle
    document.querySelectorAll('.option-card').forEach(card => {
        card.classList.remove('active');
    });

    // Seçilen arama tipini göster
    activeSearchType = type;
    
    if (type === 'name') {
        document.getElementById('nameSearch').classList.add('active');
        document.getElementById('byName').classList.add('active');
        scrollToElement('nameSearch');
    } else if (type === 'notes') {
        document.getElementById('notesSearch').classList.add('active');
        document.getElementById('byNotes').classList.add('active');
        scrollToElement('notesSearch');
    } else if (type === 'family') {
        document.getElementById('familySearch').classList.add('active');
        document.getElementById('byFamily').classList.add('active');
        scrollToElement('familySearch');
    }
}

// İsme göre arama yap
function performNameSearch() {
    const searchTerm = document.getElementById('perfumeNameInput').value.trim();
    
    if (!searchTerm) {
        alert('Lütfen bir parfüm adı girin.');
        return;
    }

    showLoading();
    
    // Simüle edilmiş arama - gerçek API entegrasyonu sonrası kaldırılacak
    setTimeout(() => {
        hideLoading();
        showNameComparison(searchTerm);
    }, 1000);
}

// Notalara göre arama yap
function performNotesSearch() {
    const selectedNotes = getSelectedNotes();
    
    if (selectedNotes.length === 0) {
        alert('Lütfen en az bir nota seçin.');
        return;
    }

    showLoading();
    
    // Simüle edilmiş arama - gerçek API entegrasyonu sonrası kaldırılacak
    setTimeout(() => {
        hideLoading();
        showNotesResults(selectedNotes);
    }, 1000);
}

// Aileye göre arama yap
function performFamilySearch(family) {
    showLoading();
    
    // Simüle edilmiş arama - gerçek API entegrasyonu sonrası kaldırılacak
    setTimeout(() => {
        hideLoading();
        showFamilyResults(family);
    }, 1000);
}

// Seçilen notaları al
function getSelectedNotes() {
    const selectedNotes = [];
    document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        selectedNotes.push({
            type: checkbox.name,
            value: checkbox.value
        });
    });
    return selectedNotes;
}

// İsme göre karşılaştırma göster
function showNameComparison(searchTerm) {
    document.querySelectorAll('.search-container').forEach(container => {
        container.classList.remove('active');
    });
    
    document.getElementById('nameComparisonArea').classList.add('active');
    scrollToElement('nameComparisonArea');

    // Bu fonksiyon API entegrasyonu sonrası gerçek verilerle güncellenecek
    updateComparisonCards(searchTerm);
}

// Nota sonuçlarını göster
function showNotesResults(notes) {
    document.querySelectorAll('.search-container').forEach(container => {
        container.classList.remove('active');
    });
    
    document.getElementById('resultsGrid').classList.add('active');
    scrollToElement('resultsGrid');

    // Bu fonksiyon API entegrasyonu sonrası gerçek verilerle güncellenecek
    updateGridResults(notes);
}

// Aile sonuçlarını göster
function showFamilyResults(family) {
    document.querySelectorAll('.search-container').forEach(container => {
        container.classList.remove('active');
    });
    
    document.getElementById('resultsGrid').classList.add('active');
    scrollToElement('resultsGrid');

    // Bu fonksiyon API entegrasyonu sonrası gerçek verilerle güncellenecek
    updateGridResults([{type: 'family', value: family}]);
}

// Slider'dan karşılaştırma göster
function showSliderComparison(perfumeName) {
    // Mevcut arama alanlarını gizle
    document.querySelectorAll('.search-container').forEach(container => {
        container.classList.remove('active');
    });
    
    // Grid sonuçlarını gizle
    document.getElementById('resultsGrid').classList.remove('active');
    
    // İsim karşılaştırma alanını göster
    document.getElementById('nameComparisonArea').classList.add('active');
    scrollToElement('nameComparisonArea');

    // Karşılaştırma kartlarını güncelle
    updateComparisonCards(perfumeName);
}

// Grid'den karşılaştırma göster
function showComparison(perfumeName) {
    showSliderComparison(perfumeName);
}

// Arama'ya geri dön
function goBackToSearch() {
    // Tüm sonuç alanlarını gizle
    document.querySelectorAll('.comparison-area, .results-grid').forEach(area => {
        area.classList.remove('active');
    });

    // Aktif arama tipini göster
    if (activeSearchType) {
        showSearch(activeSearchType);
    } else {
        // Sayfa başına dön
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Slider navigasyonu
function nextSlide() {
    const slider = document.getElementById('sliderContainer');
    const cardWidth = 300; // Kart genişliği + gap
    const maxSlide = Math.max(0, slider.children.length - 4);
    
    if (currentSlide < maxSlide) {
        currentSlide++;
        slider.style.transform = `translateX(-${currentSlide * cardWidth}px)`;
    }
    
    updateSliderNavigation();
}

function previousSlide() {
    const slider = document.getElementById('sliderContainer');
    const cardWidth = 300;
    
    if (currentSlide > 0) {
        currentSlide--;
        slider.style.transform = `translateX(-${currentSlide * cardWidth}px)`;
    }
    
    updateSliderNavigation();
}

function updateSliderNavigation() {
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    const maxSlide = Math.max(0, document.getElementById('sliderContainer').children.length - 4);
    
    prevBtn.disabled = currentSlide === 0;
    nextBtn.disabled = currentSlide >= maxSlide;
}

// Karşılaştırma kartlarını güncelle (API entegrasyonu sonrası güncellenecek)
function updateComparisonCards(perfumeName) {
    // Bu fonksiyon şu anda statik veri kullanıyor
    // API entegrasyonu sonrası gerçek verilerle güncellenecek
    console.log(`Karşılaştırma gösteriliyor: ${perfumeName}`);
    
    // Örnek güncelleme - gerçek API'den veri gelince burası değiştirilecek
    const luxuryCard = document.querySelector('.perfume-comparison-card.luxury');
    const alternativeCard = document.querySelector('.perfume-comparison-card.alternative');
    
    // Lüks parfüm bilgilerini güncelle
    luxuryCard.querySelector('.perfume-name').textContent = perfumeName;
    
    // Alternatif parfüm bilgilerini güncelle
    // Bu veriler API'den gelecek
}

// Grid sonuçlarını güncelle (API entegrasyonu sonrası güncellenecek)
function updateGridResults(searchCriteria) {
    // Bu fonksiyon şu anda statik veri kullanıyor
    // API entegrasyonu sonrası gerçek verilerle güncellenecek
    console.log('Grid sonuçları güncelleniyor:', searchCriteria);
    
    // Grid içeriğini dinamik olarak oluşturmak için API'den gelen veriler kullanılacak
}

// Parfüm verilerini API'den çek (şu anda simüle ediliyor)
async function fetchPerfumeData(searchType, searchValue) {
    // Bu fonksiyon gerçek API entegrasyonu sonrası eklenecek
    try {
        // Simüle edilmiş API çağrısı
        console.log(`API çağrısı yapılıyor: ${searchType} - ${searchValue}`);
        
        // Gerçek API endpoint'i buraya eklenecek
        // const response = await fetch(`/api/perfumes/${searchType}/${searchValue}`);
        // const data = await response.json();
        // return data;
        
        // Şu anda simüle edilmiş veri döndürüyor
        return {
            luxury: {
                name: "Örnek Lüks Parfüm",
                brand: "Lüks Marka",
                price: "₺2,850",
                notes: {
                    top: ["Bergamot", "Limon"],
                    middle: ["Gül", "Yasemin"],
                    base: ["Sandal Ağacı", "Vanilya"]
                }
            },
            alternative: {
                name: "Uygun Fiyatlı Muadil",
                brand: "Alternatif Marka",
                price: "₺385",
                similarity: 92,
                notes: {
                    top: ["Bergamot", "Greyfurt"],
                    middle: ["Gül", "Lavanta"],
                    base: ["Sandal Ağacı", "Misk"]
                }
            }
        };
    } catch (error) {
        console.error('API çağrısında hata:', error);
        return null;
    }
}

// Dinamik kart oluşturma fonksiyonları (API entegrasyonu sonrası kullanılacak)
function createPerfumeCard(perfume, type = 'grid') {
    // Grid kartı oluştur
    if (type === 'grid') {
        return `
            <div class="perfume-grid-card" onclick="showComparison('${perfume.name}')">
                <div class="grid-card-image">
                    <i class="fas fa-image"></i> Parfüm Görseli
                </div>
                <div class="grid-card-content">
                    <div class="grid-perfume-name">${perfume.name}</div>
                    <div class="grid-perfume-brand">${perfume.brand}</div>
                    <div class="grid-perfume-price">${perfume.price}</div>
                    <div class="grid-perfume-notes">
                        ${perfume.notes.map(note => `<span class="grid-note">${note}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    // Slider kartı oluştur
    if (type === 'slider') {
        return `
            <div class="perfume-card" onclick="showSliderComparison('${perfume.name}')">
                <div class="card-image">
                    <div class="popularity-badge">#${perfume.rank || ''}</div>
                    <i class="fas fa-image"></i> Parfüm Görseli
                </div>
                <div class="card-content">
                    <div class="card-perfume-name">${perfume.name}</div>
                    <div class="card-perfume-brand">${perfume.brand}</div>
                    <div class="card-perfume-price">${perfume.price}</div>
                    <div class="card-perfume-notes">
                        ${perfume.notes.map(note => `<span class="card-note">${note}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }
}

// Filtreleme fonksiyonları
function filterByGender() {
    const activeGender = document.querySelector('.gender-btn.active').getAttribute('data-gender');
    // API çağrısında cinsiyet filtresi kullanılacak
    console.log('Aktif cinsiyet filtresi:', activeGender);
}

function filterByPriceRange(minPrice, maxPrice) {
    // Fiyat aralığına göre filtreleme
    console.log(`Fiyat filtresi: ${minPrice} - ${maxPrice}`);
}

// Arama geçmişi yönetimi
function addToSearchHistory(searchTerm, searchType) {
    let history = JSON.parse(localStorage.getItem('perfumeSearchHistory') || '[]');
    
    const searchEntry = {
        term: searchTerm,
        type: searchType,
        timestamp: new Date().toISOString()
    };
    
    // Aynı arama varsa kaldır
    history = history.filter(item => !(item.term === searchTerm && item.type === searchType));
    
    // Başa ekle
    history.unshift(searchEntry);
    
    // Son 10 aramayı sakla
    history = history.slice(0, 10);
    
    localStorage.setItem('perfumeSearchHistory', JSON.stringify(history));
}

function loadSearchHistory() {
    const history = JSON.parse(localStorage.getItem('perfumeSearchHistory') || '[]');
    // Arama geçmişini UI'da göstermek için kullanılabilir
    return history;
}

// Favoriler yönetimi
function addToFavorites(perfumeId) {
    let favorites = JSON.parse(localStorage.getItem('perfumeFavorites') || '[]');
    
    if (!favorites.includes(perfumeId)) {
        favorites.push(perfumeId);
        localStorage.setItem('perfumeFavorites', JSON.stringify(favorites));
        console.log('Favorilere eklendi:', perfumeId);
    }
}

function removeFromFavorites(perfumeId) {
    let favorites = JSON.parse(localStorage.getItem('perfumeFavorites') || '[]');
    favorites = favorites.filter(id => id !== perfumeId);
    localStorage.setItem('perfumeFavorites', JSON.stringify(favorites));
    console.log('Favorilerden kaldırıldı:', perfumeId);
}

function getFavorites() {
    return JSON.parse(localStorage.getItem('perfumeFavorites') || '[]');
}

// Karşılaştırma sonuçlarını değerlendirme
function ratePerfumeComparison(perfumeId, rating, comment = '') {
    const ratingData = {
        perfumeId: perfumeId,
        rating: rating, // 'like' veya 'dislike'
        comment: comment,
        timestamp: new Date().toISOString()
    };
    
    // Bu veri API'ye gönderilecek
    console.log('Değerlendirme gönderiliyor:', ratingData);
    
    // Simüle edilmiş API çağrısı
    // sendRatingToAPI(ratingData);
}

// Hata yönetimi
function showError(message) {
    // Hata mesajı göster
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <div class="error-content">
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button class="close-error" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // 5 saniye sonra otomatik kaldır
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

// Başarı mesajı göster
function showSuccess(message) {
    // Başarı mesajı göster
    console.log('Başarı:', message);
    // UI'da başarı mesajı gösterilebilir
}

// URL yönetimi (derin bağlantılar için)
function updateURL(searchType, searchValue) {
    const url = new URL(window.location);
    url.searchParams.set('type', searchType);
    url.searchParams.set('search', searchValue);
    window.history.pushState({}, '', url);
}

function loadFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const searchType = urlParams.get('type');
    const searchValue = urlParams.get('search');
    
    if (searchType && searchValue) {
        // URL'den gelen parametrelere göre arama yap
        if (searchType === 'name') {
            document.getElementById('perfumeNameInput').value = searchValue;
            showSearch('name');
            performNameSearch();
        }
        // Diğer arama tipleri için de eklenebilir
    }
}

// Yardımcı fonksiyonlar
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Responsive slider ayarları
function getVisibleCardCount() {
    const screenWidth = window.innerWidth;
    if (screenWidth < 768) return 1;
    if (screenWidth < 1024) return 2;
    if (screenWidth < 1200) return 3;
    return 4;
}

// Sayfa yüklendiğinde URL'yi kontrol et
window.addEventListener('load', function() {
    loadFromURL();
});

// Responsive slider
window.addEventListener('resize', debounce(function() {
    currentSlide = 0;
    document.getElementById('sliderContainer').style.transform = 'translateX(0)';
    updateSliderNavigation();
}, 250));

// Sayfa kapatılmadan önce arama geçmişini kaydet
window.addEventListener('beforeunload', function() {
    // Son arama durumunu kaydet
    const lastSearch = {
        activeSearchType: activeSearchType,
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('lastPerfumeSearch', JSON.stringify(lastSearch));
});

// Global hata yakalayıcı
window.addEventListener('error', function(e) {
    console.error('Sayfa hatası:', e.error);
    showError('Bir hata oluştu. Lütfen sayfayı yenileyin.');
});

// Service Worker kaydı (PWA için - isteğe bağlı)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW kayıt başarılı:', registration.scope);
            })
            .catch(function(error) {
                console.log('SW kayıt hatası:', error);
            });
    });
}

// Konsol mesajı
console.log('🎯 PerfuMatch JavaScript yüklendi!');
console.log('📝 API entegrasyonu için hazır alanlar:');
console.log('   - fetchPerfumeData() fonksiyonu');
console.log('   - updateComparisonCards() fonksiyonu'); 
console.log('   - updateGridResults() fonksiyonu');
console.log('   - createPerfumeCard() fonksiyonu');