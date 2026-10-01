/**
 * HEALTHSYNC AI — National Health Command Center
 * Client Application Logic
 */

document.addEventListener('DOMContentLoaded', function () {
  initLiveClock();
  initSidebarToggle();
  initDashboardChart();
  initWhatIfSimulator();
  initHospitalRadarMap();
});

// ============================================================
// 1. LIVE COMMAND CENTER CLOCK
// ============================================================
function initLiveClock() {
  const clockEl = document.getElementById('liveClock');
  if (!clockEl) return;

  function update() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    const timeStr = now.toLocaleTimeString('en-GB', { hour12: false });
    clockEl.textContent = `${dateStr} ${timeStr} IST`;
  }
  update();
  setInterval(update, 1000);
}

// ============================================================
// 2. SIDEBAR TOGGLE FOR MOBILE
// ============================================================
function initSidebarToggle() {
  const toggleBtn = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (!toggleBtn || !sidebar) return;

  toggleBtn.addEventListener('click', function () {
    sidebar.classList.toggle('show');
  });

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function (e) {
    if (window.innerWidth < 992 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
      sidebar.classList.remove('show');
    }
  });
}

// ============================================================
// 3. TOAST NOTIFICATIONS
// ============================================================
function showToast(message, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container-custom';
    document.body.appendChild(container);
  }

  const toastId = 'toast_' + Date.now();
  const bgClass = type === 'success' ? 'bg-success text-white' :
                  type === 'danger' ? 'bg-danger text-white' :
                  type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

  const html = `
    <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 show shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center">
          <i class="fa-solid fa-circle-info me-2"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="document.getElementById('${toastId}').remove()"></button>
      </div>
    </div>
  `;
  container.insertAdjacentHTML('beforeend', html);

  setTimeout(() => {
    const el = document.getElementById(toastId);
    if (el) el.remove();
  }, 4500);
}

// ============================================================
// 4. DASHBOARD CHART (AI DEMAND FORECAST)
// ============================================================
let demandChartInstance = null;

function initDashboardChart() {
  const canvas = document.getElementById('demandForecastChart');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');

  // Baseline 7-day data
  const data7 = {
    labels: ['Day -6', 'Day -5', 'Day -4', 'Day -3', 'Day -2', 'Yesterday', 'Today'],
    actual: [480, 510, 495, 540, 560, 590, 620],
    predicted: [490, 505, 515, 535, 575, 610, 638]
  };

  const data30 = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    actual: [3400, 3620, 3890, 4100],
    predicted: [3450, 3700, 3980, 4310]
  };

  const data90 = {
    labels: ['Month 1', 'Month 2', 'Month 3'],
    actual: [14200, 15800, 16900],
    predicted: [14500, 16200, 18100]
  };

  demandChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data7.labels,
      datasets: [
        {
          label: 'Actual Demand (Units)',
          data: data7.actual,
          borderColor: '#0284c7',
          backgroundColor: 'rgba(2, 132, 199, 0.08)',
          borderWidth: 2.5,
          tension: 0.3,
          fill: true
        },
        {
          label: 'AI Predicted Demand (Units)',
          data: data7.predicted,
          borderColor: '#7928ca',
          backgroundColor: 'transparent',
          borderWidth: 2.5,
          borderDash: [5, 5],
          tension: 0.3,
          pointBackgroundColor: '#7928ca'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { font: { family: 'Inter', size: 12, weight: 600 } }
        },
        tooltip: {
          backgroundColor: '#0b132b',
          titleFont: { size: 13, weight: 'bold' },
          bodyFont: { size: 12 },
          padding: 10,
          cornerRadius: 8
        }
      },
      scales: {
        y: {
          beginAtZero: false,
          grid: { color: 'rgba(0, 0, 0, 0.05)' }
        },
        x: {
          grid: { display: false }
        }
      }
    }
  });

  // Window switch buttons
  document.querySelectorAll('.forecast-window-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.forecast-window-btn').forEach(b => b.classList.remove('active', 'btn-primary'));
      document.querySelectorAll('.forecast-window-btn').forEach(b => b.classList.add('btn-outline-primary'));
      this.classList.add('active', 'btn-primary');
      this.classList.remove('btn-outline-primary');

      const window = this.dataset.window;
      let activeData = data7;
      if (window === '30') activeData = data30;
      if (window === '90') activeData = data90;

      demandChartInstance.data.labels = activeData.labels;
      demandChartInstance.data.datasets[0].data = activeData.actual;
      demandChartInstance.data.datasets[1].data = activeData.predicted;
      demandChartInstance.update();
    });
  });
}

