// ==================== BLACKBOARD CONFIGURATION ====================
var BB_CONFIG = {
  baseUrl: 'https://ada.blackboard.com',
  appKey: '02c642f5-e2d4-4ade-856b-555f21932fc8',
  appSecret: 'H5ICy0hMRajfqsyzDNXZ0x5rjcnug91P'
};

// ==================== SECTION CONFIGURATION ====================
// Math Stat II - Spring 2026: Two sections with separate Blackboard courses
var SECTIONS = {
  A: { courseId: '_17607_1', name: 'Section A (STAT-2412 - 20054)' },
  B: { courseId: '_17609_1', name: 'Section B (STAT-2412 - 20055)' }
};

// ==================== CLASS SCHEDULE CONFIGURATION ====================
// All times are in Baku local time (GMT+4 / Asia/Baku timezone)
var SECTION_SCHEDULES = {
  A: {
    days: [0, 3, 6],     // 0 = Sunday (testing), 3 = Wednesday, 6 = Saturday
    startHour: 0,        // All day for testing (restore to 10:00-11:30 for production)
    startMinute: 0,
    endHour: 23,
    endMinute: 59
  },
  B: {
    days: [0, 3, 6],     // 0 = Sunday (testing), 3 = Wednesday, 6 = Saturday
    startHour: 0,        // All day for testing (restore to 11:30-13:00 for production)
    startMinute: 0,
    endHour: 23,
    endMinute: 59
  }
};

var LATE_THRESHOLD_MINUTES = 15; // Students arriving after this many minutes from class start are marked Late
var SCHEDULE_TIMEZONE = 'Asia/Baku';

// ==================== LOCATION CONFIGURATION ====================
var LOCATION_CONFIG = {
  adaLatitude: 40.39476586000145,
  adaLongitude: 49.84937393783448,
  maxDistanceKm: 5  // 500 meters
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
function isEnrolledInCourse(userId, courseId, token) {
  var enrollmentUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' +
                      courseId + '/users/' + userId;

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

// ==================== SECTION DETECTION ====================
// Auto-detect section based on current Baku time
function detectSection() {
  var now = new Date();
  var hour = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'HH'));
  var minute = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'mm'));
  var timeInMinutes = hour * 60 + minute;

  var sections = Object.keys(SECTION_SCHEDULES);
  for (var i = 0; i < sections.length; i++) {
    var sectionKey = sections[i];
    var schedule = SECTION_SCHEDULES[sectionKey];
    var startMinutes = schedule.startHour * 60 + schedule.startMinute;
    var endMinutes = schedule.endHour * 60 + schedule.endMinute;

    if (timeInMinutes >= startMinutes && timeInMinutes <= endMinutes) {
      Logger.log('Auto-detected section: ' + sectionKey + ' (time: ' + hour + ':' + minute + ')');
      return sectionKey;
    }
  }

  Logger.log('Could not auto-detect section at time: ' + hour + ':' + minute);
  return null;
}

