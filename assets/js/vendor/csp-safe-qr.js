// Minimal CSP-safe QR Code generator
// Based on public domain QR specification
// No eval(), no string compilation, pure DOM manipulation

var CSPSafeQR = (function() {
  'use strict';
  
  // QR Code constants
  var ERROR_CORRECT_LEVEL = {
    L: 1, M: 0, Q: 3, H: 2
  };
  
  var MODE_NUMBER = 1 << 0;
  var MODE_ALPHA_NUM = 1 << 1;
  var MODE_8BIT_BYTE = 1 << 2;
  
  // Simple QR data encoding for URLs (8-bit byte mode only)
  function QRCode(text, errorCorrectLevel) {
    this.text = text;
    this.errorCorrectLevel = errorCorrectLevel || ERROR_CORRECT_LEVEL.H;
    this.typeNumber = this.getTypeNumber(text);
    this.modules = null;
    this.moduleCount = 0;
    this.make();
  }
  
  QRCode.prototype = {
    getTypeNumber: function(text) {
      var length = text.length;
      // Simple type determination based on text length
      if (length <= 14) return 1;
      if (length <= 26) return 2;
      if (length <= 42) return 3;
      if (length <= 62) return 4;
      if (length <= 84) return 5;
      return 6; // For longer URLs
    },
    
    make: function() {
      this.moduleCount = this.typeNumber * 4 + 17;
      this.modules = new Array(this.moduleCount);
      
      for (var row = 0; row < this.moduleCount; row++) {
        this.modules[row] = new Array(this.moduleCount);
        for (var col = 0; col < this.moduleCount; col++) {
          this.modules[row][col] = null;
        }
      }
      
      this.setupPositionProbePattern(0, 0);
      this.setupPositionProbePattern(this.moduleCount - 7, 0);
      this.setupPositionProbePattern(0, this.moduleCount - 7);
      this.setupTimingPattern();
      this.mapData();
    },
    
    setupPositionProbePattern: function(row, col) {
      for (var r = -1; r <= 7; r++) {
        if (row + r <= -1 || this.moduleCount <= row + r) continue;
        
        for (var c = -1; c <= 7; c++) {
          if (col + c <= -1 || this.moduleCount <= col + c) continue;
          
          if ((0 <= r && r <= 6 && (c == 0 || c == 6)) ||
              (0 <= c && c <= 6 && (r == 0 || r == 6)) ||
              (2 <= r && r <= 4 && 2 <= c && c <= 4)) {
            this.modules[row + r][col + c] = true;
          } else {
            this.modules[row + r][col + c] = false;
          }
        }
      }
    },
    
    setupTimingPattern: function() {
      for (var r = 8; r < this.moduleCount - 8; r++) {
        if (this.modules[r][6] != null) continue;
        this.modules[r][6] = (r % 2 == 0);
      }
      
      for (var c = 8; c < this.moduleCount - 8; c++) {
        if (this.modules[6][c] != null) continue;
        this.modules[6][c] = (c % 2 == 0);
      }
    },
    
    mapData: function() {
      // Simplified data mapping - creates a recognizable pattern
      // For demonstration purposes - real QR would need proper error correction
      var textBytes = this.stringToBytes(this.text);
      var bitIndex = 0;
      
      for (var row = this.moduleCount - 1; row > 0; row -= 2) {
        if (row == 6) row--;
        
        for (var i = 0; i < this.moduleCount; i++) {
          for (var col = 0; col < 2; col++) {
            var c = row - col;
            
            if (this.modules[i][c] == null) {
              var dark = false;
              
              if (bitIndex < textBytes.length * 8) {
                dark = (((textBytes[Math.floor(bitIndex / 8)] >>> (7 - (bitIndex % 8))) & 1) == 1);
                bitIndex++;
              }
              
              this.modules[i][c] = dark;
            }
          }
        }
      }
    },
    
    stringToBytes: function(s) {
      var bytes = [];
      for (var i = 0; i < s.length; i++) {
        var c = s.charCodeAt(i);
        if (c < 128) {
          bytes.push(c);
        } else if (c < 2048) {
          bytes.push((c >> 6) | 192);
          bytes.push((c & 63) | 128);
        } else {
          bytes.push((c >> 12) | 224);
          bytes.push(((c >> 6) & 63) | 128);
          bytes.push((c & 63) | 128);
        }
      }
      return bytes;
    },
    
    isDark: function(row, col) {
      if (row < 0 || this.moduleCount <= row || col < 0 || this.moduleCount <= col) {
        throw new Error("QR module out of bounds");
      }
      return this.modules[row][col];
    }
  };
  
  // Public API
  return {
    create: function(text, options) {
      options = options || {};
      var qr = new QRCode(text, options.errorCorrectLevel);
      
      return {
        size: qr.moduleCount,
        isDark: function(row, col) {
          return qr.isDark(row, col);
        }
      };
    }
  };
})();