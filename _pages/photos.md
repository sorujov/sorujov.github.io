---
layout: archive
title: "Photos"
permalink: /photos/
author_profile: true
---

{% include base_path %}

# Photo Gallery

Welcome to my photo gallery. Here you can find photos from academic events, conferences, travels, and personal moments.

---

## Personal & Travel Photos

<div class="photo-gallery">
  <div class="photo-item">
    <img src="/images/personal/france-garden.jpg" alt="Gardens at Vannes Castle, France" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Gardens at Vannes Castle, France</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/france-station.jpg" alt="Gare de l'Est, Paris" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Gare de l'Est, Paris</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/professional.jpg" alt="Professional Portrait" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Professional Portrait</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/casual-style.jpg" alt="Casual Portrait" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Everyday Moments</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/theme-park.jpg" alt="Theme Park Visit" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Fun Times at Theme Park</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/nature-rock.jpg" alt="Nature and Rock Formations" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Exploring Natural Wonders</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/bike-vannes.jpg" alt="Cycling in Vannes" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Cycling Adventure in Vannes</em></p>
  </div>
</div>

---


---

<style>
.photo-gallery {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin: 20px 0;
}

.photo-item {
  text-align: center;
  max-width: 320px;
}

.photo-item img {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.photo-item img:hover {
  transform: scale(1.05);
}

.photo-item p {
  margin-top: 10px;
  font-style: italic;
  color: #666;
}

@media (max-width: 768px) {
  .photo-gallery {
    flex-direction: column;
    align-items: center;
  }
  
  .photo-item img {
    width: 90% !important;
    height: auto !important;
  }
}
</style>