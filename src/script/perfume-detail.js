// Parfüm Detay Sayfası JavaScript

class PerfumeDetailPage {
    constructor() {
        this.perfumeData = null;
        this.init();
    }

    async init() {
        try {
            // URL'den parfüm bilgilerini al
            const perfumeInfo = window.perfumeAPI.parsePerfumeFromURL();
            
            if (!perfumeInfo) {
                this.showError('Parfüm bilgileri bulunamadı.');
                return;
            }

            // Loading göster
            this.showLoading();

            // Parfüm verilerini çek
            this.perfumeData = await window.perfumeAPI.fetchPerfumeByBrandAndName(
                perfumeInfo.brand, 
                perfumeInfo.name
            );

            if (!this.perfumeData) {
                this.showError('Parfüm bilgileri yüklenemedi.');
                return;
            }

            // Sayfayı güncelle
            this.updatePage();
            this.hideLoading();

        } catch (error) {
            console.error('Parfüm detay sayfası yüklenirken hata:', error);
            this.showError('Bir hata oluştu. Lütfen daha sonra tekrar deneyin.');
        }
    }

    showLoading() {
        document.getElementById('loadingSpinner').style.display = 'flex';
        document.getElementById('mainContent').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'block';
    }

    showError(message) {
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'flex';
        
        const errorContent = document.querySelector('.error-content p');
        if (errorContent) {
            errorContent.textContent = message;
        }
    }

    updatePage() {
        this.updatePerfumeInfo();
        this.updateNotes();
        this.updateRatings();
        this.updateAlternatives();
        this.updatePageTitle();
    }

    updatePerfumeInfo() {
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
    }

    updateNotes() {
        const notesContainer = document.getElementById('perfumeNotes');
        notesContainer.innerHTML = '';

        if (this.perfumeData.notes && this.perfumeData.notes.length > 0) {
            this.perfumeData.notes.forEach(note => {
                const noteElement = document.createElement('span');
                noteElement.className = 'note-item';
                noteElement.textContent = note;
                notesContainer.appendChild(noteElement);
            });
        } else {
            notesContainer.innerHTML = '<span class="note-item">Nota bilgisi bulunamadı</span>';
        }
    }

    updateRatings() {
        const ratingsContainer = document.querySelector('.ratings-grid');
        ratingsContainer.innerHTML = '';

        if (this.perfumeData.ratings && Object.keys(this.perfumeData.ratings).length > 0) {
            Object.entries(this.perfumeData.ratings).forEach(([category, score]) => {
                const ratingElement = this.createRatingElement(category, score);
                ratingsContainer.appendChild(ratingElement);
            });
        } else {
            ratingsContainer.innerHTML = '<div class="rating-item"><div class="rating-label">Değerlendirme</div><div class="rating-value">N/A</div></div>';
        }
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
        const alternativesGrid = document.getElementById('alternativesGrid');
        alternativesGrid.innerHTML = '';

        if (this.perfumeData.bargello_recommendations && this.perfumeData.bargello_recommendations.length > 0) {
            this.perfumeData.bargello_recommendations.forEach(alternative => {
                const alternativeCard = this.createAlternativeCard(alternative);
                alternativesGrid.appendChild(alternativeCard);
            });
        } else {
            alternativesGrid.innerHTML = `
                <div class="no-alternatives">
                    <p>Bu parfüm için henüz muadil bulunamadı.</p>
                </div>
            `;
        }
    }

    createAlternativeCard(alternative) {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'alternative-card';
        
        // Notaları düzenle
        const notesHTML = this.formatAlternativeNotes(alternative.notalar);
        
        cardDiv.innerHTML = `
            <div class="similarity-badge">${alternative.benzerlik}</div>
            <div class="alternative-name">${alternative.isim}</div>
            <div class="alternative-brand">Bargello</div>
            <div class="alternative-price">Uygun Fiyatlı</div>
            ${notesHTML}
        `;
        
        return cardDiv;
    }

    formatAlternativeNotes(notalar) {
        if (!notalar || typeof notalar !== 'object') {
            return '<div class="alternative-notes"><h4>Notalar</h4><p>Nota bilgisi bulunamadı</p></div>';
        }

        let notesHTML = '<div class="alternative-notes">';
        
        Object.entries(notalar).forEach(([category, notes]) => {
            if (notes && notes !== 'Yok' && notes.trim() !== '') {
                notesHTML += `
                    <div class="notes-category">
                        <h4>${category}:</h4>
                        <div class="alternative-notes-list">
                `;
                
                // Notaları virgülle ayır ve her birini span olarak ekle
                const notesList = typeof notes === 'string' ? notes.split(',') : [notes];
                notesList.forEach(note => {
                    if (note.trim()) {
                        notesHTML += `<span class="alternative-note">${note.trim()}</span>`;
                    }
                });
                
                notesHTML += '</div></div>';
            }
        });
        
        notesHTML += '</div>';
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

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    new PerfumeDetailPage();
});

// Hata yakalayıcı
window.addEventListener('error', function(e) {
    console.error('Sayfa hatası:', e.error);
    
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.style.display = 'flex';
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('mainContent').style.display = 'none';
    }
});

// Geri buton için
window.addEventListener('popstate', function(e) {
    // Tarayıcı geri butonuna basıldığında ana sayfaya yönlendir
    if (window.location.pathname === '/perfume-detail.html' && !window.location.search) {
        window.location.href = 'index.html';
    }
});

console.log('🎯 Parfüm Detay Sayfası JavaScript yüklendi!'); 