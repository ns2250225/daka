<template>
  <div class="container">
    <div id="map" class="map"></div>
    
    <div class="search-container">
      <input 
        v-model="searchQuery" 
        @keyup.enter="searchLocation" 
        placeholder="输入地点..." 
        class="search-input"
      />
      <button @click="searchLocation" class="search-btn">搜索</button>
      
      <div v-if="searchResults.length" class="search-results">
        <div 
          v-for="result in searchResults" 
          :key="result.place_id" 
          @click="selectLocation(result)"
          class="search-item"
        >
          {{ result.display_name }}
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal fade-in">
        <div class="modal-header">
          <h2>生成旅拍照片</h2>
          <button @click="closeModal" class="close-icon" title="关闭">&times;</button>
        </div>
        
        <div class="location-info">
          <p class="location-name"><strong>地点:</strong> {{ selectedLocation?.display_name }}</p>
          <div class="coords">
            <span class="badge">纬度: {{ parseFloat(selectedLocation?.lat || '0').toFixed(4) }}</span>
            <span class="badge">经度: {{ parseFloat(selectedLocation?.lon || '0').toFixed(4) }}</span>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>上传照片</label>
            <input type="file" @change="handleFileUpload" accept="image/*" class="form-control file-input" />
          </div>
          
          <div class="form-group">
            <label>图片比例</label>
            <select v-model="aspectRatio" class="form-control select-input">
              <option value="3:4">竖屏 (3:4)</option>
              <option value="4:3">横屏 (4:3)</option>
            </select>
          </div>
        </div>

        <button @click="generatePhoto" :disabled="loading" class="generate-btn">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '正在生成中...' : '开始生成旅拍' }}
        </button>
        
        <!-- Preview -->
        <div v-if="generatedImage" class="preview-section fade-in">
          <div class="result-header">
            <h3>生成结果</h3>
            <a :href="generatedImage" download="travel_photo.jpg" class="download-icon-btn" title="下载">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            </a>
          </div>
          
          <div class="image-wrapper" @click="openLightbox">
             <img :src="generatedImage" alt="Generated Travel Photo" class="preview-image" />
             <div class="zoom-overlay">
               <span class="zoom-icon">🔍 点击放大</span>
             </div>
          </div>
          
          <div class="result-actions">
            <a :href="generatedImage" download="travel_photo.jpg" class="action-btn download-btn">
              下载图片
            </a>
            <button @click="generatedImage = null" class="action-btn reset-btn">
              重新生成
            </button>
          </div>
        </div>
        
        <div v-if="error" class="error-msg">{{ error }}</div>
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="showLightbox" class="lightbox" @click="closeLightbox">
        <button class="lightbox-close-btn" @click="closeLightbox">&times;</button>
        <img :src="generatedImage || ''" class="lightbox-image" @click.stop />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import L from 'leaflet';
import axios from 'axios';

// Interfaces
interface SearchResult {
  place_id: number;
  display_name: string;
  lat: string;
  lon: string;
}

// State
const map = ref<L.Map | null>(null);
const searchQuery = ref('');
const searchResults = ref<SearchResult[]>([]);
const showModal = ref(false);
const selectedLocation = ref<SearchResult | null>(null);
const file = ref<File | null>(null);
const aspectRatio = ref('3:4');
const loading = ref(false);
const generatedImage = ref<string | null>(null);
const error = ref<string | null>(null);
const marker = ref<L.Marker | null>(null);
const showLightbox = ref(false);

// Initialize Map
onMounted(() => {
  map.value = L.map('map').setView([20, 0], 2); // Global view

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map.value as any);

  // Fix marker icon issue in Leaflet with Vite/Webpack
  // @ts-ignore
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
});

// Search Logic
const searchLocation = async () => {
  if (!searchQuery.value) return;
  
  try {
    const response = await axios.get('https://nominatim.openstreetmap.org/search', {
      params: {
        q: searchQuery.value,
        format: 'json'
      }
    });
    searchResults.value = response.data;
  } catch (e) {
    console.error(e);
  }
};

const selectLocation = (result: SearchResult) => {
  selectedLocation.value = result;
  searchResults.value = []; // Clear results
  
  const lat = parseFloat(result.lat);
  const lon = parseFloat(result.lon);
  
  if (map.value) {
    map.value.setView([lat, lon], 13);
    
    if (marker.value) {
      map.value.removeLayer(marker.value as any);
    }
    marker.value = L.marker([lat, lon]).addTo(map.value as any);
  }
  
  showModal.value = true;
  generatedImage.value = null;
  error.value = null;
};

