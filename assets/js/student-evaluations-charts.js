// Student Evaluations Charts - Mathematical Statistics I
// This script initializes Chart.js visualizations for student evaluation data

document.addEventListener('DOMContentLoaded', function() {
  // Course Ratings Bar Chart
  const ctxBar = document.getElementById('courseRatingsChart');
  if (ctxBar) {
    new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: ['Overall Course', 'Exercise Sessions', 'Lectures', 'Real-life Link', 'Organization', 'Participation', 'Availability', 'Clarity'],
        datasets: [{
          label: 'Average Rating (out of 5)',
          data: [4.56, 4.45, 4.61, 4.15, 4.69, 4.68, 4.73, 4.75],
          backgroundColor: [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(76, 175, 80, 0.8)',
            'rgba(76, 175, 80, 0.8)',
            'rgba(76, 175, 80, 0.8)',
            'rgba(76, 175, 80, 0.8)'
          ],
          borderColor: [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(76, 175, 80, 1)',
            'rgba(76, 175, 80, 1)',
            'rgba(76, 175, 80, 1)',
            'rgba(76, 175, 80, 1)'
          ],
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          y: {
            beginAtZero: true,
            max: 5,
            ticks: {
              stepSize: 1
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          title: {
            display: true,
            text: 'Student Ratings Across All Metrics',
            font: {
              size: 16
            }
          }
        }
      }
    });
  }

  // Teacher Effectiveness Radar Chart
  const ctxRadar = document.getElementById('teacherRadarChart');
  if (ctxRadar) {
    new Chart(ctxRadar, {
      type: 'radar',
      data: {
        labels: ['Organization', 'Participation', 'Availability', 'Clarity'],
        datasets: [{
          label: 'Teacher Rating',
          data: [4.69, 4.68, 4.73, 4.75],
          fill: true,
          backgroundColor: 'rgba(76, 175, 80, 0.2)',
          borderColor: 'rgba(76, 175, 80, 1)',
          pointBackgroundColor: 'rgba(76, 175, 80, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(76, 175, 80, 1)'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          r: {
            beginAtZero: true,
            max: 5,
            ticks: {
              stepSize: 1
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }

  // Attendance Distribution Pie Chart
  const ctxAttendance = document.getElementById('attendanceChart');
  if (ctxAttendance) {
    new Chart(ctxAttendance, {
      type: 'pie',
      data: {
        labels: ['90-100%', '80-89%', '70-79%', '50-69%', '0-49%'],
        datasets: [{
          data: [53, 11, 6, 3, 2],
          backgroundColor: [
            'rgba(76, 175, 80, 0.8)',
            'rgba(102, 126, 234, 0.8)',
            'rgba(255, 193, 7, 0.8)',
            'rgba(255, 152, 0, 0.8)',
            'rgba(244, 67, 54, 0.8)'
          ],
          borderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom'
          },
          title: {
            display: true,
            text: 'Student Attendance Rates',
            font: {
              size: 14
            }
          }
        }
      }
    });
  }
});