// ============================================================
// 5. WHAT-IF SIMULATOR ENGINE (INNOVATION 6)
// ============================================================
function initWhatIfSimulator() {
  const container = document.getElementById('whatIfContainer');
  if (!container) return;

  const buttons = document.querySelectorAll('.what-if-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', function () {
      buttons.forEach(b => b.classList.remove('active', 'btn-primary'));
      buttons.forEach(b => b.classList.add('btn-outline-secondary'));
      this.classList.add('active', 'btn-primary');
      this.classList.remove('btn-outline-secondary');

      const increasePct = parseFloat(this.dataset.percent);
      runWhatIfSimulation(increasePct);
    });
  });
}

function runWhatIfSimulation(percent) {
  const statusEl = document.getElementById('whatIfStatus');
  if (statusEl) statusEl.textContent = 'Simulating...';

  fetch('/api/forecast/what-if', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ demand_increase: percent })
  })
    .then(res => res.json())
    .then(data => {
      if (!data.success) {
        showToast('Simulation failed: ' + data.error, 'danger');
        return;
      }

      const sim = data.simulation;
      if (statusEl) statusEl.textContent = `Simulation active: +${percent}% Demand`;

      // Update UI metrics
      const bedEl = document.getElementById('simBedOccupancy');
      if (bedEl) bedEl.textContent = sim.simulated_bed_occupancy + '%';

      const alertEl = document.getElementById('simAlertCount');
      if (alertEl) alertEl.textContent = sim.simulated_alert_count;

      const critPhcEl = document.getElementById('simCritPhcs');
      if (critPhcEl) critPhcEl.textContent = sim.simulated_crit_phcs;

      const critMedsEl = document.getElementById('simCritMeds');
      if (critMedsEl) critMedsEl.textContent = sim.critical_medicines_count;

      const deficitEl = document.getElementById('simDeficitUnits');
      if (deficitEl) deficitEl.textContent = sim.total_shortage_units.toLocaleString() + ' units';

      // Dynamically update Resource Risk Index - Staff Strain and Composite Score
      if (sim.simulated_staff_strain !== undefined) {
        const staffStrainText = document.getElementById('riskStaffStrainText');
        const staffStrainBar = document.getElementById('riskStaffStrainBar');
        const staffStrainDetail = document.getElementById('riskStaffStrainDetail');
        if (staffStrainText) staffStrainText.textContent = sim.simulated_staff_strain + '%';
        if (staffStrainBar) {
          staffStrainBar.style.width = sim.simulated_staff_strain + '%';
          staffStrainBar.className = 'progress-bar ' + (sim.simulated_staff_strain >= 80 ? 'bg-danger' : sim.simulated_staff_strain >= 70 ? 'bg-warning' : 'bg-info');
        }
        if (staffStrainDetail) {
          staffStrainDetail.innerHTML = `<i class="fa-solid fa-bolt text-warning me-1"></i>Simulated: +${percent}% workload`;
        }
      }

      if (sim.simulated_risk_index) {
        const overallEl = document.getElementById('riskOverallNumber');
        const badgeEl = document.getElementById('riskOverallBadge');
        const bedText = document.getElementById('riskBedOccupancyText');
        const bedBar = document.getElementById('riskBedOccupancyBar');
        const medText = document.getElementById('riskMedPressureText');
        const medBar = document.getElementById('riskMedPressureBar');
        const surgeText = document.getElementById('riskPatientSurgeText');
        const surgeBar = document.getElementById('riskPatientSurgeBar');

        if (overallEl) overallEl.textContent = sim.simulated_risk_index.overall;
        if (badgeEl) {
          badgeEl.textContent = sim.simulated_risk_index.severity;
          badgeEl.className = 'badge ' + (sim.simulated_risk_index.severity === 'CRITICAL' ? 'bg-danger' : 'bg-warning text-dark');
        }
        if (bedText) bedText.textContent = sim.simulated_risk_index.bed_pressure + '%';
        if (bedBar) bedBar.style.width = sim.simulated_risk_index.bed_pressure + '%';
        if (medText) medText.textContent = sim.simulated_risk_index.medicine_pressure + '%';
        if (medBar) medBar.style.width = sim.simulated_risk_index.medicine_pressure + '%';
        if (surgeText) surgeText.textContent = sim.simulated_risk_index.patient_surge + '%';
        if (surgeBar) surgeBar.style.width = sim.simulated_risk_index.patient_surge + '%';
      }

      // Update table if present
      const tableBody = document.getElementById('whatIfTableBody');
      if (tableBody && sim.all_medicines) {
        tableBody.innerHTML = '';
        sim.all_medicines.forEach(m => {
          const badgeClass = m.risk_level === 'CRITICAL' ? 'badge-critical' :
                            m.risk_level === 'HIGH' ? 'badge-high' :
                            m.risk_level === 'MEDIUM' ? 'badge-medium' : 'badge-low';
          const row = `
            <tr>
              <td class="fw-semibold">${m.medicine_name}</td>
              <td>${m.current_stock.toLocaleString()} ${m.unit}</td>
              <td>${m.daily_usage} / day</td>
              <td class="text-primary fw-bold">${m.predicted_7d.toLocaleString()} ${m.unit}</td>
              <td class="fw-bold">${m.stockout_days} days</td>
              <td><span class="badge ${badgeClass}">${m.risk_level}</span></td>
              <td class="small text-muted">${m.reason}</td>
            </tr>
          `;
          tableBody.insertAdjacentHTML('beforeend', row);
        });
      }

      showToast(`What-If stress test (+${percent}% demand) calculated successfully!`, 'primary');
    })
    .catch(err => {
      console.error(err);
      showToast('Error running simulation.', 'danger');
    });
}