const closeModal = () => {
  showModal.value = false;
};

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const f = target.files[0];
    if (f) file.value = f;
  }
};

const openLightbox = () => {
    if (generatedImage.value) {
        showLightbox.value = true;
    }
}

const closeLightbox = () => {
    showLightbox.value = false;
}

const generatePhoto = async () => {
  if (!file.value || !selectedLocation.value) {
    error.value = "请上传照片并选择地点。";
    return;
  }

  loading.value = true;
  error.value = null;

  const formData = new FormData();
  formData.append('file', file.value);
  formData.append('lat', selectedLocation.value.lat);
  formData.append('lon', selectedLocation.value.lon);
  formData.append('aspect_ratio', aspectRatio.value);

  try {
    const response = await axios.post('/api/generate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    const data = response.data;
    console.log("API Response:", data);

    let imgData = null;
    
    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.inline_data?.data) {
        imgData = data.candidates[0].content.parts[0].inline_data.data;
    } else if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.inlineData?.data) {
         imgData = data.candidates[0].content.parts[0].inlineData.data;
    }
    
    if (imgData) {
        generatedImage.value = `data:image/jpeg;base64,${imgData}`;
    } else {
        error.value = "无法解析返回的图片数据。";
        console.error("Unknown response structure:", data);
    }

  } catch (e: any) {
    console.error(e);
    error.value = "生成失败: " + (e.response?.data?.detail || e.message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container {
  position: relative;
  width: 100%;
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

.search-container {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  display: flex;
  flex-direction: column;
  width: 350px;
  backdrop-filter: blur(5px);
}

.search-input {
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
  color: #333;
  background: #fff;
}

.search-input:focus {
  border-color: #4CAF50;
}

.search-btn {
  padding: 12px;
  cursor: pointer;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #45a049;
}

.search-results {
  margin-top: 10px;
  max-height: 250px;
  overflow-y: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  color: #333;
}

.search-item {
  padding: 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.search-item:last-child {
  border-bottom: none;
}

.search-item:hover {
  background-color: #f9f9f9;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(3px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal {
  background: white;
  padding: 30px;
  border-radius: 16px;
  width: 90%;
  max-width: 550px;
  max-height: 90vh;
  overflow-y: auto;
  color: #333;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}

.modal.fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.close-icon {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
  line-height: 1;
  padding: 0;
}

.close-icon:hover {
  color: #333;
}

.location-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.location-name {
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.coords {
  display: flex;
  gap: 10px;
}

.badge {
  background: #e9ecef;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  flex: 1;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  color: #333;
  box-sizing: border-box;
}

.select-input {
  height: 42px; /* Match file input height approx */
}

.generate-btn {
  background-color: #2196F3;
  color: white;
  padding: 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  width: 100%;
  font-size: 16px;
  font-weight: bold;
  transition: background-color 0.3s, transform 0.1s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.generate-btn:hover:not(:disabled) {
  background-color: #1976D2;
}

.generate-btn:active:not(:disabled) {
  transform: scale(0.98);
}

.generate-btn:disabled {
  background-color: #b0bec5;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Preview Section */
.preview-section {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  animation: fadeIn 0.4s ease-out;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.download-icon-btn {
  color: #666;
  transition: color 0.3s;
}

.download-icon-btn:hover {
  color: #2196F3;
}

.image-wrapper {
  position: relative;
  max-width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  cursor: zoom-in;
  margin-bottom: 15px;
  background: #f0f0f0;
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s;
}

.zoom-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-wrapper:hover .zoom-overlay {
  opacity: 1;
}

.zoom-icon {
  color: white;
  font-weight: bold;
  background: rgba(0,0,0,0.5);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
}

.result-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  transition: all 0.2s;
}

.download-btn {
  background-color: #4CAF50;
  color: white;
}

.download-btn:hover {
  background-color: #43a047;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.reset-btn {
  background-color: #f5f5f5;
  color: #666;
}

.reset-btn:hover {
  background-color: #e0e0e0;
  color: #333;
}

.error-msg {
  color: #d32f2f;
  margin-top: 15px;
  background: #ffebee;
  padding: 10px;
  border-radius: 6px;
  font-size: 14px;
}

/* Lightbox */
.lightbox {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  cursor: zoom-out;
  animation: fadeIn 0.2s ease-out;
}

.lightbox-image {
  max-width: 90%;
  max-height: 90vh;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
  border-radius: 4px;
  cursor: default;
}

.lightbox-close-btn {
  position: absolute;
  top: 20px;
  right: 30px;
  background: none;
  border: none;
  color: white;
  font-size: 40px;
  cursor: pointer;
  z-index: 3001;
}
</style>
