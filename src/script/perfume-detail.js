// Parfüm Detay Sayfası JavaScript

class PerfumeDetailPage {
    constructor() {
        this.perfumeData = null;
        this.init();
    }

    async init() {
        try {
            console.log('🎯 Parfüm detay sayfası başlatılıyor...');
            
            // URL'den parfüm bilgilerini al
            const perfumeInfo = window.perfumeAPI.parsePerfumeFromURL();
            console.log('📋 URL\'den alınan bilgiler:', perfumeInfo);
            
            if (!perfumeInfo) {
                console.error('❌ Parfüm bilgileri URL\'de bulunamadı');
                this.showError('Parfüm bilgileri bulunamadı.');
                return;
            }

            // Loading göster
            this.showLoading();
            console.log('⏳ Loading gösteriliyor...');

            // Parfüm verilerini çek
            console.log('🔍 Parfüm verileri getiriliyor:', perfumeInfo.brand, perfumeInfo.name);
            this.perfumeData = await window.perfumeAPI.fetchPerfumeByBrandAndName(
                perfumeInfo.brand, 
                perfumeInfo.name
            );

            console.log('📊 Getirilen parfüm verisi:', this.perfumeData);

            if (!this.perfumeData) {
                console.error('❌ Parfüm verileri getirilemedi');
                this.showError('Parfüm bilgileri yüklenemedi.');
                return;
            }

            // Sayfayı güncelle
            console.log('🔄 Sayfa güncelleniyor...');
            this.updatePage();
            this.hideLoading();
            console.log('✅ Parfüm detay sayfası başarıyla yüklendi');

        } catch (error) {
            console.error('❌ Parfüm detay sayfası yüklenirken hata:', error);
            this.showError('Bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
        }
    }

    showLoading() {
        console.log('⏳ Loading spinner gösteriliyor');
        document.getElementById('loadingSpinner').style.display = 'flex';
        document.getElementById('mainContent').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
    }

    hideLoading() {
        console.log('✅ Loading spinner gizleniyor');
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';
    }

    showError(message) {
        console.error('❌ Hata gösteriliyor:', message);
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'flex';
        
        const errorContent = document.querySelector('.error-content p');
        if (errorContent) {
            errorContent.textContent = message;
        }
    }

    updatePage() {
        console.log('🔄 Sayfa bileşenleri güncelleniyor...');
        this.updatePerfumeInfo();
        this.updateNotes();
        this.updateRatings();
        this.updateAlternatives();
        this.updatePageTitle();
        console.log('✅ Tüm bileşenler güncellendi');
    }

    updatePerfumeInfo() {
        console.log('📝 Parfüm bilgileri güncelleniyor...');
        const perfumeInfo = window.perfumeAPI.parsePerfumeFromURL();
        
        // Başlık ve marka
        document.getElementById('perfumeTitle').textContent = perfumeInfo.name;
        document.getElementById('perfumeBrand').textContent = perfumeInfo.brand;
        
        // Meta bilgiler
        document.getElementById('perfumeGender').textContent = this.perfumeData.gender || 'Unisex';
        document.getElementById('perfumePerfumer').textContent = `Parfümör: ${this.perfumeData.perfumer || 'Bilinmiyor'}`;
        
        // Parfumo linki
        if (this.perfumeData.url) {
            document.getElementById('parfumoLink').href = this.perfumeData.url;
        }
        
        console.log('✅ Parfüm bilgileri güncellendi');
    }

    updateNotes() {
        console.log('🌸 Notalar güncelleniyor...');
        const notesContainer = document.getElementById('perfumeNotes');
        notesContainer.innerHTML = '';

        if (this.perfumeData.notes && this.perfumeData.notes.length > 0) {
            console.log('📋 Notalar bulundu:', this.perfumeData.notes);
            this.perfumeData.notes.forEach(note => {
                const noteElement = document.createElement('span');
                noteElement.className = 'note-item';
                noteElement.textContent = note;
                notesContainer.appendChild(noteElement);
            });
        } else {
            console.log('⚠️ Nota bilgisi bulunamadı');
            notesContainer.innerHTML = '<span class="note-item">Nota bilgisi bulunamadı</span>';
        }
        
        console.log('✅ Notalar güncellendi');
    }

    updateRatings() {
        console.log('⭐ Değerlendirmeler güncelleniyor...');
        const ratingsContainer = document.querySelector('.ratings-grid');
        ratingsContainer.innerHTML = '';

        if (this.perfumeData.ratings && Object.keys(this.perfumeData.ratings).length > 0) {
            console.log('📊 Değerlendirmeler bulundu:', this.perfumeData.ratings);
            Object.entries(this.perfumeData.ratings).forEach(([category, score]) => {
                const ratingElement = this.createRatingElement(category, score);
                ratingsContainer.appendChild(ratingElement);
            });
        } else {
            console.log('⚠️ Değerlendirme bilgisi bulunamadı');
            ratingsContainer.innerHTML = '<div class="rating-item"><div class="rating-label">Değerlendirme</div><div class="rating-value">N/A</div></div>';
        }
        
        console.log('✅ Değerlendirmeler güncellendi');
    }

    createRatingElement(category, score) {
        const ratingDiv = document.createElement('div');
        ratingDiv.className = 'rating-item';
        
        ratingDiv.innerHTML = `
            <div class="rating-label">${this.translateRatingCategory(category)}</div>
            <div class="rating-value">${score}</div>
        `;
        
        return ratingDiv;
    }

    translateRatingCategory(category) {
        const translations = {
            'Scent': 'Koku',
            'Longevity': 'Kalıcılık',
            'Sillage': 'Yayılım',
            'Bottle': 'Şişe',
            'Value': 'Değer',
            'Overall': 'Genel'
        };
        
        return translations[category] || category;
    }

    updateAlternatives() {
        console.log('🔄 Alternatifler güncelleniyor...');
        const alternativesGrid = document.getElementById('alternativesGrid');
        alternativesGrid.innerHTML = '';

        console.log('📊 Mevcut alternatifler:', this.perfumeData.bargello_recommendations);

        if (this.perfumeData.bargello_recommendations && this.perfumeData.bargello_recommendations.length > 0) {
            console.log('✅ Alternatifler bulundu, kartlar oluşturuluyor...');
            this.perfumeData.bargello_recommendations.forEach((alternative, index) => {
                console.log(`📋 Alternatif ${index + 1}:`, alternative);
                const alternativeCard = this.createAlternativeCard(alternative);
                alternativesGrid.appendChild(alternativeCard);
            });
            console.log('✅ Tüm alternatif kartları oluşturuldu');
        } else {
            console.log('⚠️ Hiç alternatif bulunamadı');
            alternativesGrid.innerHTML = `
                <div class="no-alternatives">
                    <i class="fas fa-search"></i>
                    <p>Bu parfüm için henüz muadil bulunamadı.</p>
                    <p class="no-alternatives-subtitle">Benzerlik hesaplaması devam ediyor...</p>
                </div>
            `;
        }
        
        console.log('✅ Alternatifler bölümü güncellendi');
    }

    createAlternativeCard(alternative) {
        console.log('🎨 Alternatif kartı oluşturuluyor:', alternative);
        
        const cardDiv = document.createElement('div');
        cardDiv.className = 'alternative-card';
        
        // Benzerlik skorunu düzenle
        const similarityScore = alternative.similarity_score || '85%';
        const perfumeName = alternative.name || 'Bilinmeyen Parfüm';
        const brand = alternative.brand || 'Bargello';
        const price = alternative.price || 'Uygun Fiyatlı';
        
        // Notaları düzenle
        const notesHTML = this.formatAlternativeNotes(alternative.notes);
        
        cardDiv.innerHTML = `
            <div class="similarity-badge">${similarityScore}</div>
            <div class="alternative-name">${perfumeName}</div>
            <div class="alternative-brand">${brand}</div>
            <div class="alternative-price">${price}</div>
            ${notesHTML}
        `;
        
        console.log('✅ Alternatif kartı oluşturuldu:', perfumeName);
        return cardDiv;
    }

    formatAlternativeNotes(notes) {
        console.log('🌸 Alternatif notaları formatlanıyor:', notes);
        
        if (!notes) {
            console.log('⚠️ Nota bilgisi yok');
            return '<div class="alternative-notes"><h4>Notalar</h4><p>Nota bilgisi bulunamadı</p></div>';
        }

        let notesHTML = '<div class="alternative-notes">';
        
        // Eğer notalar object ise (top, middle, base)
        if (typeof notes === 'object' && !Array.isArray(notes)) {
            console.log('📋 Object formatında notalar bulundu');
            
            // Üst notalar
            if (notes.top && notes.top.length > 0) {
                notesHTML += `
                    <div class="notes-category">
                        <h4>Üst Notalar:</h4>
                        <div class="alternative-notes-list">
                `;
                notes.top.forEach(note => {
                    const noteName = typeof note === 'object' ? note.name : note;
                    if (noteName) {
                        notesHTML += `<span class="alternative-note">${noteName}</span>`;
                    }
                });
                notesHTML += '</div></div>';
            }
            
            // Orta notalar
            if (notes.middle && notes.middle.length > 0) {
                notesHTML += `
                    <div class="notes-category">
                        <h4>Orta Notalar:</h4>
                        <div class="alternative-notes-list">
                `;
                notes.middle.forEach(note => {
                    const noteName = typeof note === 'object' ? note.name : note;
                    if (noteName) {
                        notesHTML += `<span class="alternative-note">${noteName}</span>`;
                    }
                });
                notesHTML += '</div></div>';
            }
            
            // Alt notalar
            if (notes.base && notes.base.length > 0) {
                notesHTML += `
                    <div class="notes-category">
                        <h4>Alt Notalar:</h4>
                        <div class="alternative-notes-list">
                `;
                notes.base.forEach(note => {
                    const noteName = typeof note === 'object' ? note.name : note;
                    if (noteName) {
                        notesHTML += `<span class="alternative-note">${noteName}</span>`;
                    }
                });
                notesHTML += '</div></div>';
            }
        }
        // Eğer notalar array ise
        else if (Array.isArray(notes)) {
            console.log('📋 Array formatında notalar bulundu');
            notesHTML += '<h4>Notalar:</h4><div class="alternative-notes-list">';
            notes.forEach(note => {
                const noteName = typeof note === 'object' ? note.name : note;
                if (noteName && noteName.trim()) {
                    notesHTML += `<span class="alternative-note">${noteName.trim()}</span>`;
                }
            });
            notesHTML += '</div>';
        }
        // Eğer notalar string ise
        else if (typeof notes === 'string') {
            console.log('📋 String formatında notalar bulundu');
            notesHTML += '<h4>Notalar:</h4><div class="alternative-notes-list">';
            const notesList = notes.split(',');
            notesList.forEach(note => {
                if (note.trim()) {
                    notesHTML += `<span class="alternative-note">${note.trim()}</span>`;
                }
            });
            notesHTML += '</div>';
        }
        
        notesHTML += '</div>';
        console.log('✅ Notalar formatlandı');
        return notesHTML;
    }

    updatePageTitle() {
        const perfumeInfo = window.perfumeAPI.parsePerfumeFromURL();
        if (perfumeInfo) {
            document.title = `${perfumeInfo.name} - ${perfumeInfo.brand} | PerfuMatch`;
        }
    }

    // Benzer parfümler için (gelecekte eklenebilir)
    updateSimilarPerfumes() {
        const similarGrid = document.getElementById('similarGrid');
        
        // Şimdilik gizle
        const similarSection = document.querySelector('.similar-section');
        if (similarSection) {
            similarSection.style.display = 'none';
        }
    }
}

// Toast notification sistemi
class ToastNotification {
    static show(message, type = 'info', duration = 3000) {
        console.log(`📢 Toast gösteriliyor: ${type} - ${message}`);
        
        // Toast container oluştur
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // Toast element oluştur
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = this.getIcon(type);
        toast.innerHTML = `
            <div class="toast-content">
                <i class="${icon}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Toast'ı ekle
        toastContainer.appendChild(toast);
        
        // Animasyon için timeout
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // Otomatik kaldırma
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }, duration);
    }
    
    static getIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 DOM yüklendi, PerfumeDetailPage başlatılıyor...');
    new PerfumeDetailPage();
});

// Hata yakalayıcı
window.addEventListener('error', function(e) {
    console.error('❌ Sayfa hatası:', e.error);
    ToastNotification.show('Bir hata oluştu. Sayfa yeniden yüklenecek.', 'error');
    
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.style.display = 'flex';
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'none';
    }
});

// Geri buton için
window.addEventListener('popstate', function(e) {
    console.log('🔙 Geri butonuna basıldı');
    // Tarayıcı geri butonuna basıldığında ana sayfaya yönlendir
    if (window.location.pathname === '/perfume-detail.html' && !window.location.search) {
        window.location.href = 'index.html';
    }
});

console.log('🎯 Parfüm Detay Sayfası JavaScript yüklendi!'); 