// ==================== SCHEDULE VALIDATION ====================
function isWithinSchedule(section) {
  var now = new Date();
  var bakuTimeStr = Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'yyyy-MM-dd HH:mm:ss EEEE');
  Logger.log('Current Baku time: ' + bakuTimeStr);

  var dayOfWeek = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'u')) % 7; // 1=Mon to 0=Sun
  var hour = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'HH'));
  var minute = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'mm'));
  var timeInMinutes = hour * 60 + minute;

  // If section is specified, validate against that section's schedule
  if (section && SECTION_SCHEDULES[section]) {
    var schedule = SECTION_SCHEDULES[section];
    var startMinutes = schedule.startHour * 60 + schedule.startMinute;
    var endMinutes = schedule.endHour * 60 + schedule.endMinute;

    Logger.log('Validating against ' + section + ' schedule: ' + startMinutes + '-' + endMinutes);

    var isCorrectDay = schedule.days.indexOf(dayOfWeek) !== -1;
    var isCorrectTime = (timeInMinutes >= startMinutes && timeInMinutes <= endMinutes);

    if (!isCorrectDay) {
      var dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
      var allowedDays = schedule.days.map(function(d) { return dayNames[d]; }).join(' and ');
      return {
        allowed: false,
        reason: 'Attendance for ' + SECTIONS[section].name + ' is only available on ' + allowedDays + '. Today is ' + dayNames[dayOfWeek] + '.'
      };
    }

    if (!isCorrectTime) {
      var currentTimeStr = Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'HH:mm');
      var startStr = String(schedule.startHour).padStart(2, '0') + ':' + String(schedule.startMinute).padStart(2, '0');
      var endStr = String(schedule.endHour).padStart(2, '0') + ':' + String(schedule.endMinute).padStart(2, '0');
      return {
        allowed: false,
        reason: 'Attendance for ' + SECTIONS[section].name + ' is only available during class time (' + startStr + ' - ' + endStr + ' Baku time). Current time: ' + currentTimeStr + '.'
      };
    }

    Logger.log('Schedule check PASSED for section ' + section);
    return { allowed: true, section: section };
  }

  // If no section specified, check if current time falls within ANY section
  var sections = Object.keys(SECTION_SCHEDULES);
  for (var i = 0; i < sections.length; i++) {
    var sectionKey = sections[i];
    var sched = SECTION_SCHEDULES[sectionKey];
    var start = sched.startHour * 60 + sched.startMinute;
    var end = sched.endHour * 60 + sched.endMinute;
    var correctDay = sched.days.indexOf(dayOfWeek) !== -1;
    var correctTime = (timeInMinutes >= start && timeInMinutes <= end);

    if (correctDay && correctTime) {
      Logger.log('Schedule check PASSED (auto-detected section ' + sectionKey + ')');
      return { allowed: true, section: sectionKey };
    }
  }

  // Not within any section's schedule
  var dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  var currentTimeStr = Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'HH:mm');
  return {
    allowed: false,
    reason: 'Attendance is only available during class time. Section A: Wed/Sat 10:00-11:30, Section B: Wed/Sat 11:30-13:00. Current time: ' + dayNames[dayOfWeek] + ' ' + currentTimeStr + '.'
  };
}

