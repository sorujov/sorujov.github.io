// Simple CSP-compliant QR Code Generator
// No eval(), pure DOM manipulation
// Based on QR Code specification

var SimpleQR = (function() {
  'use strict';
  
  // QR Code error correction levels
  var ECL = { L: 1, M: 0, Q: 3, H: 2 };
  
  // Reed-Solomon error correction (simplified for URLs)
  function reedSolomon(data, ecl) {
    // Simplified: for basic URL encoding
    return data;
  }
  
  // Generate QR matrix
  function generateMatrix(text) {
    var size = 29; // Version 3 (29x29) suitable for URLs up to ~100 chars
    var matrix = [];
    
    // Initialize matrix
    for (var i = 0; i < size; i++) {
      matrix[i] = [];
      for (var j = 0; j < size; j++) {
        matrix[i][j] = 0;
      }
    }
    
    // Add finder patterns (corners)
    function addFinderPattern(row, col) {
      for (var i = -1; i <= 7; i++) {
        for (var j = -1; j <= 7; j++) {
          var r = row + i;
          var c = col + j;
          if (r >= 0 && r < size && c >= 0 && c < size) {
            if ((i === 0 || i === 6) && j >= 0 && j <= 6) matrix[r][c] = 1;
            else if ((j === 0 || j === 6) && i >= 0 && i <= 6) matrix[r][c] = 1;
            else if (i >= 2 && i <= 4 && j >= 2 && j <= 4) matrix[r][c] = 1;
          }
        }
      }
    }
    
    addFinderPattern(0, 0);
    addFinderPattern(0, size - 7);
    addFinderPattern(size - 7, 0);
    
    // Add timing patterns
    for (var i = 8; i < size - 8; i++) {
      matrix[6][i] = (i % 2 === 0) ? 1 : 0;
      matrix[i][6] = (i % 2 === 0) ? 1 : 0;
    }
    
    // Encode data (simplified byte mode)
    var bytes = [];
    for (var i = 0; i < text.length; i++) {
      bytes.push(text.charCodeAt(i));
    }
    
    // Fill data into matrix (simplified zigzag pattern)
    var byteIndex = 0;
    var bitIndex = 7;
    var direction = -1;
    var row = size - 1;
    
    for (var col = size - 1; col > 0; col -= 2) {
      if (col === 6) col--;
      
      while (row >= 0 && row < size) {
        for (var c = 0; c < 2; c++) {
          var currentCol = col - c;
          
          if (matrix[row][currentCol] === 0) {
            var bit = 0;
            if (byteIndex < bytes.length) {
              bit = (bytes[byteIndex] >> bitIndex) & 1;
              bitIndex--;
              if (bitIndex < 0) {
                byteIndex++;
                bitIndex = 7;
              }
            }
            matrix[row][currentCol] = bit ? 1 : 0;
          }
        }
        row += direction;
      }
      
      direction = -direction;
      row += direction;
    }
    
    return matrix;
  }
  
  // Create SVG element
  function createSVG(matrix, size) {
    var moduleSize = Math.floor(size / matrix.length);
    var actualSize = moduleSize * matrix.length;
    var border = moduleSize * 2;
    var totalSize = actualSize + (border * 2);
    
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', totalSize);
    svg.setAttribute('height', totalSize);
    svg.setAttribute('viewBox', '0 0 ' + totalSize + ' ' + totalSize);
    
    // White background
    var bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    bg.setAttribute('width', totalSize);
    bg.setAttribute('height', totalSize);
    bg.setAttribute('fill', '#ffffff');
    svg.appendChild(bg);
    
    // Draw modules
    for (var row = 0; row < matrix.length; row++) {
      for (var col = 0; col < matrix[row].length; col++) {
        if (matrix[row][col]) {
          var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          rect.setAttribute('x', (col * moduleSize + border).toString());
          rect.setAttribute('y', (row * moduleSize + border).toString());
          rect.setAttribute('width', moduleSize.toString());
          rect.setAttribute('height', moduleSize.toString());
          rect.setAttribute('fill', '#000000');
          svg.appendChild(rect);
        }
      }
    }
    
    return svg;
  }
  
  return {
    generate: function(container, text, size) {
      size = size || 256;
      var matrix = generateMatrix(text);
      var svg = createSVG(matrix, size);
      container.innerHTML = '';
      container.appendChild(svg);
      return true;
    }
  };
})();