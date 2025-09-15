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

## Academic & Professional

<div class="photo-gallery">
  <div class="photo-item">
    <img src="/images/academic/conference1.jpg" alt="Academic Conference" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Academic Conference - [Add description here]</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/academic/teaching.jpg" alt="Teaching" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Teaching at ADA University - [Add description here]</em></p>
  </div>
</div>

---

## Travel & Personal

<div class="photo-gallery">
  <div class="photo-item">
    <img src="/images/personal/travel1.jpg" alt="Travel Photo" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Travel memories - [Add description here]</em></p>
  </div>
  
  <div class="photo-item">
    <img src="/images/personal/nature.jpg" alt="Nature" style="width: 300px; height: 200px; object-fit: cover; margin: 10px; border-radius: 8px;">
    <p><em>Nature photography - [Add description here]</em></p>
  </div>
</div>

---

## Instructions for Adding Photos

To add your own photos:

1. **Upload photos** to the appropriate folders:
   - Academic/Professional photos: `images/academic/`
   - Personal/Travel photos: `images/personal/`
   - General photos: `images/`

2. **Update the HTML above** by:
   - Replacing the `src="/images/..."` paths with your actual photo filenames
   - Adding descriptive `alt` text for accessibility
   - Updating the captions with meaningful descriptions

3. **Photo recommendations**:
   - Use high-quality images (at least 1200px wide for best results)
   - Common formats: JPG, PNG, WebP
   - Keep file sizes reasonable (under 2MB each for faster loading)

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