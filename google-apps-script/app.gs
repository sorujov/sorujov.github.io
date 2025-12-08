// ==================== BLACKBOARD CONFIGURATION ====================
var BB_CONFIG = {
  baseUrl: 'https://ada.blackboard.com',
  appKey: '02c642f5-e2d4-4ade-856b-555f21932fc8',
  appSecret: 'H5ICy0hMRajfqsyzDNXZ0x5rjcnug91P',
  courseId: '_16980_1'  // Mathematical Statistics I
};

// ==================== CLASS SCHEDULE CONFIGURATION ====================
// All times are in Baku local time (GMT+4 / Asia/Baku timezone)
var CLASS_SCHEDULE = {
  days: [3, 6],  // 3 = Wednesday, 6 = Saturday (0 = Sunday)
  startHour: 10,  // 10:00 Baku time
  startMinute: 0,
  endHour: 12,    // 12:30 Baku time
  endMinute: 30,
  timezone: 'Asia/Baku'
};

// ==================== LOCATION CONFIGURATION ====================
var LOCATION_CONFIG = {
  adaLatitude: 40.39476586000145,
  adaLongitude: 49.84937393783448,
  maxDistanceKm: 5.0  // 5000 meters for testing
};

// ==================== BLACKBOARD AUTHENTICATION ====================
function getBlackboardToken() {
  var cache = CacheService.getScriptCache();
  var cachedToken = cache.get('bb_token');
  if (cachedToken) return cachedToken;
  
  var tokenUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/oauth2/token';
  var credentials = Utilities.base64Encode(BB_CONFIG.appKey + ':' + BB_CONFIG.appSecret);
  
  var options = {
    'method': 'post',
    'headers': { 'Authorization': 'Basic ' + credentials },
    'contentType': 'application/x-www-form-urlencoded',
    'payload': 'grant_type=client_credentials',
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(tokenUrl, options);
    var json = JSON.parse(response.getContentText());
    
    if (json.access_token) {
      cache.put('bb_token', json.access_token, 3300);
      return json.access_token;
    } else {
      Logger.log('Token error: ' + response.getContentText());
      return null;
    }
  } catch (e) {
    Logger.log('Token fetch error: ' + e.message);
    return null;
  }
}

// ==================== BLACKBOARD USER LOOKUP ====================
function getBBUserId(username, token) {
  var url = BB_CONFIG.baseUrl + '/learn/api/public/v1/users?userName=' + encodeURIComponent(username);
  var options = {
    'method': 'get',
    'headers': { 'Authorization': 'Bearer ' + token },
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(url, options);
    var json = JSON.parse(response.getContentText());
    
    if (json.results && json.results.length > 0) {
      return json.results[0].id;
    }
    Logger.log('User not found: ' + username);
    return null;
  } catch (e) {
    Logger.log('User lookup error: ' + e.message);
    return null;
  }
}

// ==================== CHECK COURSE ENROLLMENT ====================
function isEnrolledInCourse(userId, token) {
  var enrollmentUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + 
                      BB_CONFIG.courseId + '/users/' + userId;
  
  var options = {
    'method': 'get',
    'headers': { 'Authorization': 'Bearer ' + token },
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(enrollmentUrl, options);
    var code = response.getResponseCode();
    
    Logger.log('Enrollment check response code: ' + code);
    
    if (code === 200) {
      var enrollment = JSON.parse(response.getContentText());
      Logger.log('Enrollment data: ' + JSON.stringify(enrollment));
      
      if (enrollment.courseRoleId === 'Student') {
        Logger.log('User is enrolled as Student');
        return true;
      } else {
        Logger.log('User has role: ' + enrollment.courseRoleId + ' (not Student)');
        return false;
      }
    } else if (code === 404) {
      Logger.log('User not enrolled in course (404)');
      return false;
    } else {
      Logger.log('Enrollment check failed with code: ' + code);
      return false;
    }
  } catch (e) {
    Logger.log('Enrollment check error: ' + e.message);
    return false;
  }
}