// ==================== BLACKBOARD MEETING MANAGEMENT ====================
function getOrCreateTodayMeeting(courseId, token) {
  var today = new Date();
  var todayStr = Utilities.formatDate(today, 'GMT+4', "yyyy-MM-dd");

  var meetingsUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + courseId + '/meetings';
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
      return createMeeting(courseId, token, todayStr, today);

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
function createMeeting(courseId, token, dateStr, dateObj) {
  var meetingsUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' + courseId + '/meetings';

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
function isAlreadyMarked(userId, courseId, meetingId, token) {
  var attendanceUrl = BB_CONFIG.baseUrl + '/learn/api/public/v1/courses/' +
                      courseId + '/meetings/' + meetingId + '/users';

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
// Records attendance with the specified status (Present or Late)
function markAttendanceInBlackboard(email, courseId, attendanceStatus) {
  var maxRetries = 3;
  var retryDelay = 1000;

  for (var attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      var username = email.split('@')[0];
      Logger.log('Processing BB sync for: ' + username + ' in course ' + courseId + ' as ' + attendanceStatus + ' (Attempt ' + attempt + '/' + maxRetries + ')');

      var token = getBlackboardToken();
      if (!token) {
        return { success: false, error: 'Authentication failed - token not obtained' };
      }

      var userId = getBBUserId(username, token);
      if (!userId) {
        return { success: false, error: 'User not found in Blackboard: ' + username, notEnrolled: true };
      }
      Logger.log('Found BB user: ' + userId);

      var isEnrolled = isEnrolledInCourse(userId, courseId, token);
      if (!isEnrolled) {
        Logger.log('User not enrolled in course ' + courseId + ' - rejecting');
        return { success: false, error: 'Not enrolled in this course section', notEnrolled: true };
      }
      Logger.log('User is enrolled - proceeding');

      var meetingId = getOrCreateTodayMeeting(courseId, token);
      if (!meetingId) {
        return { success: false, error: 'Failed to create/find meeting' };
      }
      Logger.log('Using meeting ID: ' + meetingId);

      var existingStatus = isAlreadyMarked(userId, courseId, meetingId, token);
      if (existingStatus) {
        // Don't downgrade Present to Late
        if (existingStatus === 'Present' && attendanceStatus === 'Late') {
          Logger.log('Student already marked as Present. Not downgrading to Late.');
          return {
            success: true,
            code: 200,
            userId: userId,
            meetingId: meetingId,
            alreadyMarked: true,
            status: existingStatus
          };
        }
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
                          courseId + '/meetings/' + meetingId + '/users';

      var payload = {
        'meetingId': meetingId,
        'userId': userId,
        'status': attendanceStatus
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
        Logger.log('Successfully marked student as ' + attendanceStatus + '!');
        return { success: true, code: code, userId: userId, meetingId: meetingId, alreadyMarked: false, status: attendanceStatus };
      }

      if (code === 409) {
        Logger.log('Duplicate attendance record (409)');
        return {
          success: true,
          code: 409,
          userId: userId,
          meetingId: meetingId,
          alreadyMarked: true,
          status: attendanceStatus
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

// ==================== MAIN ATTENDANCE HANDLER ====================
function doPost(e) {
  try {
    Logger.log('=== doPost called ===');
    Logger.log('Request payload: ' + e.postData.contents);

    const data = JSON.parse(e.postData.contents);
    Logger.log('Parsed data: ' + JSON.stringify(data));

    // Determine section: from request data, or auto-detect by time
    var section = data.section ? data.section.toUpperCase() : null;

    // Attendance status will be determined server-side based on time (after section is resolved)
    var attendanceStatus = 'Present'; // default, overridden below

    // STEP 1: Validate section
    if (section && !SECTIONS[section]) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: 'Invalid section: ' + section + '. Valid sections are: A, B.',
        errorType: 'invalid_section'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // STEP 2: Check schedule (also auto-detects section if not provided)
    var scheduleCheck = isWithinSchedule(section);
    if (!scheduleCheck.allowed) {
      Logger.log('REJECTED: Outside schedule - ' + scheduleCheck.reason);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: scheduleCheck.reason,
        errorType: 'schedule',
        outsideSchedule: true
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Use detected section if not explicitly provided
    if (!section) {
      section = scheduleCheck.section;
    }

    var courseId = SECTIONS[section].courseId;

    // Determine Present/Late based on server time vs class start + grace period
    var schedule = SECTION_SCHEDULES[section];
    var now = new Date();
    var currentHour = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'HH'));
    var currentMinute = parseInt(Utilities.formatDate(now, SCHEDULE_TIMEZONE, 'mm'));
    var currentTimeMinutes = currentHour * 60 + currentMinute;
    var classStartMinutes = schedule.startHour * 60 + schedule.startMinute;
    var lateThresholdMinutes = classStartMinutes + LATE_THRESHOLD_MINUTES;

    if (currentTimeMinutes >= lateThresholdMinutes) {
      attendanceStatus = 'Late';
    } else {
      attendanceStatus = 'Present';
    }
    Logger.log('Time-based status: class starts at ' + classStartMinutes + ', late after ' + lateThresholdMinutes + ', current=' + currentTimeMinutes + ' → ' + attendanceStatus);
    Logger.log('Using section: ' + section + ' (course: ' + courseId + ', status: ' + attendanceStatus + ')');

    // STEP 3: Check for duplicate device submission today
    if (data.userAgent) {
      var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
      var lastRow = sheet.getLastRow();
      if (lastRow > 0) {
        var todayStr = Utilities.formatDate(new Date(), SCHEDULE_TIMEZONE, 'yyyy-MM-dd');
        // Check recent rows (last 200) for same userAgent today
        var startRow = Math.max(1, lastRow - 200);
        var numRows = lastRow - startRow + 1;
        var dataRange = sheet.getRange(startRow, 1, numRows, 16).getValues();
        for (var i = 0; i < dataRange.length; i++) {
          var rowDate = dataRange[i][0];
          if (rowDate instanceof Date) {
            var rowDateStr = Utilities.formatDate(rowDate, SCHEDULE_TIMEZONE, 'yyyy-MM-dd');
            var rowUserAgent = dataRange[i][15]; // column 16 (0-indexed: 15)
            if (rowDateStr === todayStr && rowUserAgent === data.userAgent) {
              var existingStudent = dataRange[i][1]; // email column
              Logger.log('REJECTED: Duplicate device. Already submitted for ' + existingStudent + ' from same device.');
              return ContentService.createTextOutput(JSON.stringify({
                success: false,
                message: 'This device has already been used to check in today. One check-in per device per day.',
                errorType: 'duplicate_device'
              })).setMimeType(ContentService.MimeType.JSON);
            }
          }
        }
      }
    }

    // STEP 4: Check location (if provided)
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

    // STEP 5: Check Blackboard enrollment and mark attendance
    var bbResult = markAttendanceInBlackboard(data.email, courseId, attendanceStatus);

    // STEP 6: If not enrolled, reject completely
    if (bbResult.notEnrolled) {
      Logger.log('REJECTED: Student not enrolled - ' + data.email + ' in section ' + section);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: 'You are not enrolled in ' + SECTIONS[section].name + '. Please contact your instructor.',
        errorType: 'enrollment',
        blackboard: 'not_enrolled',
        section: section,
        bbError: bbResult.error
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // STEP 7: Check if Blackboard sync failed (non-enrollment errors)
    if (!bbResult.success) {
      Logger.log('REJECTED: Blackboard sync failed - ' + bbResult.error);
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        message: 'Unable to record attendance in Blackboard: ' + bbResult.error,
        errorType: 'blackboard_sync',
        blackboard: 'failed',
        section: section,
        bbError: bbResult.error
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // STEP 8: Write to Google Sheet
    var writeSheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    writeSheet.appendRow([
      new Date(),
      data.email,
      data.sessionTime,
      data.name.split(' ')[0] || data.name,
      data.name.split(' ').slice(1).join(' ') || '',
      (data.latitude || '') + ', ' + (data.longitude || ''),
      data.distance,
      section,
      attendanceStatus,
      bbResult.status || attendanceStatus,
      data.email,
      data.name,
      data.latitude,
      data.longitude,
      data.distance,
      data.userAgent || ''
    ]);

    // STEP 9: Return success
    var statusLabel = bbResult.alreadyMarked
      ? 'Your attendance was already recorded as ' + bbResult.status + ' for this session.'
      : 'Attendance recorded as ' + attendanceStatus + ' for ' + SECTIONS[section].name + '!';

    return ContentService.createTextOutput(JSON.stringify({
      success: true,
      message: statusLabel,
      blackboard: 'synced',
      section: section,
      bbDetails: {
        userId: bbResult.userId,
        meetingId: bbResult.meetingId,
        alreadyMarked: bbResult.alreadyMarked || false,
        status: bbResult.status || attendanceStatus,
        courseId: courseId
      }
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log('doPost error: ' + error.toString());
    Logger.log('Error stack: ' + error.stack);
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: 'Server error: ' + error.toString(),
      errorType: 'server_error',
      stack: error.stack,
      details: 'Full error logged to Apps Script execution log'
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput('Math Stat II Attendance API is running. Sections: A (_17607_1), B (_17609_1)');
}

// ==================== TEST FUNCTIONS ====================
function testBlackboardConnection() {
  Logger.log('=== Testing Blackboard Connection ===');
  Logger.log('Base URL: ' + BB_CONFIG.baseUrl);
  Logger.log('Sections: ' + JSON.stringify(SECTIONS));

  var token = getBlackboardToken();
  Logger.log('Token: ' + (token ? 'OK (' + token.substring(0,20) + '...)' : 'FAILED'));

  if (token) {
    var testUsername = 'sorujov';
    var userId = getBBUserId(testUsername, token);
    Logger.log('User lookup (' + testUsername + '): ' + (userId || 'NOT FOUND'));

    if (userId) {
      // Test enrollment in both sections
      var sections = Object.keys(SECTIONS);
      for (var i = 0; i < sections.length; i++) {
        var sec = sections[i];
        var enrolled = isEnrolledInCourse(userId, SECTIONS[sec].courseId, token);
        Logger.log('Enrollment in ' + SECTIONS[sec].name + ': ' + (enrolled ? 'ENROLLED' : 'NOT ENROLLED'));

        if (enrolled) {
          var meetingId = getOrCreateTodayMeeting(SECTIONS[sec].courseId, token);
          Logger.log('Today meeting for ' + sec + ': ' + (meetingId || 'FAILED'));
        }
      }
    }
  }

  Logger.log('=== Test Complete ===');
}

function testSchedule() {
  Logger.log('=== Testing Schedule Validation ===');

  // Test auto-detection
  var detected = detectSection();
  Logger.log('Auto-detected section: ' + (detected || 'NONE'));

  // Test each section's schedule
  var sections = Object.keys(SECTION_SCHEDULES);
  for (var i = 0; i < sections.length; i++) {
    var result = isWithinSchedule(sections[i]);
    Logger.log('Section ' + sections[i] + ' schedule check: ' + JSON.stringify(result));
  }

  // Test without section (auto-detect)
  var autoResult = isWithinSchedule(null);
  Logger.log('Auto-detect schedule check: ' + JSON.stringify(autoResult));

  Logger.log('=== Test Complete ===');
}

function testEnrollmentBothSections() {
  Logger.log('=== Testing Enrollment in Both Sections ===');

  var token = getBlackboardToken();
  if (!token) {
    Logger.log('Failed to get token');
    return;
  }

  var testUsername = 'sorujov';
  var userId = getBBUserId(testUsername, token);
  if (!userId) {
    Logger.log('User not found: ' + testUsername);
    return;
  }

  var sections = Object.keys(SECTIONS);
  for (var i = 0; i < sections.length; i++) {
    var sec = sections[i];
    var enrolled = isEnrolledInCourse(userId, SECTIONS[sec].courseId, token);
    Logger.log(SECTIONS[sec].name + ': ' + (enrolled ? 'ENROLLED' : 'NOT ENROLLED'));
  }

  Logger.log('=== Test Complete ===');
}

function testAttendanceMarking() {
  Logger.log('=== Testing Attendance Marking ===');

  // Test marking as Present in Section A
  var resultA = markAttendanceInBlackboard('sorujov@ada.edu.az', SECTIONS.A.courseId, 'Present');
  Logger.log('Section A Present: ' + JSON.stringify(resultA));

  // Test marking as Late in Section B
  var resultB = markAttendanceInBlackboard('sorujov@ada.edu.az', SECTIONS.B.courseId, 'Late');
  Logger.log('Section B Late: ' + JSON.stringify(resultB));

  Logger.log('=== Test Complete ===');
}

function clearTokenCache() {
  CacheService.getScriptCache().remove('bb_token');
  Logger.log('Token cache cleared');
}

function testAllErrorScenarios() {
  Logger.log('=== Testing All Error Scenarios ===\n');

  // Test 1: Schedule validation for each section
  Logger.log('TEST 1: Schedule Validation');
  var scheduleA = isWithinSchedule('A');
  Logger.log('Section A: ' + JSON.stringify(scheduleA));
  var scheduleB = isWithinSchedule('B');
  Logger.log('Section B: ' + JSON.stringify(scheduleB));
  var scheduleAuto = isWithinSchedule(null);
  Logger.log('Auto-detect: ' + JSON.stringify(scheduleAuto));
  Logger.log('');

  // Test 2: Location validation - on campus
  Logger.log('TEST 2: Location Validation - On Campus');
  var onCampusResult = isWithinCampus(40.39476586000145, 49.84937393783448);
  Logger.log('Result: ' + JSON.stringify(onCampusResult));
  Logger.log('');

  // Test 3: Location validation - far away
  Logger.log('TEST 3: Location Validation - Too Far');
  var farAwayResult = isWithinCampus(40.4095, 49.9671);
  Logger.log('Result: ' + JSON.stringify(farAwayResult));
  Logger.log('');

  // Test 4: Location validation - missing data
  Logger.log('TEST 4: Location Validation - Missing Data');
  var missingDataResult = isWithinCampus(null, null);
  Logger.log('Result: ' + JSON.stringify(missingDataResult));
  Logger.log('');

  // Test 5: Section detection
  Logger.log('TEST 5: Section Auto-Detection');
  var detectedSection = detectSection();
  Logger.log('Detected: ' + (detectedSection || 'NONE (outside all class times)'));
  Logger.log('');

  Logger.log('=== All Tests Complete ===');
  Logger.log('\nSummary:');
  Logger.log('Section A schedule: ' + (scheduleA.allowed ? 'PASS (within schedule)' : 'EXPECTED (outside schedule)'));
  Logger.log('Section B schedule: ' + (scheduleB.allowed ? 'PASS (within schedule)' : 'EXPECTED (outside schedule)'));
  Logger.log('On-campus location: ' + (onCampusResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('Far location rejection: ' + (!farAwayResult.allowed ? 'PASS' : 'FAIL'));
  Logger.log('Missing location rejection: ' + (!missingDataResult.allowed ? 'PASS' : 'FAIL'));
}
