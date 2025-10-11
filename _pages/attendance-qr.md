---
layout: single
title: "Attendance QR Code"
permalink: /attendance/math-stat-1/
classes: wide
---

<div style="text-align: center; padding: 2rem;">
  <h2>📊 Mathematical Statistics I - Attendance</h2>
  <p>Class Session QR Code</p>

  <div id="qr" style="display:inline-block;background:#fff;border:3px solid #667eea;border-radius:10px;padding:10px;"></div>
  <p id="qr-status" style="color:#667eea;font-weight:bold;margin-top:15px;">Generating...</p>
</div>

<script>
(function(){
  'use strict';
  // Small QR encoder adapted for CSP, Version 2 (25x25), byte mode, no eval
  function makeMatrix(n){var a=new Array(n);for(var i=0;i<n;i++){a[i]=new Array(n);for(var j=0;j<n;j++)a[i][j]=0;}return a;}
  function mark(m,mask,r,c,v){m[r][c]=v;mask[r][c]=true;}
  function addFinder(m,mask,r,c){
    for(var i=-1;i<=7;i++)for(var j=-1;j<=7;j++){
      var R=r+i,C=c+j;if(R<0||C<0||R>=m.length||C>=m.length)continue;
      var dark=false;
      if(i>=0&&i<=6&&j>=0&&j<=6){
        if(i===0||i===6||j===0||j===6) dark=true;
        if(i>=2&&i<=4&&j>=2&&j<=4) dark=true;
      }
      mark(m,mask,R,C,dark?1:0);
    }
  }
  function addTiming(m,mask){
    var n=m.length;
    for(var i=8;i<n-8;i++){ mark(m,mask,6,i,(i%2===0)?1:0); mark(m,mask,i,6,(i%2===0)?1:0); }
  }
  function bitsForByteModeLen(len){
    var b=[]; // mode 0100
    b.push(0,1,0,0);
    // 8-bit length
    for(var i=7;i>=0;i--) b.push((len>>i)&1);
    return b;
  }
  function bytesToBits(s){
    var b=[];
    for(var k=0;k<s.length;k++){
      var ch=s.charCodeAt(k)&255;
      for(var i=7;i>=0;i--) b.push((ch>>i)&1);
    }
    return b;
  }
  function padBits(b,totalBytes){
    // Terminator up to 4 bits
    var maxBits=totalBytes*8;
    var remaining=maxBits-b.length;
    var term=Math.min(4,Math.max(0,remaining));
    for(var i=0;i<term;i++) b.push(0);
    while(b.length%8!==0) b.push(0);
    // Pad bytes 0xEC, 0x11 alternating
    var pads=[0xEC,0x11],pi=0;
    while(b.length<maxBits){
      var v=pads[pi%2]; pi++;
      for(var i=7;i>=0;i--) b.push((v>>i)&1);
    }
    return b;
  }
  function placeData(m,mask,bits){
    var n=m.length, bi=0, up=true;
    for(var col=n-1; col>0; col-=2){
      if(col===6) col--;
      for(var i=0;i<n;i++){
        var r = up ? (n-1-i) : i;
        for(var k=0;k<2;k++){
          var c=col-k;
          if(!mask[r][c]){
            m[r][c]=(bi<bits.length)?bits[bi++]:0;
          }
        }
      }
      up=!up;
    }
  }
  function drawSVG(m,container){
    var n=m.length, cell=8, margin=cell*2, size=n*cell+margin*2;
    var svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('width',size); svg.setAttribute('height',size);
    var bg=document.createElementNS(svg.namespaceURI,'rect');
    bg.setAttribute('x',0); bg.setAttribute('y',0);
    bg.setAttribute('width',size); bg.setAttribute('height',size);
    bg.setAttribute('fill','#ffffff'); svg.appendChild(bg);
    for(var r=0;r<n;r++){
      for(var c=0;c<n;c++){
        if(m[r][c]){
          var rect=document.createElementNS(svg.namespaceURI,'rect');
          rect.setAttribute('x',margin+c*cell);
          rect.setAttribute('y',margin+r*cell);
          rect.setAttribute('width',cell);
          rect.setAttribute('height',cell);
          rect.setAttribute('fill','#000000');
          svg.appendChild(rect);
        }
      }
    }
    container.innerHTML=''; container.appendChild(svg);
  }

  function generateQR(text){
    // Version 2 (25x25) with enough capacity for short URLs with token
    var n=25, m=makeMatrix(n), mask=makeMatrix(n);
    addFinder(m,mask,0,0); addFinder(m,mask,0,n-7); addFinder(m,mask,n-7,0);
    addTiming(m,mask);
    // Fixed dark module (format/version areas simplified)
    mark(m,mask,8, (n-8), 1);

    var data=[];
    data = data.concat(bitsForByteModeLen(text.length));
    data = data.concat(bytesToBits(text));
    // Version 2-L has 44 data bytes (we'll target ~44)
    padBits(data, 44);
    placeData(m,mask,data);
    return m;
  }

  var status=document.getElementById('qr-status');
  var box=document.getElementById('qr');
  var CLASS_ID='STAT2311-F25';
  var PERIOD=30000;

  function refresh(){
    try{
      var token=btoa(Date.now()+'-'+CLASS_ID);
      var url=location.origin+'/attend/math-stat-1/?tok='+encodeURIComponent(token);
      var matrix=generateQR(url);
      drawSVG(matrix, box);
      status.textContent='✓ QR Updated - '+new Date().toLocaleTimeString();
      status.style.color='#28a745';
    }catch(e){
      status.textContent='⚠ Error: '+e.message;
      status.style.color='#dc3545';
      console.error(e);
    }
  }
  refresh();
  setInterval(refresh, PERIOD);
})();
</script>