// ==================== LOCATION VALIDATION ====================
function calculateDistance(lat1, lon1, lat2, lon2) {
  var R = 6371; // Earth's radius in kilometers
  var dLat = (lat2 - lat1) * Math.PI / 180;
  var dLon = (lon2 - lon1) * Math.PI / 180;
  var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
          Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
          Math.sin(dLon/2) * Math.sin(dLon/2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function isWithinCampus(latitude, longitude) {
  if (!latitude || !longitude) {
    Logger.log('REJECTED: Missing location data');
    return {
      allowed: false,
      reason: 'Location data is required. Please enable location services and try again.'
    };
  }
  
  var distance = calculateDistance(
    latitude, 
    longitude, 
    LOCATION_CONFIG.adaLatitude, 
    LOCATION_CONFIG.adaLongitude
  );
  
  Logger.log('Distance from campus: ' + (distance * 1000).toFixed(0) + 'm (max: ' + (LOCATION_CONFIG.maxDistanceKm * 1000) + 'm)');
  
  if (distance > LOCATION_CONFIG.maxDistanceKm) {
    Logger.log('REJECTED: Too far from campus');
    return {
      allowed: false,
      reason: 'You must be on ADA University campus to check in. You are ' + (distance * 1000).toFixed(0) + ' meters away from campus (maximum allowed: ' + (LOCATION_CONFIG.maxDistanceKm * 1000).toFixed(0) + 'm).',
      distance: distance
    };
  }
  
  Logger.log('Location check PASSED');
  return { allowed: true, distance: distance };
}

// ==================== SCHEDULE VALIDATION ====================
function isWithinSchedule() {
  var now = new Date();
  // Get current time in Baku timezone
  var bakuTimeStr = Utilities.formatDate(now, CLASS_SCHEDULE.timezone, 'yyyy-MM-dd HH:mm:ss EEEE');
  Logger.log('Current Baku time: ' + bakuTimeStr);
  
  // Parse Baku time components
  var dayOfWeek = parseInt(Utilities.formatDate(now, CLASS_SCHEDULE.timezone, 'u')) % 7; // 1=Mon to 0=Sun
  var hour = parseInt(Utilities.formatDate(now, CLASS_SCHEDULE.timezone, 'HH'));
  var minute = parseInt(Utilities.formatDate(now, CLASS_SCHEDULE.timezone, 'mm'));
  var timeInMinutes = hour * 60 + minute;
  
  var classStartMinutes = CLASS_SCHEDULE.startHour * 60 + CLASS_SCHEDULE.startMinute;
  var classEndMinutes = CLASS_SCHEDULE.endHour * 60 + CLASS_SCHEDULE.endMinute;
  
  Logger.log('Day of week: ' + dayOfWeek + ' (allowed: ' + CLASS_SCHEDULE.days.join(', ') + ')');
  Logger.log('Time in minutes: ' + timeInMinutes + ' (allowed: ' + classStartMinutes + '-' + classEndMinutes + ')');
  
  var isCorrectDay = CLASS_SCHEDULE.days.indexOf(dayOfWeek) !== -1;
  var isCorrectTime = (timeInMinutes >= classStartMinutes && timeInMinutes <= classEndMinutes);
  
  if (!isCorrectDay) {
    var dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    var allowedDays = CLASS_SCHEDULE.days.map(function(d) { return dayNames[d]; }).join(' and ');
    Logger.log('REJECTED: Not on allowed day. Current: ' + dayNames[dayOfWeek]);
    return { 
      allowed: false, 
      reason: 'Attendance is only available on ' + allowedDays + '. Today is ' + dayNames[dayOfWeek] + '.'
    };
  }
  
  if (!isCorrectTime) {
    Logger.log('REJECTED: Outside class time');
    var currentTimeStr = Utilities.formatDate(now, CLASS_SCHEDULE.timezone, 'HH:mm');
    return { 
      allowed: false, 
      reason: 'Attendance is only available during class time (10:00 - 12:30 Baku time). Current time: ' + currentTimeStr + '.'
    };
  }
  
  Logger.log('Schedule check PASSED');
  return { allowed: true };
}

// ==================== BLACKBOARD MEETING MANAGEMENT ====================
function getOrCreateTodayMeeting(token) {
  var today = new Date();
  var todayStr = Utilities.formatDate(today, 'GMT+4', "yyyy-MM-dd");
  
  var meetingsUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + BB_CONFIG.courseId + '/meetings';
  var options = {
    'method': 'get',
    'headers': { 'Authorization': 'Bearer ' + token },
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(meetingsUrl, options);
    var code = response.getResponseCode();
    
    if (code === 200) {
      var data = JSON.parse(response.getContentText());
      var meetings = data.results || [];
      
      for (var i = 0; i < meetings.length; i++) {
        var meeting = meetings[i];
        var meetingDate = meeting.start ? meeting.start.substring(0, 10) : '';
        
        if (meetingDate === todayStr) {
          Logger.log('Found today\'s meeting: ' + meeting.id);
          return meeting.id;
        }
      }
      
      Logger.log('No meeting found for ' + todayStr + ', creating new one...');
      return createMeeting(token, todayStr, today);
      
    } else {
      Logger.log('Failed to get meetings with code: ' + code);
      return null;
    }
    
  } catch (e) {
    Logger.log('Meeting lookup error: ' + e.message);
    return null;
  }
}

// ==================== CREATE MEETING ====================
function createMeeting(token, dateStr, dateObj) {
  var meetingsUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + BB_CONFIG.courseId + '/meetings';
  
  var payload = {
    'title': dateStr,
    'start': dateObj.toISOString()
  };
  
  var options = {
    'method': 'post',
    'headers': { 
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    },
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(meetingsUrl, options);
    var code = response.getResponseCode();
    
    if (code === 201 || code === 200) {
      var meeting = JSON.parse(response.getContentText());
      Logger.log('Meeting created successfully: ' + meeting.id);
      return meeting.id;
    } else {
      Logger.log('Failed to create meeting with code: ' + code);
      return null;
    }
  } catch (e) {
    Logger.log('Create meeting error: ' + e.message);
    return null;
  }
}

// ==================== CHECK IF ALREADY MARKED ====================
function isAlreadyMarked(userId, meetingId, token) {
  var attendanceUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + 
                      BB_CONFIG.courseId + '/meetings/' + meetingId + '/users';
  
  var options = {
    'method': 'get',
    'headers': { 'Authorization': 'Bearer ' + token },
    'muteHttpExceptions': true
  };
  
  try {
    var response = UrlFetchApp.fetch(attendanceUrl, options);
    var code = response.getResponseCode();
    
    if (code === 200) {
      var data = JSON.parse(response.getContentText());
      var attendances = data.results || [];
      
      for (var i = 0; i < attendances.length; i++) {
        if (attendances[i].userId === userId) {
          Logger.log('Student already marked as: ' + attendances[i].status);
          return attendances[i].status;
        }
      }
      return null;
    }
    return null;
  } catch (e) {
    Logger.log('Error checking attendance: ' + e.message);
    return null;
  }
}

// ==================== BLACKBOARD ATTENDANCE RECORDING ====================
function markPresentInBlackboard(email) {
  var maxRetries = 3;
  var retryDelay = 1000;
  
  for (var attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      var username = email.split('@')[0];
      Logger.log('Processing BB sync for: ' + username + ' (Attempt ' + attempt + '/' + maxRetries + ')');
      
      var token = getBlackboardToken();
      if (!token) {
        return { success: false, error: 'Authentication failed - token not obtained' };
      }
      
      var userId = getBBUserId(username, token);
      if (!userId) {
        return { success: false, error: 'User not found in Blackboard: ' + username, notEnrolled: true };
      }
      Logger.log('Found BB user: ' + userId);
      
      var isEnrolled = isEnrolledInCourse(userId, token);
      if (!isEnrolled) {
        Logger.log('User not enrolled in course - rejecting');
        return { success: false, error: 'Not enrolled in this course', notEnrolled: true };
      }
      Logger.log('User is enrolled - proceeding');
      
      var meetingId = getOrCreateTodayMeeting(token);
      if (!meetingId) {
        return { success: false, error: 'Failed to create/find meeting' };
      }
      Logger.log('Using meeting ID: ' + meetingId);
      
      var existingStatus = isAlreadyMarked(userId, meetingId, token);
      if (existingStatus) {
        Logger.log('Student already marked as: ' + existingStatus + '. Skipping duplicate.');
        return { 
          success: true, 
          code: 200, 
          userId: userId, 
          meetingId: meetingId,
          alreadyMarked: true,
          status: existingStatus
        };
      }
      
      var attendanceUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + 
                          BB_CONFIG.courseId + '/meetings/' + meetingId + '/users';
      
      var payload = {
        'meetingId': meetingId,
        'userId': userId,
        'status': 'Present'
      };
      
      Logger.log('Marking attendance with payload: ' + JSON.stringify(payload));
      
      var options = {
        'method': 'post',
        'headers': { 
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        },
        'contentType': 'application/json',
        'payload': JSON.stringify(payload),
        'muteHttpExceptions': true
      };
      
      var response = UrlFetchApp.fetch(attendanceUrl, options);
      var code = response.getResponseCode();
      var text = response.getContentText();
      
      Logger.log('Attendance API response code: ' + code);
      
      if (code === 201 || code === 200) {
        Logger.log('Successfully marked student present!');
        return { success: true, code: code, userId: userId, meetingId: meetingId, alreadyMarked: false };
      }
      
      if (code === 409) {
        Logger.log('Duplicate attendance record (409)');
        return { 
          success: true, 
          code: 409, 
          userId: userId, 
          meetingId: meetingId,
          alreadyMarked: true,
          status: 'Present'
        };
      }
      
      if (code === 503 || code === 429) {
        if (attempt < maxRetries) {
          Logger.log('Blackboard temporarily unavailable (HTTP ' + code + '), retrying in ' + retryDelay + 'ms...');
          Utilities.sleep(retryDelay);
          retryDelay *= 2;
          continue;
        } else {
          return { success: false, error: 'HTTP ' + code + ' (Blackboard unavailable after ' + maxRetries + ' retries)', response: text };
        }
      }
      
      Logger.log('Attendance marking failed with code: ' + code);
      return { success: false, error: 'HTTP ' + code, response: text };
      
    } catch (e) {
      Logger.log('BB Exception on attempt ' + attempt + ': ' + e.message);
      if (attempt < maxRetries) {
        Utilities.sleep(retryDelay);
        retryDelay *= 2;
      } else {
        return { success: false, error: 'Exception after ' + maxRetries + ' retries: ' + e.message };
      }
    }
  }
  
  return { success: false, error: 'Max retries exceeded - Blackboard unavailable' };
}

// ==================== MAIN ATTENDANCE HANDLER (WITH SCHEDULE + LOCATION + ENROLLMENT CHECK) ====================
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    // STEP 1: Check schedule FIRST (fastest check)
    var scheduleCheck = isWithinSchedule();
    if (!scheduleCheck.allowed) {
      Logger.log('REJECTED: Outside schedule - ' + scheduleCheck.reason);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: scheduleCheck.reason,
        errorType: 'schedule',
        outsideSchedule: true
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // STEP 2: Check location (if provided)
    if (data.latitude && data.longitude) {
      var locationCheck = isWithinCampus(parseFloat(data.latitude), parseFloat(data.longitude));
      if (!locationCheck.allowed) {
        Logger.log('REJECTED: Outside campus - ' + locationCheck.reason);
        return ContentService.createTextOutput(JSON.stringify({
          success: false,
          message: locationCheck.reason,
          errorType: 'location',
          distance: locationCheck.distance ? (locationCheck.distance * 1000).toFixed(0) + 'm' : null,
          outsideCampus: true
        })).setMimeType(ContentService.MimeType.JSON);
      }
    }
    
    // STEP 3: Check Blackboard enrollment
    var bbResult = markPresentInBlackboard(data.email);
    
    // STEP 4: If not enrolled, reject completely
    if (bbResult.notEnrolled) {
      Logger.log('REJECTED: Student not enrolled - ' + data.email);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: 'You are not enrolled in this course. Please contact your instructor.',
        errorType: 'enrollment',
        blackboard: 'not_enrolled',
        bbError: bbResult.error
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // STEP 5: Check if Blackboard sync failed (non-enrollment errors)
    if (!bbResult.success) {
      Logger.log('REJECTED: Blackboard sync failed - ' + bbResult.error);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: 'Unable to record attendance in Blackboard: ' + bbResult.error,
        errorType: 'blackboard_sync',
        blackboard: 'failed',
        bbError: bbResult.error
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // STEP 6: Only write to Google Sheet if all checks passed
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    sheet.appendRow([
      new Date(),
      data.email,
      data.sessionTime,
      data.name.split(' ')[0] || data.name,
      data.name.split(' ').slice(1).join(' ') || '',
      `${data.latitude}, ${data.longitude}`,
      data.distance,
      data.email,
      data.email,
      data.name,
      data.latitude,
      data.longitude,
      data.distance
    ]);
    
    // STEP 7: Return success
    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      message: bbResult.alreadyMarked 
        ? 'Your attendance was already recorded for this session.' 
        : 'Attendance recorded successfully!',
      blackboard: 'synced',
      bbDetails: { 
        userId: bbResult.userId, 
        meetingId: bbResult.meetingId,
        alreadyMarked: bbResult.alreadyMarked || false,
        status: bbResult.status || 'Present'
      }
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    Logger.log('doPost error: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: 'Server error: ' + error.toString(),
      errorType: 'server_error'
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput('Attendance API is running');
}

// ==================== TEST FUNCTIONS ====================
function testBlackboardConnection() {
  Logger.log('=== Testing Blackboard Connection ===');
  Logger.log('Base URL: ' + BB_CONFIG.baseUrl);
  Logger.log('Course ID: ' + BB_CONFIG.courseId);
  
  var token = getBlackboardToken();
  Logger.log('Token: ' + (token ? 'OK (' + token.substring(0,20) + '...)' : 'FAILED'));
  
  if (token) {
    var testUsername = 'sorujov';
    var userId = getBBUserId(testUsername, token);
    Logger.log('User lookup (' + testUsername + '): ' + (userId || 'NOT FOUND'));
    
    if (userId) {
      var enrolled = isEnrolledInCourse(userId, token);
      Logger.log('Enrollment status: ' + (enrolled ? 'ENROLLED' : 'NOT ENROLLED'));
      
      if (enrolled) {
        var meetingId = getOrCreateTodayMeeting(token);
        Logger.log('Today meeting: ' + (meetingId || 'FAILED'));
      }
    }
  }
  
  Logger.log('=== Test Complete ===');
}

function testSchedule() {
  Logger.log('=== Testing Schedule Validation ===');
  
  var result = isWithinSchedule();
  Logger.log('Schedule check result: ' + JSON.stringify(result));
  
  if (result.allowed) {
    Logger.log('✅ Within schedule - attendance allowed');
  } else {
    Logger.log('❌ Outside schedule - ' + result.reason);
  }
  
  Logger.log('=== Test Complete ===');
}

function testEnrollment() {
  Logger.log('=== Testing Enrollment Check ===');
  
  var result1 = markPresentInBlackboard('rabaszade19617@ada.edu.az');
  Logger.log('Enrolled student: ' + JSON.stringify(result1));
  
  var result2 = markPresentInBlackboard('fake.student@ada.edu.az');
  Logger.log('Non-enrolled student: ' + JSON.stringify(result2));
  
  Logger.log('=== Test Complete ===');
}

function clearTokenCache() {
  CacheService.getScriptCache().remove('bb_token');
  Logger.log('Token cache cleared');
}

// ==================== TEST ALL ERROR SCENARIOS ====================
function testAllErrorScenarios() {
  Logger.log('=== Testing All Error Scenarios ===\n');
  
  // Test 1: Schedule validation
  Logger.log('TEST 1: Schedule Validation');
  var scheduleResult = isWithinSchedule();
  Logger.log('Result: ' + JSON.stringify(scheduleResult));
  Logger.log('');
  
  // Test 2: Location validation - on campus
  Logger.log('TEST 2: Location Validation - On Campus');
  var onCampusResult = isWithinCampus(40.39476586000145, 49.84937393783448);
  Logger.log('Result: ' + JSON.stringify(onCampusResult));
  Logger.log('');
  
  // Test 3: Location validation - far away (should be rejected)
  Logger.log('TEST 3: Location Validation - Too Far');
  var farAwayResult = isWithinCampus(40.4095, 49.9671); // ~10km away
  Logger.log('Result: ' + JSON.stringify(farAwayResult));
  Logger.log('');
  
  // Test 4: Location validation - very far (should be rejected)
  Logger.log('TEST 4: Location Validation - Very Far');
  var veryFarResult = isWithinCampus(40.3777, 49.7920); // ~6km away
  Logger.log('Result: ' + JSON.stringify(veryFarResult));
  Logger.log('');
  
  // Test 5: Location validation - missing data
  Logger.log('TEST 5: Location Validation - Missing Data');
  var missingDataResult = isWithinCampus(null, null);
  Logger.log('Result: ' + JSON.stringify(missingDataResult));
  Logger.log('');
  
  // Test 6: Enrollment check - enrolled student
  Logger.log('TEST 6: Enrollment Check - Valid Student');
  var enrolledResult = markPresentInBlackboard('rabaszade19617@ada.edu.az');
  Logger.log('Result: ' + JSON.stringify(enrolledResult));
  Logger.log('');
  
  // Test 7: Enrollment check - non-enrolled student
  Logger.log('TEST 7: Enrollment Check - Not Enrolled');
  var notEnrolledResult = markPresentInBlackboard('nonexistent.student@ada.edu.az');
  Logger.log('Result: ' + JSON.stringify(notEnrolledResult));
  Logger.log('');
  
  Logger.log('=== All Tests Complete ===');
  Logger.log('\nSummary:');
  Logger.log('✓ Schedule validation: ' + (scheduleResult.allowed ? 'PASS' : 'FAIL (expected based on current time)'));
  Logger.log('✓ On-campus location: ' + (onCampusResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('✓ Far location rejection: ' + (!farAwayResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('✓ Very far location rejection: ' + (!veryFarResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('✓ Missing location rejection: ' + (!missingDataResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('✓ Enrolled student: ' + (enrolledResult.success ? 'PASS' : 'FAIL (check enrollment)'));
  Logger.log('✓ Not enrolled rejection: ' + (notEnrolledResult.notEnrolled ? 'PASS' : 'FAIL'));
}