// ============================================================
// 6. ALERT RESOLUTION (AJAX)
// ============================================================
function resolveAlert(alertId) {
  if (!confirm(`Resolve alert #${alertId}? This will log an audit event.`)) return;

  fetch(`/api/alerts/${alertId}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        const row = document.getElementById(`alertRow_${alertId}`);
        if (row) {
          row.style.opacity = '0.5';
          const badge = row.querySelector('.alert-status-badge');
          if (badge) {
            badge.className = 'badge bg-secondary';
            badge.textContent = 'RESOLVED';
          }
          const btn = row.querySelector('.resolve-btn');
          if (btn) btn.remove();
        }
      } else {
        showToast(data.error || 'Failed to resolve alert', 'danger');
      }
    })
    .catch(err => {
      console.error(err);
      showToast('Network error resolving alert.', 'danger');
    });
}

// ============================================================
// 7. REDISTRIBUTION APPROVE & REJECT (AJAX)
// ============================================================
function approveRedistribution(redistId) {
  if (!confirm(`Are you sure you want to APPROVE redistribution proposal #${redistId}? Medicine stocks will be updated.`)) return;

  fetch(`/api/redistribution/${redistId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'success');
        setTimeout(() => window.location.reload(), 1200);
      } else {
        showToast(data.error || 'Failed to approve redistribution', 'danger');
      }
    })
    .catch(err => {
      console.error(err);
      showToast('Error approving transfer.', 'danger');
    });
}

function rejectRedistribution(redistId) {
  if (!confirm(`Are you sure you want to REJECT proposal #${redistId}?`)) return;

  fetch(`/api/redistribution/${redistId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        showToast(data.message, 'info');
        setTimeout(() => window.location.reload(), 1200);
      } else {
        showToast(data.error || 'Failed to reject redistribution', 'danger');
      }
    })
    .catch(err => {
      console.error(err);
      showToast('Error rejecting transfer.', 'danger');
    });
}

// ============================================================
// 8. FEDERATED LEARNING ROUND SIMULATION (INNOVATION 7)
// ============================================================
function triggerFederatedRound() {
  const btn = document.getElementById('btnStartFederatedRound');
  const spinner = document.getElementById('federatedSpinner');
  if (btn) btn.disabled = true;
  if (spinner) spinner.classList.remove('d-none');

  showToast('Initiating Federated Round: Dispatching local training parameters to 5 PHC edge nodes...', 'primary');

  setTimeout(() => {
    fetch('/api/federated/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(`Round ${data.details.round_number} Completed! Global accuracy reached ${data.details.accuracy}% (+${data.details.accuracy_gain}%).`, 'success');
          setTimeout(() => window.location.reload(), 1500);
        } else {
          showToast('Failed to trigger federated round.', 'danger');
          if (btn) btn.disabled = false;
          if (spinner) spinner.classList.add('d-none');
        }
      })
      .catch(err => {
        console.error(err);
        showToast('Error executing federated round.', 'danger');
        if (btn) btn.disabled = false;
        if (spinner) spinner.classList.add('d-none');
      });
  }, 1000);
}

// ============================================================
// 9. CLIENT FILTERING UTILITIES
// ============================================================
function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('keyup', function () {
    const filter = input.value.toLowerCase();
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
      const row = rows[i];
      const text = row.textContent.toLowerCase();
      if (text.includes(filter)) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    }
  });
}

// ============================================================
// 10. GIS REAL-TIME HOSPITAL RADAR & GOOGLE MAPS PROXIMITY
// ============================================================
let hospitalMap = null;
let userLiveMarker = null;
let radarRangeCircle = null;
let hospitalMarkersMap = {};
let currentRadarHospitals = [];
let currentRadarRadius = 10.0;
let userCurrentLat = 22.5396; // Default to Central Kolkata Hub (SSKM)
let userCurrentLon = 88.3426;
let mapStreetLayer = null;
let mapSatelliteLayer = null;

function initHospitalRadarMap() {
  const mapContainer = document.getElementById('hospitalRadarMap');
  if (!mapContainer || typeof L === 'undefined') return;

  // Initialize Tile Layers (Google Maps styled tiles)
  mapStreetLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '&copy; Google Maps / OpenStreetMap contributors'
  });

  mapSatelliteLayer = L.tileLayer('https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    attribution: '&copy; Google Maps / OpenStreetMap contributors'
  });

  // Create Leaflet Map Instance
  hospitalMap = L.map('hospitalRadarMap', {
    center: [userCurrentLat, userCurrentLon],
    zoom: 12,
    layers: [mapStreetLayer],
    zoomControl: false
  });

  // Add zoom control at top-left
  L.control.zoom({ position: 'topleft' }).addTo(hospitalMap);

  // Setup Layer Toggle Buttons
  const btnStreet = document.getElementById('btnLayerStreet');
  const btnSatellite = document.getElementById('btnLayerSatellite');
  if (btnStreet && btnSatellite) {
    btnStreet.addEventListener('click', function () {
      btnStreet.classList.add('active');
      btnSatellite.classList.remove('active');
      if (hospitalMap.hasLayer(mapSatelliteLayer)) {
        hospitalMap.removeLayer(mapSatelliteLayer);
      }
      if (!hospitalMap.hasLayer(mapStreetLayer)) {
        hospitalMap.addLayer(mapStreetLayer);
      }
    });

    btnSatellite.addEventListener('click', function () {
      btnSatellite.classList.add('active');
      btnStreet.classList.remove('active');
      if (hospitalMap.hasLayer(mapStreetLayer)) {
        hospitalMap.removeLayer(mapStreetLayer);
      }
      if (!hospitalMap.hasLayer(mapSatelliteLayer)) {
        hospitalMap.addLayer(mapSatelliteLayer);
      }
    });
  }

  // Setup Recenter Button (Google Maps crosshair)
  const btnRecenter = document.getElementById('btnMapRecenter');
  if (btnRecenter) {
    btnRecenter.addEventListener('click', function () {
      if (hospitalMap) {
        hospitalMap.setView([userCurrentLat, userCurrentLon], 13, { animate: true });
        if (userLiveMarker) {
          userLiveMarker.openTooltip();
        }
      }
    });
  }

  // Setup Radar Radius Buttons (5, 10, 15, 20 km, All)
  const radiusButtons = document.querySelectorAll('.radar-range-btn');
  radiusButtons.forEach(btn => {
    btn.addEventListener('click', function () {
      radiusButtons.forEach(b => b.classList.remove('active', 'btn-primary'));
      radiusButtons.forEach(b => b.classList.add('btn-outline-primary'));
      this.classList.remove('btn-outline-primary');
      this.classList.add('active', 'btn-primary');

      currentRadarRadius = parseFloat(this.getAttribute('data-radius')) || 0;
      updateRadarOverlayAndFetchHospitals(true);
    });
  });

  // Setup Refresh / Detect Location Button
  const btnRefreshLoc = document.getElementById('btnRefreshLocation');
  if (btnRefreshLoc) {
    btnRefreshLoc.addEventListener('click', function () {
      requestUserLiveLocation();
    });
  }

  // Setup Preset Hub Buttons
  const presetButtons = document.querySelectorAll('.preset-location-btn');
  presetButtons.forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const lat = parseFloat(this.getAttribute('data-lat'));
      const lon = parseFloat(this.getAttribute('data-lon'));
      const name = this.getAttribute('data-name');
      if (!isNaN(lat) && !isNaN(lon)) {
        userCurrentLat = lat;
        userCurrentLon = lon;
        updateLocationStatusUI(`Hub Locked: ${name}`, 'success');
        showToast(`Switched location to ${name}`, 'success');
        updateRadarOverlayAndFetchHospitals(true);
      }
    });
  });

  // Custom Coords Prompt
  const btnCustomPrompt = document.getElementById('btnCustomCoordsPrompt');
  if (btnCustomPrompt) {
    btnCustomPrompt.addEventListener('click', function (e) {
      e.preventDefault();
      const input = prompt('Enter coordinates as "Latitude, Longitude" (e.g. 22.5726, 88.3639):', `${userCurrentLat}, ${userCurrentLon}`);
      if (input) {
        const parts = input.split(',');
        if (parts.length === 2) {
          const lat = parseFloat(parts[0].trim());
          const lon = parseFloat(parts[1].trim());
          if (!isNaN(lat) && !isNaN(lon)) {
            userCurrentLat = lat;
            userCurrentLon = lon;
            updateLocationStatusUI(`Custom: ${lat.toFixed(4)}°, ${lon.toFixed(4)}°`, 'success');
            showToast(`Target set to ${lat.toFixed(4)}, ${lon.toFixed(4)}`, 'success');
            updateRadarOverlayAndFetchHospitals(true);
          } else {
            alert('Invalid coordinates entered.');
          }
        }
      }
    });
  }

  // Setup Real-time Search and Status Filter
  const searchInput = document.getElementById('mapHospitalSearch');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      filterAndRenderHospitalList();
    });
  }

  const statusSelect = document.getElementById('mapStatusFilter');
  if (statusSelect) {
    statusSelect.addEventListener('change', function () {
      filterAndRenderHospitalList();
    });
  }

  const sortSelect = document.getElementById('hospitalSortSelect');
  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      filterAndRenderHospitalList();
    });
  }

  // Automatically request live geolocation upon load
  requestUserLiveLocation();
}

function updateLocationStatusUI(message, state = 'info') {
  const textEl = document.getElementById('gpsStatusText');
  const dotEl = document.getElementById('gpsPulseDot');
  if (textEl) textEl.textContent = message;
  if (dotEl) {
    dotEl.className = 'pulse-dot me-2 ' +
      (state === 'success' ? 'bg-success' :
       state === 'warning' ? 'bg-warning' :
       state === 'danger' ? 'bg-danger' : 'bg-primary');
  }
}

function requestUserLiveLocation() {
  updateLocationStatusUI('Requesting Live GPS access...', 'warning');

  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        userCurrentLat = pos.coords.latitude;
        userCurrentLon = pos.coords.longitude;
        const accuracy = Math.round(pos.coords.accuracy || 15);
        updateLocationStatusUI(`GPS Locked: ${userCurrentLat.toFixed(4)}°N, ${userCurrentLon.toFixed(4)}°E (±${accuracy}m)`, 'success');
        showToast(`Live location acquired (${userCurrentLat.toFixed(4)}, ${userCurrentLon.toFixed(4)})`, 'success');
        updateRadarOverlayAndFetchHospitals(true);
      },
      function (err) {
        console.warn('Geolocation permission/access warning:', err.message);
        updateLocationStatusUI('GPS Denied / Desktop (Using Command Hub)', 'warning');
        showToast('Using central command hub (Click "Detect My Location" or switch hub anytime)', 'warning');
        updateRadarOverlayAndFetchHospitals(true);
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 60000 }
    );
  } else {
    updateLocationStatusUI('Geolocation not supported (Using Command Hub)', 'warning');
    updateRadarOverlayAndFetchHospitals(true);
  }
}

function updateRadarOverlayAndFetchHospitals(shouldRefitBounds = false) {
  if (!hospitalMap) return;

  // 1. Update User Location Puck (Google Maps Blue Dot)
  const puckIcon = L.divIcon({
    className: 'user-live-puck-wrapper',
    html: `
      <div class="user-live-puck-container" title="Your Live GPS Location">
        <div class="user-live-puck-pulse"></div>
        <div class="user-live-puck-core"></div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });

  if (userLiveMarker) {
    userLiveMarker.setLatLng([userCurrentLat, userCurrentLon]);
  } else {
    userLiveMarker = L.marker([userCurrentLat, userCurrentLon], {
      icon: puckIcon,
      zIndexOffset: 2500
    }).addTo(hospitalMap);
    userLiveMarker.bindTooltip('📍 Your Live Location', { direction: 'top', offset: [0, -14] });
  }

  // 2. Update Radar Range Circle
  if (radarRangeCircle) {
    hospitalMap.removeLayer(radarRangeCircle);
    radarRangeCircle = null;
  }

  if (currentRadarRadius > 0) {
    radarRangeCircle = L.circle([userCurrentLat, userCurrentLon], {
      radius: currentRadarRadius * 1000,
      color: '#0284c7',
      weight: 2,
      fillColor: '#0284c7',
      fillOpacity: 0.08,
      dashArray: '6, 6'
    }).addTo(hospitalMap);

    if (shouldRefitBounds) {
      hospitalMap.fitBounds(radarRangeCircle.getBounds(), { padding: [35, 35], maxZoom: 15 });
    }
  } else if (shouldRefitBounds) {
    hospitalMap.setView([userCurrentLat, userCurrentLon], 10);
  }

  // 3. Update Radar Badges
  const radarLabel = currentRadarRadius > 0 ? `${currentRadarRadius} km Active` : 'All State Facilities';
  const badgeText = document.getElementById('mapRadarBadgeText');
  if (badgeText) badgeText.textContent = `Radar: ${radarLabel}`;

  const subtitle = document.getElementById('hospitalListSubtitle');
  if (subtitle) {
    subtitle.textContent = currentRadarRadius > 0
      ? `Within ${currentRadarRadius} km radar of your location`
      : 'All facilities across state network';
  }

  // 4. Fetch Nearby Hospitals from Backend
  const listContainer = document.getElementById('hospitalCardsContainer');
  if (listContainer) {
    listContainer.innerHTML = `
      <div class="text-center py-5 text-muted">
        <div class="spinner-border spinner-border-sm text-primary mb-2" role="status"></div>
        <div class="small">Scanning healthcare facilities in radar...</div>
      </div>
    `;
  }

  const url = `/api/hospitals/nearby?lat=${userCurrentLat}&lon=${userCurrentLon}&radius=${currentRadarRadius}`;
  fetch(url)
    .then(r => r.json())
    .then(data => {
      if (data.success) {
        currentRadarHospitals = data.hospitals || [];
        filterAndRenderHospitalList();
      } else {
        if (listContainer) {
          listContainer.innerHTML = `<div class="alert alert-danger small p-2 m-2">Failed to load hospitals.</div>`;
        }
      }
    })
    .catch(err => {
      console.error('Error fetching nearby hospitals:', err);
      if (listContainer) {
        listContainer.innerHTML = `<div class="alert alert-danger small p-2 m-2">Error connecting to telemetry.</div>`;
      }
    });
}

function filterAndRenderHospitalList() {
  const searchInput = document.getElementById('mapHospitalSearch');
  const statusSelect = document.getElementById('mapStatusFilter');
  const sortSelect = document.getElementById('hospitalSortSelect');

  const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
  const statusFilter = (statusSelect ? statusSelect.value : '').trim().toUpperCase();
  const sortBy = sortSelect ? sortSelect.value : 'distance_asc';

  // Filter
  let filtered = currentRadarHospitals.filter(h => {
    if (query) {
      const matchName = h.name.toLowerCase().includes(query);
      const matchCode = (h.phc_code || '').toLowerCase().includes(query);
      const matchDist = (h.district || '').toLowerCase().includes(query);
      if (!matchName && !matchCode && !matchDist) return false;
    }
    if (statusFilter && h.status !== statusFilter) {
      return false;
    }
    return true;
  });

  // Sort
  filtered.sort((a, b) => {
    if (sortBy === 'distance_asc') return a.distance_km - b.distance_km;
    if (sortBy === 'beds_desc') return b.available_beds - a.available_beds;
    if (sortBy === 'occupancy_desc') return b.bed_occupancy_rate - a.bed_occupancy_rate;
    if (sortBy === 'name_asc') return a.name.localeCompare(b.name);
    return 0;
  });

  // Update counts
  const countBadge = document.getElementById('hospitalListCountBadge');
  const radarCountPill = document.getElementById('mapRadarCountPill');
  if (countBadge) countBadge.textContent = filtered.length;
  if (radarCountPill) radarCountPill.textContent = `${filtered.length} Found`;

  // Render Map Markers
  renderHospitalMapMarkers(filtered);

  // Render Hospital Cards in Sidebar List
  const container = document.getElementById('hospitalCardsContainer');
  if (!container) return;

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="text-center py-5 px-3">
        <i class="fa-solid fa-magnifying-glass-location text-muted fs-1 mb-3"></i>
        <h6 class="fw-bold text-dark mb-1">No Hospitals Found in Radar</h6>
        <p class="text-muted small mb-3">No medical facilities found within ${currentRadarRadius > 0 ? currentRadarRadius + ' km' : 'current filter'}.</p>
        <div class="d-flex justify-content-center gap-2">
          <button class="btn btn-sm btn-outline-primary" onclick="setRadarRadius(10)">Expand to 10 km</button>
          <button class="btn btn-sm btn-primary" onclick="setRadarRadius(20)">Expand to 20 km</button>
        </div>
      </div>
    `;
    return;
  }

  let html = '';
  filtered.forEach(h => {
    const statusLower = (h.status || 'NORMAL').toLowerCase();
    const badgeClass =
      h.status === 'CRITICAL' ? 'badge-critical' :
      h.status === 'WARNING' ? 'badge-high' :
      h.status === 'WATCH' ? 'badge-medium' : 'badge-low';

    const occBg =
      h.bed_occupancy_rate >= 90 ? 'bg-danger' :
      h.bed_occupancy_rate >= 75 ? 'bg-warning' : 'bg-success';

    html += `
      <div class="hospital-radar-card" id="hospCard_${h.id}" onclick="locateHospitalOnMap(${h.id})">
        <div class="d-flex justify-content-between align-items-start mb-1">
          <div class="fw-bold text-dark text-truncate me-2" title="${h.name}">${h.name}</div>
          <span class="hospital-dist-badge"><i class="fa-solid fa-location-dot me-1"></i>${h.distance_km} km</span>
        </div>
        <div class="d-flex align-items-center justify-content-between small text-muted mb-2">
          <span>${h.district} • ${h.phc_code}</span>
          <span class="badge ${badgeClass}">${h.status}</span>
        </div>
        <div class="small mb-1">
          <div class="d-flex justify-content-between text-muted" style="font-size: 0.74rem;">
            <span>Available Beds: <strong>${h.available_beds}</strong> (${h.total_beds} total)</span>
            <span class="fw-semibold">${h.bed_occupancy_rate}% Occ.</span>
          </div>
          <div class="progress mt-1" style="height: 5px;">
            <div class="progress-bar ${occBg}" style="width: ${h.bed_occupancy_rate}%;"></div>
          </div>
        </div>
        <div class="d-flex justify-content-between align-items-center mt-2 pt-1 border-top" style="font-size: 0.72rem;">
          <span class="text-muted"><i class="fa-solid fa-user-doctor me-1"></i>Staff: ${h.staff_present}/${h.staff_total}</span>
          <div class="d-flex gap-1" onclick="event.stopPropagation()">
            <button class="btn btn-sm btn-light border py-0 px-2 text-primary" style="font-size: 0.72rem;" onclick="locateHospitalOnMap(${h.id})" title="Pan on Map">
              <i class="fa-solid fa-crosshairs me-1"></i>Map
            </button>
            <a href="${h.google_maps_url}" target="_blank" class="btn btn-sm btn-light border py-0 px-2 text-primary" style="font-size: 0.72rem;" title="Google Maps Directions">
              <i class="fa-brands fa-google me-1"></i>Route
            </a>
            <button class="btn btn-sm btn-light border py-0 px-2 text-secondary" style="font-size: 0.72rem;" onclick="openHospitalQuickModal(${h.id})" title="Full Details">
              <i class="fa-solid fa-circle-info"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}

function renderHospitalMapMarkers(hospitals) {
  if (!hospitalMap) return;

  // Clear previous markers
  Object.values(hospitalMarkersMap).forEach(m => hospitalMap.removeLayer(m));
  hospitalMarkersMap = {};

  hospitals.forEach(h => {
    if (h.latitude === null || h.longitude === null) return;

    const statusLower = (h.status || 'NORMAL').toLowerCase();
    const pinClass = `pin-${statusLower}`;

    const icon = L.divIcon({
      className: 'custom-hospital-marker-wrapper',
      html: `
        <div class="custom-hospital-marker ${pinClass}">
          <div class="hospital-pin-bubble">
            <i class="fa-solid fa-hospital"></i>
          </div>
          <div class="hospital-pin-badge">${h.distance_km} km</div>
        </div>
      `,
      iconSize: [36, 48],
      iconAnchor: [18, 44],
      popupAnchor: [0, -42]
    });

    const marker = L.marker([h.latitude, h.longitude], {
      icon: icon,
      title: h.name
    }).addTo(hospitalMap);

    const badgeClass =
      h.status === 'CRITICAL' ? 'badge-critical' :
      h.status === 'WARNING' ? 'badge-high' :
      h.status === 'WATCH' ? 'badge-medium' : 'badge-low';

    const occBg =
      h.bed_occupancy_rate >= 90 ? 'bg-danger' :
      h.bed_occupancy_rate >= 75 ? 'bg-warning' : 'bg-success';

    const popupHtml = `
      <div class="gm-popup-card">
        <div class="d-flex justify-content-between align-items-start mb-1">
          <h6 class="mb-0 text-truncate" title="${h.name}">${h.name}</h6>
          <span class="badge ${badgeClass} ms-1">${h.status}</span>
        </div>
        <div class="gm-popup-dist">
          <i class="fa-solid fa-location-arrow text-primary me-1"></i>${h.distance_km} km from your position
        </div>
        <div class="small text-muted mb-2">${h.district} • ${h.phc_code}</div>
        <div class="mb-2">
          <div class="gm-popup-beds-label">
            <span>Beds Available:</span>
            <strong class="text-dark">${h.available_beds} of ${h.total_beds}</strong>
          </div>
          <div class="progress" style="height: 6px;">
            <div class="progress-bar ${occBg}" style="width: ${h.bed_occupancy_rate}%;"></div>
          </div>
          <div class="d-flex justify-content-between text-muted" style="font-size: 0.7rem; margin-top: 2px;">
            <span>Occupancy: ${h.bed_occupancy_rate}%</span>
            <span>Staff: ${h.staff_present}/${h.staff_total}</span>
          </div>
        </div>
        <div class="d-flex gap-2 mt-2 pt-1 border-top">
          <a href="${h.google_maps_url}" target="_blank" class="btn btn-sm btn-primary flex-grow-1 py-1" style="font-size: 0.76rem;">
            <i class="fa-brands fa-google me-1"></i> Directions
          </a>
          <button class="btn btn-sm btn-outline-secondary py-1" style="font-size: 0.76rem;" onclick="openHospitalQuickModal(${h.id})">
            <i class="fa-solid fa-circle-info me-1"></i> Telemetry
          </button>
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml, { maxWidth: 300, closeButton: true });

    marker.on('click', function () {
      highlightHospitalCard(h.id);
    });

    hospitalMarkersMap[h.id] = marker;
  });
}

function locateHospitalOnMap(id) {
  if (!hospitalMap) return;

  highlightHospitalCard(id);

  const marker = hospitalMarkersMap[id];
  if (marker) {
    hospitalMap.setView(marker.getLatLng(), 15, { animate: true });
    marker.openPopup();
  }
}

function highlightHospitalCard(id) {
  document.querySelectorAll('.hospital-radar-card').forEach(c => c.classList.remove('active-card'));
  const card = document.getElementById(`hospCard_${id}`);
  if (card) {
    card.classList.add('active-card');
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function setRadarRadius(km) {
  const btn = document.querySelector(`.radar-range-btn[data-radius="${km}"]`);
  if (btn) {
    btn.click();
  } else {
    currentRadarRadius = km;
    updateRadarOverlayAndFetchHospitals(true);
  }
}

function openHospitalQuickModal(id) {
  const h = currentRadarHospitals.find(item => item.id === id);
  if (!h) return;

  const modalEl = document.getElementById('hospitalQuickDetailModal');
  if (!modalEl) return;

  const titleEl = document.getElementById('quickModalTitle');
  const bodyEl = document.getElementById('quickModalBody');
  const routeBtn = document.getElementById('quickModalGoogleMapsBtn');

  if (titleEl) titleEl.innerHTML = `<i class="fa-solid fa-hospital me-2 text-primary"></i>${h.phc_code} — ${h.name}`;
  if (routeBtn) routeBtn.href = h.google_maps_url;

  const badgeClass =
    h.status === 'CRITICAL' ? 'badge-critical' :
    h.status === 'WARNING' ? 'badge-high' :
    h.status === 'WATCH' ? 'badge-medium' : 'badge-low';

  const occBg =
    h.bed_occupancy_rate >= 90 ? 'bg-danger' :
    h.bed_occupancy_rate >= 75 ? 'bg-warning' : 'bg-success';

  if (bodyEl) {
    bodyEl.innerHTML = `
      <div class="row g-2 mb-3">
        <div class="col-6"><strong>District:</strong> ${h.district}</div>
        <div class="col-6"><strong>State:</strong> ${h.state}</div>
        <div class="col-6"><strong>Distance:</strong> <span class="text-primary fw-bold">${h.distance_km} km away</span></div>
        <div class="col-6"><strong>Operational Status:</strong> <span class="badge ${badgeClass}">${h.status}</span></div>
      </div>
      <hr>
      <div class="mb-2">
        <div class="d-flex justify-content-between">
          <strong>Inpatient Bed Capacity:</strong>
          <span>${h.occupied_beds} occupied / ${h.total_beds} total (${h.available_beds} free)</span>
        </div>
      </div>
      <div class="progress mb-3" style="height: 8px;">
        <div class="progress-bar ${occBg}" style="width: ${h.bed_occupancy_rate}%;"></div>
      </div>
      <div class="mb-2">
        <div class="d-flex justify-content-between">
          <strong>Clinical Staff on Duty:</strong>
          <span>${h.staff_present} of ${h.staff_total} (${h.staff_attendance_rate}%)</span>
        </div>
      </div>
      <div class="progress mb-3" style="height: 8px;">
        <div class="progress-bar bg-success" style="width: ${h.staff_attendance_rate}%;"></div>
      </div>
      <div class="row g-2 small text-muted">
        <div class="col-6"><strong>Patients Today:</strong> ${h.patients_today}</div>
        <div class="col-6"><strong>Coordinates:</strong> ${h.latitude}, ${h.longitude}</div>
      </div>
    `;
  }

  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

