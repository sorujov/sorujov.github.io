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
    <img src="/images/personal/IMG_0289.JPEG" alt="Personal Photo 1" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Personal moments</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/IMG_0290.JPEG" alt="Personal Photo 2" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Life memories</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/IMG_0291.JPEG" alt="Personal Photo 3" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Personal experiences</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/IMG_0335.JPEG" alt="Personal Photo 4" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Captured moments</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/IMG_0339.JPEG" alt="Personal Photo 5" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Special times</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/IMG_0353.JPEG" alt="Personal Photo 6" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Life journey</em></p>
  </div>
</div>

---

*You can add more photos by uploading them to the `images/personal/` or `images/academic/` directories and updating this page.*

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