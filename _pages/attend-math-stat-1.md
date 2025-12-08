---
layout: single
title: "Check-in - Mathematical Statistics I"
permalink: /attend/math-stat-1/
classes: wide
---


<div style="max-width: 500px; margin: 2rem auto; text-align: center;">
  <h2>📊 Confirm Your Attendance</h2>
  <p>Course: Mathematical Statistics I (STAT 2311)</p>
  
  <button id="checkin" type="button" style="
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 2rem;
    border: none;
    border-radius: 25px;
    font-size: 1.2rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    margin: 20px 0;
    transition: transform 0.2s;
    display: inline-block;
  ">
    ✓ Verify Location
  </button>
  
  <div id="student-form" style="display: none; margin-top: 20px;">
    <form id="attendance-form">
      <input type="text" id="student-username" placeholder="Username (e.g., rabaszade19617)" required style="
        width: 100%;
        padding: 12px;
        margin: 10px 0;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 16px;
        box-sizing: border-box;
        color: #333;
        background-color: #fff;
      ">
      <button type="submit" style="
        background: linear-gradient(45deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        margin-top: 10px;
      ">Submit Attendance</button>
    </form>
  </div>
  
  <div id="out" style="
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    min-height: 50px;
    background: #f8f9fa;
  "></div>
  
  <div style="margin-top: 30px; padding: 15px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
    <p style="margin: 0; font-size: 0.9rem;"><strong>Note:</strong> You must be on ADA University campus to check in. Location access is required.</p>
  </div>
</div>

<script src="{{ site.baseurl }}/assets/js/attend-math-stat-1.js?v=20241208-5"></script>
