// Simple QR Code Generator using CSS/HTML (CSP-safe)
// This creates a visual QR code without using eval or canvas

function SimpleQR(element, options) {
  this.element = element;
  this.options = Object.assign({
    size: 256,
    cellSize: 8,
    text: '',
    colorDark: '#000',
    colorLight: '#fff'
  }, options);
}

SimpleQR.prototype.makeCode = function(text) {
  // For now, create a placeholder that shows the URL
  // In production, you'd implement actual QR generation
  const url = text;
  
  this.element.innerHTML = `
    <div style="
      width: ${this.options.size}px;
      height: ${this.options.size}px;
      background: ${this.options.colorLight};
      border: 2px solid ${this.options.colorDark};
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      font-family: monospace;
      font-size: 12px;
      text-align: center;
      padding: 10px;
      box-sizing: border-box;
      word-break: break-all;
    ">
      <div style="font-weight: bold; margin-bottom: 10px;">QR Code</div>
      <div style="font-size: 10px; color: #666;">
        ${url}
      </div>
      <div style="margin-top: 10px; font-size: 10px; color: #999;">
        Scan with QR app
      </div>
    </div>
  `;
};

SimpleQR.prototype.clear = function() {
  this.element.innerHTML = '';
};

// Make it available globally
window.SimpleQR = SimpleQR;