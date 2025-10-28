(function(){
  const qs = sel => document.querySelector(sel);
  const qsv = sel => (qs(sel)?.value || '').trim();

  // Utility function to escape HTML and prevent XSS
  function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  const kpiTotalEl = qs('#kpi-total');
  let charts = {};

  const palette = {
    blue: '#3b82f6',
    blueFill: 'rgba(59,130,246,0.15)',
    green: '#22c55e',
    orange: '#f59e0b',
    purple: '#9333ea',
    gray: '#64748b',
    red: '#ef4444',
    yellow: '#f59e0b'
  };

  const commonOpts = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 800, easing: 'easeOutQuart' },
    plugins: {
      legend: { display: true, position: 'top' },
      tooltip: { enabled: true, mode: 'index', intersect: false },
    },
    scales: {
      x: { grid: { color: 'rgba(0,0,0,0.05)' } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, beginAtZero: true }
    }
  };

  function buildParams() {
    const params = new URLSearchParams();
    const range = qsv('#sitrep-range');
    const fromDate = qsv('#sitrep-from-date');
    const toDate = qsv('#sitrep-to-date');
    const sourcesSel = qs('#sitrep-sources');
    const sources = sourcesSel ? Array.from(sourcesSel.selectedOptions).map(o => o.value).join(',') : '';

    if (range) params.set('rangeDays', range);
    if (fromDate) params.set('fromDate', fromDate);
    if (toDate) params.set('toDate', toDate);
    if (sources) params.set('sources', sources);
    return params.toString();
  }

  async function fetchStats() {
    const query = buildParams();
    const url = '/api/sitreps/stats' + (query ? ('?' + query) : '');
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return await res.json();
  }

  function upsertChart(id, cfg) {
    const ctx = qs(id).getContext('2d');
    if (charts[id]) {
      charts[id].data = cfg.data;
      charts[id].options = cfg.options || charts[id].options;
      charts[id].update();
    } else {
      charts[id] = new Chart(ctx, cfg);
    }
  }

  function render(stats) {
    // KPI
    kpiTotalEl.textContent = stats.total || 0;

    // Time series
    const labelsTime = stats.by_day.map(d => d.day);
    const dataTime = stats.by_day.map(d => d.count);
    upsertChart('#chart-time', {
      type: 'line',
      data: {
        labels: labelsTime,
        datasets: [{
          label: 'Incidents',
          data: dataTime,
          borderColor: palette.blue,
          backgroundColor: palette.blueFill,
          tension: 0.3,
          fill: true,
          pointRadius: 2,
          pointHoverRadius: 4
        }]
      },
      options: {
        ...commonOpts,
        plugins: { ...commonOpts.plugins, title: { display: true, text: 'Incidents Over Time' } },
        scales: { ...commonOpts.scales, x: { ...commonOpts.scales.x, title: { display: true, text: 'Date' } } }
      }
    });

    // Severity
    const labelsSev = stats.by_severity.map(s => s.severity);
    const dataSev = stats.by_severity.map(s => s.count);
    upsertChart('#chart-severity', {
      type: 'doughnut',
      data: {
        labels: labelsSev,
        datasets: [{
          data: dataSev,
          backgroundColor: ['#ef4444','#f59e0b','#10b981','#6366f1','#6b7280','#22c55e','#f97316'],
          borderColor: '#ffffff',
          borderWidth: 2
        }]
      },
      options: {
        ...commonOpts,
        cutout: '55%',
        plugins: { ...commonOpts.plugins, title: { display: true, text: 'Severity Breakdown' } }
      }
    });

    // Source category
    const labelsSrc = stats.by_source_category.map(s => s.source_category);
    const dataSrc = stats.by_source_category.map(s => s.count);
    upsertChart('#chart-source', {
      type: 'bar',
      data: {
        labels: labelsSrc,
        datasets: [{
          label: 'By Source',
          data: dataSrc,
          backgroundColor: palette.green,
          borderRadius: 6,
          maxBarThickness: 32
        }]
      },
      options: {
        ...commonOpts,
        indexAxis: 'y',
        plugins: { ...commonOpts.plugins, title: { display: true, text: 'Source Category' } },
        scales: { ...commonOpts.scales, x: { ...commonOpts.scales.x, beginAtZero: true } }
      }
    });

    // Status
    const labelsSt = stats.by_status.map(s => s.status);
    const dataSt = stats.by_status.map(s => s.count);
    upsertChart('#chart-status', {
      type: 'bar',
      data: {
        labels: labelsSt,
        datasets: [{
          label: 'By Status',
          data: dataSt,
          backgroundColor: palette.orange,
          borderRadius: 6,
          maxBarThickness: 42
        }]
      },
      options: {
        ...commonOpts,
        plugins: { ...commonOpts.plugins, title: { display: true, text: 'Status' } },
        scales: { ...commonOpts.scales, y: { ...commonOpts.scales.y, beginAtZero: true } }
      }
    });

    // Top units
    const labelsUnits = stats.top_units.map(u => u.unit);
    const dataUnits = stats.top_units.map(u => u.count);
    upsertChart('#chart-units', {
      type: 'bar',
      data: {
        labels: labelsUnits,
        datasets: [{
          label: 'Top Units',
          data: dataUnits,
          backgroundColor: palette.purple,
          borderRadius: 6,
          maxBarThickness: 32
        }]
      },
      options: {
        ...commonOpts,
        indexAxis: 'y',
        plugins: { ...commonOpts.plugins, title: { display: true, text: 'Top Units' } },
        scales: { ...commonOpts.scales, x: { ...commonOpts.scales.x, beginAtZero: true } }
      }
    });
  }

  async function applyFilters() {
    try {
      const stats = await fetchStats();
      render(stats);
    } catch (e) {
      console.error(e);
      alert('Failed to load dashboard stats');
    }
  }

  // Ensure multi-select behavior for sources dropdown
  function initializeSourcesMultiSelect() {
    const sourcesSel = qs('#sitrep-sources');
    if (sourcesSel) {
      // Ensure multiple attribute is set
      sourcesSel.setAttribute('multiple', 'multiple');
      
      // Add event listener to handle multi-select behavior
      sourcesSel.addEventListener('mousedown', function(e) {
        e.preventDefault();
        const option = e.target;
        if (option.tagName === 'OPTION') {
          // Toggle selection state
          option.selected = !option.selected;
          
          // Trigger change event
          sourcesSel.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
      
      // Prevent default click behavior that might interfere
      sourcesSel.addEventListener('click', function(e) {
        e.preventDefault();
      });
    }
  }

  // Wire buttons
  qs('#sitrep-filter-apply')?.addEventListener('click', applyFilters);
  qs('#sitrep-filter-reset')?.addEventListener('click', () => {
    qs('#sitrep-range').value = '';
    qs('#sitrep-from-date').value = '';
    qs('#sitrep-to-date').value = '';
    const sourcesSel = qs('#sitrep-sources');
    if (sourcesSel) Array.from(sourcesSel.options).forEach(o => o.selected = false);
    applyFilters();
  });

  // AI Insights functionality
  qs('#ai-insights-btn')?.addEventListener('click', generateAIInsights);
  qs('#close-insights-modal')?.addEventListener('click', closeInsightsModal);
  qs('#ai-insights-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'ai-insights-modal') {
      closeInsightsModal();
    }
  });

  // Initialize multi-select behavior
  initializeSourcesMultiSelect();
  
  // Initial load
  applyFilters();

  // AI Insights Functions
  async function generateAIInsights(retryCount = 0) {
    const modal = qs('#ai-insights-modal');
    const loading = qs('#insights-loading');
    const content = qs('#insights-content');
    
    // Show modal and loading state
    modal.style.display = 'block';
    loading.style.display = 'block';
    content.innerHTML = '';
    
    try {
      // Get current filter parameters
      const params = buildParams();
      console.log('AI Insights - Sending parameters:', params);
      
      // Create AbortController for timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      // Call AI insights API with timeout
      const response = await fetch('/api/sitreps/ai-insights?' + params, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('AI Insights - Received data:', data);
      
      if (response.ok) {
        // Handle case where data might be a JSON string instead of object
        let insights = data;
        if (typeof data === 'string') {
          try {
            insights = JSON.parse(data);
          } catch (parseError) {
            console.error('Failed to parse JSON string:', parseError);
            // If it's a string but not valid JSON, treat it as summary text
            insights = {
              patterns: [],
              anomalies: [],
              trends: [],
              summary: data
            };
          }
        }
        
        displayInsights(insights);
      } else {
        throw new Error(data.error || 'Failed to generate insights');
      }
    } catch (error) {
      console.error('Error generating AI insights:', error);
      
      let errorMessage = 'Failed to generate AI insights';
      let errorDetails = error.message;
      
      if (error.name === 'AbortError') {
        errorMessage = 'Request Timeout';
        errorDetails = 'The AI analysis is taking longer than expected. This may be due to high server load or complex data processing. Please try again with a smaller date range or fewer filters.';
      } else if (error.message.includes('Failed to fetch') || error.message.includes('ERR_CONNECTION_RESET')) {
        errorMessage = 'Connection Error';
        errorDetails = 'Unable to connect to the AI analysis service. Please check your connection and try again.';
      } else if (error.message.includes('HTTP 500')) {
         errorMessage = 'Server Error';
         errorDetails = 'The server encountered an error while processing your request. Please try again later.';
       }
       
       // Auto-retry for connection errors (max 2 retries)
       if ((error.message.includes('Failed to fetch') || error.name === 'AbortError') && retryCount < 2) {
         console.log(`Retrying AI insights request (attempt ${retryCount + 1}/2)...`);
         setTimeout(() => generateAIInsights(retryCount + 1), 2000);
         return;
       }
       
       content.innerHTML = `
        <div class="insight-section">
          <h3><i class="fa-solid fa-exclamation-triangle"></i> ${errorMessage}</h3>
          <div class="insight-item">
            <p><strong>Details:</strong> ${errorDetails}</p>
            <p><strong>Suggestions:</strong></p>
            <ul>
              <li>Try reducing the date range or number of filters</li>
              <li>Wait a moment and try again</li>
              <li>Check if the AI analysis service is running</li>
            </ul>
          </div>
        </div>
      `;
    } finally {
      loading.style.display = 'none';
    }
  }

  function displayInsights(data) {
    const content = qs('#insights-content');
    let html = '';
    
    // Ensure data is an object
    if (!data || typeof data !== 'object') {
      data = {
        patterns: [],
        anomalies: [],
        trends: [],
        summary: 'Invalid data format received.'
      };
    }
    
    // Display patterns
    if (data.patterns && Array.isArray(data.patterns) && data.patterns.length > 0) {
      html += `
        <div class="insight-section">
          <h3><i class="fa-solid fa-chart-line"></i> Identified Patterns</h3>
          ${data.patterns.map(pattern => `
            <div class="insight-item pattern-item">
              <h4>${escapeHtml(pattern.title || 'Untitled Pattern')}</h4>
              <p>${escapeHtml(pattern.description || 'No description available.')}</p>
              ${pattern.confidence ? `<small class="confidence">Confidence: ${pattern.confidence}%</small>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }
    
    // Display anomalies
    if (data.anomalies && Array.isArray(data.anomalies) && data.anomalies.length > 0) {
      html += `
        <div class="insight-section">
          <h3><i class="fa-solid fa-exclamation-circle"></i> Detected Anomalies</h3>
          ${data.anomalies.map(anomaly => {
            const severityClass = anomaly.severity ? `severity-${anomaly.severity.toLowerCase()}` : '';
            return `
            <div class="insight-item anomaly-item">
              <h4>${escapeHtml(anomaly.title || 'Untitled Anomaly')}</h4>
              <p>${escapeHtml(anomaly.description || 'No description available.')}</p>
              ${anomaly.severity ? `<small class="${severityClass}">Severity: ${escapeHtml(anomaly.severity)}</small>` : ''}
            </div>
            `;
          }).join('')}
        </div>
      `;
    }
    
    // Display trends
    if (data.trends && Array.isArray(data.trends) && data.trends.length > 0) {
      html += `
        <div class="insight-section">
          <h3><i class="fa-solid fa-trending-up"></i> Key Trends</h3>
          ${data.trends.map(trend => {
            const trendClass = trend.direction ? `trend-${trend.direction.toLowerCase()}` : '';
            return `
            <div class="insight-item trend-item">
              <h4>${escapeHtml(trend.title || 'Untitled Trend')}</h4>
              <p>${escapeHtml(trend.description || 'No description available.')}</p>
              ${trend.direction ? `<small class="${trendClass}">Trend: ${escapeHtml(trend.direction)}</small>` : ''}
            </div>
            `;
          }).join('')}
        </div>
      `;
    }
    
    // Display summary
    if (data.summary) {
      html += `
        <div class="insight-section">
          <h3><i class="fa-solid fa-lightbulb"></i> Summary</h3>
          <div class="insight-item">
            <p>${escapeHtml(data.summary)}</p>
          </div>
        </div>
      `;
    }
    
    if (!html) {
      html = `
        <div class="insight-section empty-state">
          <h3><i class="fa-solid fa-info-circle"></i> No Insights Available</h3>
          <div class="insight-item">
            <p>No significant patterns or anomalies detected in the current dataset. Try adjusting your filters or check back when more data is available.</p>
          </div>
        </div>
      `;
    }
    
    content.innerHTML = html;
  }

  function closeInsightsModal() {
    qs('#ai-insights-modal').style.display = 'none';
  }
})();