// PerfuMatch API Entegrasyonu
class PerfumeAPI {
    constructor() {
        // Always use Flask backend on port 5000
        this.baseURL = 'http://localhost:5000';
        this.apiURL = `${this.baseURL}/api`;
        
        console.log('🔗 API Base URL:', this.baseURL);
        console.log('🔗 API URL:', this.apiURL);
    }

    // Yardımcı fonksiyonlar
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Parfüm arama (veritabanından)
    async searchPerfumes(searchTerm, searchType = 'name', gender = 'all', limit = 10) {
        const url = `${this.apiURL}/perfume/search`;
        const data = {
            searchTerm,
            searchType,
            gender,
            limit
        };

        return await this.makeRequest(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Parfumo.com'dan arama
    async searchParfumo(brand, perfumeName) {
        const url = `${this.apiURL}/perfume/parfumo-search`;
        const data = {
            brand,
            perfumeName
        };

        return await this.makeRequest(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Parfüm detayı
    async getPerfumeDetail(perfumeId) {
        const url = `${this.apiURL}/perfume/${perfumeId}`;
        return await this.makeRequest(url);
    }

    // Parfüm alternatifleri
    async getPerfumeAlternatives(perfumeId) {
        const url = `${this.apiURL}/perfume/${perfumeId}/alternatives`;
        return await this.makeRequest(url);
    }

    // Markalar
    async getBrands() {
        const url = `${this.apiURL}/brands`;
        return await this.makeRequest(url);
    }

    // Parfüm aileleri
    async getFamilies() {
        const url = `${this.apiURL}/families`;
        return await this.makeRequest(url);
    }

    // Notalar
    async getNotes(type = null) {
        let url = `${this.apiURL}/notes`;
        if (type) {
            url += `?type=${type}`;
        }
        return await this.makeRequest(url);
    }

    // Popüler parfümler
    async getPopularPerfumes() {
        const url = `${this.apiURL}/popular-perfumes`;
        return await this.makeRequest(url);
    }

    // Parfüm değerlendirme
    async ratePerfume(perfumeId, rating, comment = '', similarityId = null) {
        const url = `${this.apiURL}/perfume/${perfumeId}/rate`;
        const data = {
            rating,
            comment,
            similarity_id: similarityId
        };

        return await this.makeRequest(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Sağlık kontrolü
    async healthCheck() {
        const url = `${this.apiURL}/health`;
        return await this.makeRequest(url);
    }

    // URL oluşturma yardımcıları
    createPerfumeURL(brand, perfumeName) {
        // Detay sayfası yerine ana sayfada karşılaştırma göster
        return `${this.baseURL}/#comparison?brand=${encodeURIComponent(brand)}&name=${encodeURIComponent(perfumeName)}`;
    }

    // Parfüm kartı oluşturma
    createPerfumeCard(perfume, type = 'grid') {
        if (type === 'grid') {
            const brandName = perfume.brand ? perfume.brand.name : 'Bilinmiyor';
            return `
                <div class="perfume-grid-card" onclick="window.perfumeAPI.showPerfumeComparison('${brandName}', '${perfume.name}')">
                    <div class="grid-card-image">
                        ${perfume.image_url ? 
                            `<img src="${perfume.image_url}" alt="${perfume.name}" />` :
                            '<i class="fas fa-image"></i> Parfüm Görseli'
                        }
                    </div>
                    <div class="grid-card-content">
                        <div class="grid-perfume-name">${perfume.name}</div>
                        <div class="grid-perfume-brand">${brandName}</div>
                        <div class="grid-perfume-price">${perfume.price ? perfume.price + ' ' + perfume.currency : 'Fiyat Belirtilmemiş'}</div>
                        <div class="grid-perfume-notes">
                            ${this.renderNotes(perfume.notes, 'grid')}
                        </div>
                        ${perfume.rating ? `<div class="grid-perfume-rating">⭐ ${perfume.rating}</div>` : ''}
                    </div>
                </div>
            `;
        }

        if (type === 'slider') {
            const brandName = perfume.brand ? perfume.brand.name : 'Bilinmiyor';
            return `
                <div class="perfume-card" onclick="window.perfumeAPI.showPerfumeComparison('${brandName}', '${perfume.name}')">
                    <div class="card-image">
                        ${perfume.image_url ? 
                            `<img src="${perfume.image_url}" alt="${perfume.name}" />` :
                            '<i class="fas fa-image"></i> Parfüm Görseli'
                        }
                    </div>
                    <div class="card-content">
                        <div class="card-perfume-name">${perfume.name}</div>
                        <div class="card-perfume-brand">${brandName}</div>
                        <div class="card-perfume-price">${perfume.price ? perfume.price + ' ' + perfume.currency : 'Fiyat Belirtilmemiş'}</div>
                        <div class="card-perfume-notes">
                            ${this.renderNotes(perfume.notes, 'card')}
                        </div>
                    </div>
                </div>
            `;
        }
    }

    // Notaları render etme
    renderNotes(notes, type = 'grid') {
        if (!notes) return '';
        
        const className = type === 'grid' ? 'grid-note' : 'card-note';
        let html = '';
        
        // Üst notalar
        if (notes.top && notes.top.length > 0) {
            html += notes.top.slice(0, 3).map(note => 
                `<span class="${className}">${note.name}</span>`
            ).join('');
        }
        
        // Orta notalar
        if (notes.middle && notes.middle.length > 0) {
            html += notes.middle.slice(0, 2).map(note => 
                `<span class="${className}">${note.name}</span>`
            ).join('');
        }
        
        // Alt notalar
        if (notes.base && notes.base.length > 0) {
            html += notes.base.slice(0, 2).map(note => 
                `<span class="${className}">${note.name}</span>`
            ).join('');
        }
        
        return html;
    }

    // Karşılaştırma kartı oluşturma
    createComparisonCard(perfume, alternatives) {
        if (!alternatives || alternatives.length === 0) {
            return '<div class="no-alternatives">Bu parfüm için alternatif bulunamadı.</div>';
        }

        const bestAlternative = alternatives[0];
        
        return `
            <div class="comparison-container">
                <!-- Lüks Parfüm -->
                <div class="perfume-comparison-card luxury">
                    <div class="card-badge luxury-badge">
                        <i class="fas fa-crown"></i> Lüks Parfüm
                    </div>
                    <div class="perfume-image-placeholder">
                        ${perfume.image_url ? 
                            `<img src="${perfume.image_url}" alt="${perfume.name}" />` :
                            '<i class="fas fa-image"></i> Parfüm Görseli'
                        }
                    </div>
                    <div class="perfume-name">${perfume.name}</div>
                    <div class="perfume-brand">${perfume.brand ? perfume.brand.name : 'Bilinmiyor'}</div>
                    <div class="perfume-price">${perfume.price ? perfume.price + ' ' + perfume.currency : 'Fiyat Belirtilmemiş'}</div>
                    
                    ${this.renderNotesSection(perfume.notes)}
                </div>

                <!-- VS -->
                <div class="vs-container">VS</div>

                <!-- Muadil Parfüm -->
                <div class="perfume-comparison-card alternative">
                    <div class="card-badge alternative-badge">
                        <i class="fas fa-star"></i> Uygun Fiyatlı Muadil
                    </div>
                    <div class="perfume-image-placeholder">
                        ${bestAlternative.image_url ? 
                            `<img src="${bestAlternative.image_url}" alt="${bestAlternative.name}" />` :
                            '<i class="fas fa-image"></i> Parfüm Görseli'
                        }
                    </div>
                    <div class="perfume-name">${bestAlternative.name}</div>
                    <div class="perfume-brand">${bestAlternative.brand ? bestAlternative.brand.name : 'Bilinmiyor'}</div>
                    <div class="perfume-price">${bestAlternative.price ? bestAlternative.price + ' ' + bestAlternative.currency : 'Fiyat Belirtilmemiş'}</div>
                    
                    <div class="similarity-info">
                        <div class="similarity-percentage">${bestAlternative.similarity_score || '85'}%</div>
                        <div class="similarity-text">Benzerlik Oranı</div>
                    </div>
                    
                    ${this.renderNotesSection(bestAlternative.notes)}
                </div>
            </div>
        `;
    }

    // Nota bölümü render etme
    renderNotesSection(notes) {
        if (!notes) return '';
        
        let html = '';
        
        if (notes.top && notes.top.length > 0) {
            html += `
                <div class="notes-section">
                    <div class="notes-title">Üst Notalar:</div>
                    <div class="notes-list">
                        ${notes.top.map(note => `<span class="note-tag">${note.name}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        if (notes.middle && notes.middle.length > 0) {
            html += `
                <div class="notes-section">
                    <div class="notes-title">Orta Notalar:</div>
                    <div class="notes-list">
                        ${notes.middle.map(note => `<span class="note-tag">${note.name}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        if (notes.base && notes.base.length > 0) {
            html += `
                <div class="notes-section">
                    <div class="notes-title">Alt Notalar:</div>
                    <div class="notes-list">
                        ${notes.base.map(note => `<span class="note-tag">${note.name}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        return html;
    }

    // Parfüm detayını göster
    async showPerfumeDetail(perfumeId) {
        try {
            const perfume = await this.getPerfumeDetail(perfumeId);
            const alternatives = await this.getPerfumeAlternatives(perfumeId);
            
            // Karşılaştırma alanını göster
            document.querySelectorAll('.search-container, .results-grid').forEach(container => {
                container.classList.remove('active');
            });
            
            const comparisonArea = document.getElementById('nameComparisonArea');
            if (comparisonArea) {
                comparisonArea.innerHTML = `
                    <h2 class="comparison-title">Parfüm Karşılaştırması</h2>
                    ${this.createComparisonCard(perfume, alternatives.alternatives)}
                    <button class="back-button" onclick="goBackToSearch()">
                        <i class="fas fa-arrow-left"></i> Geri Dön
                    </button>
                `;
                comparisonArea.classList.add('active');
                comparisonArea.scrollIntoView({ behavior: 'smooth' });
            }
            
        } catch (error) {
            console.error('Parfüm detay hatası:', error);
            showError('Parfüm detayları yüklenemedi');
        }
    }

    // Parfüm karşılaştırmasını göster (marka ve isim ile)
    async showPerfumeComparison(brand, perfumeName) {
        try {
            // Loading göster
            if (typeof showLoading === 'function') {
                showLoading();
            }

            // Önce veritabanında ara
            const searchResults = await this.searchPerfumes(`${brand} ${perfumeName}`, 'name');
            
            if (searchResults.results && searchResults.results.length > 0) {
                // Veritabanında bulundu, ID ile detay göster
                const perfume = searchResults.results[0];
                await this.showPerfumeDetail(perfume.id);
            } else {
                // Veritabanında bulunamadı, Parfumo'dan ara
                const parfumoResult = await this.searchParfumo(brand, perfumeName);
                
                if (parfumoResult) {
                    // Parfumo sonucunu göster
                    this.showParfumoComparison(parfumoResult);
                } else {
                    throw new Error('Parfüm bulunamadı');
                }
            }
            
            // Loading gizle
            if (typeof hideLoading === 'function') {
                hideLoading();
            }
            
        } catch (error) {
            console.error('Parfüm karşılaştırma hatası:', error);
            if (typeof hideLoading === 'function') {
                hideLoading();
            }
            if (typeof showError === 'function') {
                showError('Parfüm karşılaştırması yüklenemedi');
            }
        }
    }

    // Parfumo sonucunu göster
    showParfumoComparison(parfumoData) {
        // Arama alanlarını gizle
        document.querySelectorAll('.search-container, .results-grid').forEach(container => {
            container.classList.remove('active');
        });
        
        // Karşılaştırma alanını göster
        const comparisonArea = document.getElementById('nameComparisonArea');
        
        // Parfumo verisini karşılaştırma formatına çevir
        const luxuryPerfume = {
            name: parfumoData.perfumer || 'Bilinmiyor',
            brand: { name: 'Lüks Marka' },
            price: 'Yüksek Fiyat',
            currency: 'TRY',
            notes: this.convertParfumoNotes(parfumoData.notes)
        };
        
        const alternatives = parfumoData.database_alternatives || parfumoData.bargello_recommendations || [];
        
        comparisonArea.innerHTML = `
            <h2 class="comparison-title">Parfüm Karşılaştırması</h2>
            ${this.createComparisonCard(luxuryPerfume, alternatives)}
            <button class="back-button" onclick="goBackToSearch()">
                <i class="fas fa-arrow-left"></i> Geri Dön
            </button>
        `;
        
        comparisonArea.classList.add('active');
        comparisonArea.scrollIntoView({ behavior: 'smooth' });
    }

    // Parfumo notalarını çevir
    convertParfumoNotes(notes) {
        if (!notes || !Array.isArray(notes)) return { top: [], middle: [], base: [] };
        
        return {
            top: notes.slice(0, 3).map(note => ({ name: note })),
            middle: notes.slice(3, 6).map(note => ({ name: note })),
            base: notes.slice(6).map(note => ({ name: note }))
        };
    }

    // Popüler parfümleri yükle
    async loadPopularPerfumes() {
        try {
            const data = await this.getPopularPerfumes();
            const slider = document.getElementById('sliderContainer');
            
            if (slider && data.top_rated) {
                slider.innerHTML = data.top_rated.map((perfume, index) => {
                    perfume.rank = index + 1;
                    return this.createPerfumeCard(perfume, 'slider');
                }).join('');
            }
            
        } catch (error) {
            console.error('Popüler parfüm yükleme hatası:', error);
        }
    }

    // Notaları dinamik olarak yükle
    async loadNotes() {
        try {
            const [topNotes, middleNotes, baseNotes] = await Promise.all([
                this.getNotes('top'),
                this.getNotes('middle'),
                this.getNotes('base')
            ]);

            // Üst notalar
            const topContainer = document.querySelector('[data-note-type="top"] .checkbox-group');
            if (topContainer) {
                topContainer.innerHTML = topNotes.map(note => `
                    <div class="checkbox-item">
                        <input type="checkbox" id="note_top_${note.id}" name="topNotes" value="${note.name}">
                        <label for="note_top_${note.id}">${note.name}</label>
                    </div>
                `).join('');
            }

            // Orta notalar
            const middleContainer = document.querySelector('[data-note-type="middle"] .checkbox-group');
            if (middleContainer) {
                middleContainer.innerHTML = middleNotes.map(note => `
                    <div class="checkbox-item">
                        <input type="checkbox" id="note_middle_${note.id}" name="middleNotes" value="${note.name}">
                        <label for="note_middle_${note.id}">${note.name}</label>
                    </div>
                `).join('');
            }

            // Alt notalar
            const baseContainer = document.querySelector('[data-note-type="base"] .checkbox-group');
            if (baseContainer) {
                baseContainer.innerHTML = baseNotes.map(note => `
                    <div class="checkbox-item">
                        <input type="checkbox" id="note_base_${note.id}" name="baseNotes" value="${note.name}">
                        <label for="note_base_${note.id}">${note.name}</label>
                    </div>
                `).join('');
            }

        } catch (error) {
            console.error('Nota yükleme hatası:', error);
        }
    }

    // URL'den parfüm bilgilerini parse et
    parsePerfumeFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const brand = urlParams.get('brand');
        const name = urlParams.get('name');
        
        console.log('🔍 URL\'den parse edilen bilgiler:', { brand, name });
        
        if (!brand || !name) {
            console.error('❌ URL\'de brand veya name parametresi bulunamadı');
            return null;
        }
        
        return { brand, name };
    }

    // Marka ve isim ile parfüm getir
    async fetchPerfumeByBrandAndName(brand, name) {
        try {
            console.log('🔍 Parfüm aranıyor:', { brand, name });
            
            // Önce veritabanında ara
            const searchResults = await this.searchPerfumes(`${brand} ${name}`, 'name');
            console.log('📊 Veritabanı arama sonucu:', searchResults);
            
            if (searchResults.results && searchResults.results.length > 0) {
                const perfume = searchResults.results[0];
                console.log('✅ Veritabanında parfüm bulundu:', perfume);
                
                // Alternatifler için API çağrısı yap
                try {
                    const alternatives = await this.getPerfumeAlternatives(perfume.id);
                    console.log('🔄 Alternatifler getiriliyor:', alternatives);
                    
                    // Alternatifler formatını düzenle
                    const formattedAlternatives = alternatives.alternatives.map(alt => {
                        const altPerfume = alt.alternative_perfume;
                        return {
                            id: altPerfume.id,
                            name: altPerfume.name,
                            brand: altPerfume.brand ? altPerfume.brand.name : 'Bilinmiyor',
                            similarity_score: `${alt.similarity_score}%`,
                            price: altPerfume.price ? `${altPerfume.price} ${altPerfume.currency}` : 'Fiyat Belirtilmemiş',
                            notes: altPerfume.notes || [],
                            gender: altPerfume.gender,
                            image_url: altPerfume.image_url
                        };
                    });
                    
                    perfume.bargello_recommendations = formattedAlternatives;
                    console.log('✅ Formatlanmış alternatifler:', formattedAlternatives);
                } catch (altError) {
                    console.warn('⚠️ Alternatifler getirilemedi:', altError);
                    perfume.bargello_recommendations = [];
                }
                
                return perfume;
            }
            
            // Veritabanında bulunamadı, Parfumo'dan ara
            console.log('🌐 Parfumo\'dan aranıyor...');
            const parfumoResult = await this.searchParfumo(brand, name);
            console.log('📊 Parfumo arama sonucu:', parfumoResult);
            
            if (parfumoResult) {
                // Parfumo verisini uygun formata çevir
                const formattedPerfume = {
                    name: name,
                    brand: { name: brand },
                    gender: parfumoResult.gender || 'Unisex',
                    perfumer: parfumoResult.perfumer || 'Bilinmiyor',
                    url: parfumoResult.url,
                    notes: parfumoResult.notes || [],
                    ratings: parfumoResult.ratings || {},
                    bargello_recommendations: parfumoResult.bargello_recommendations || []
                };
                
                console.log('✅ Parfumo\'dan parfüm formatlandı:', formattedPerfume);
                return formattedPerfume;
            }
            
            console.error('❌ Parfüm hiçbir yerde bulunamadı');
            return null;
            
        } catch (error) {
            console.error('❌ fetchPerfumeByBrandAndName hatası:', error);
            throw error;
        }
    }
}

// Global API instance
window.perfumeAPI = new PerfumeAPI();

// Sayfa yüklendiğinde API'yi başlat
document.addEventListener('DOMContentLoaded', function() {
    // Popüler parfümleri yükle
    window.perfumeAPI.loadPopularPerfumes();
    
    // Notaları yükle
    window.perfumeAPI.loadNotes();
    
    // Sağlık kontrolü yap
    window.perfumeAPI.healthCheck().then(health => {
        console.log('API Durumu:', health);
    }).catch(error => {
        console.error('API bağlantı hatası:', error);
    });
});

console.log('🎯 PerfuMatch API entegrasyonu yüklendi!'); 