/*************************************************************************
 * main.js — Consolidated & Optimized
 * 
 * This script sets up:
 * 1) Map & basemaps
 * 2) Layer control & searching (server-based)
 * 3) Info panel
 * 4) Geocoding (Nominatim + GeoNames)
 * 5) Measurement tools (Leaflet.Draw)
 * 6) KML/KMZ loader
 * 7) Coordinate display
 * 8) Attribute query & thematic styling
 * 9) Directions (Mapbox)
 * 10) Auto-suggestions for places
 * 11) Convert-to-GeoJSON modal
 * 12) Data Tools box: import layers, create new layer (advanced), 
 *     layer management panel, export as ZIP, save project, etc.
 *************************************************************************/

/*************************************
 *  0) MAP INIT & DEFAULT BASE LAYERS
 *************************************/
// Democratic Republic of Congo bounds and center
const CONGO_BOUNDS = [
  [-13.5, 12.0], // Southwest corner
  [5.5, 31.5]    // Northeast corner
];
const CONGO_CENTER = [-4.0, 23.5]; // Central DRC coordinates

// Global map variable
let map;

// Define base maps - Optimized for fast loading and high zoom levels
const basemapLayers = {
  osm: L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors",
    maxZoom: 20,
    maxNativeZoom: 19,
    subdomains: ['a', 'b', 'c'],
    tileSize: 256,
    zoomOffset: 0,
    detectRetina: true,
    keepBuffer: 2,
    updateWhenIdle: false,
    updateWhenZooming: true,
    crossOrigin: true,
    errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
  }),
  "esri-aerial": L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    { 
      attribution: "ESRI World Imagery", 
      maxZoom: 21,
      maxNativeZoom: 19,
      tileSize: 256,
      zoomOffset: 0,
      detectRetina: true,
      keepBuffer: 2,
      updateWhenIdle: false,
      updateWhenZooming: true,
      crossOrigin: true,
      errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    }
  ),
  "esri-street": L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    { 
      attribution: "ESRI Street Map", 
      maxZoom: 20,
      maxNativeZoom: 19,
      tileSize: 256,
      zoomOffset: 0,
      detectRetina: true,
      keepBuffer: 2,
      updateWhenIdle: false,
      updateWhenZooming: true,
      crossOrigin: true,
      errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    }
  ),
  "esri-topo": L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
    { 
      attribution: "ESRI Topographic", 
      maxZoom: 20,
      maxNativeZoom: 19,
      tileSize: 256,
      zoomOffset: 0,
      detectRetina: true,
      keepBuffer: 2,
      updateWhenIdle: false,
      updateWhenZooming: true,
      crossOrigin: true,
      errorTileUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    }
  ),
  none: null,
};

// Wait for DOM to be ready
function initializeMap() {
  // Debug: Check if Leaflet is loaded
  console.log('Leaflet loaded:', typeof L !== 'undefined');
  console.log('Map container exists:', document.getElementById('map') !== null);
  console.log('Document ready state:', document.readyState);

// Initialize map with error handling and performance optimizations
try {
  map = L.map("map", {
    center: CONGO_CENTER,
    zoom: 6,
    maxZoom: 21,
    minZoom: 2,
    maxBounds: CONGO_BOUNDS,
    maxBoundsViscosity: 0.8,
    // Performance optimizations
    preferCanvas: true,
    updateWhenIdle: false,
    updateWhenZooming: true,
    wheelPxPerZoomLevel: 60,
    zoomSnap: 0.25,
    zoomDelta: 0.25,
    // Smooth animations
    zoomAnimation: true,
    zoomAnimationThreshold: 4,
    fadeAnimation: true,
    markerZoomAnimation: true,
    // Tile loading optimizations
    renderer: L.canvas({ padding: 0.5 })
  });
  console.log('Map initialized successfully with performance optimizations');
} catch (error) {
  console.error('Error initializing map:', error);
  // Fallback: try without bounds but keep performance settings
  try {
    map = L.map("map", {
      center: CONGO_CENTER,
      zoom: 6,
      maxZoom: 21,
      minZoom: 2,
      preferCanvas: true,
      updateWhenIdle: false,
      updateWhenZooming: true,
      wheelPxPerZoomLevel: 60,
      zoomSnap: 0.25,
      zoomDelta: 0.25,
      zoomAnimation: true,
      zoomAnimationThreshold: 4,
      fadeAnimation: true,
      markerZoomAnimation: true,
      renderer: L.canvas({ padding: 0.5 })
    });
    console.log('Map initialized without bounds but with performance optimizations');
  } catch (fallbackError) {
    console.error('Fallback map initialization failed:', fallbackError);
  }
}

// Make map globally accessible for chatbot
window.map = map;

// Enhanced tile loading optimization function
function optimizeTileLayer(layer, layerName) {
  if (!layer) return;
  
  let tilesLoading = 0;
  let tilesLoaded = 0;
  let tilesErrored = 0;
  
  layer.on('loading', function() {
    console.log(`${layerName}: Starting to load tiles`);
  });
  
  layer.on('load', function() {
    console.log(`${layerName}: All tiles loaded successfully`);
  });
  
  layer.on('tileloadstart', function() {
    tilesLoading++;
  });
  
  layer.on('tileload', function() {
    tilesLoaded++;
    tilesLoading--;
    if (tilesLoading === 0) {
      console.log(`${layerName}: Batch loading complete - ${tilesLoaded} tiles loaded, ${tilesErrored} errors`);
    }
  });
  
  layer.on('tileerror', function(error) {
    tilesErrored++;
    tilesLoading--;
    console.warn(`${layerName}: Tile error (${tilesErrored} total errors):`, error);
    
    // Retry failed tiles after a short delay
    setTimeout(() => {
      if (error.tile && error.tile.src) {
        error.tile.src = error.tile.src + '?retry=' + Date.now();
      }
    }, 1000);
  });
  
  // Preload tiles for better performance
  layer.on('add', function() {
    console.log(`${layerName}: Layer added, optimizing tile loading`);
    if (map) {
      // Force tile refresh for current view
      layer.redraw();
    }
  });
}

// Default basemap and scale bar with error handling
try {
  if (map && basemapLayers.osm) {
    basemapLayers.osm.addTo(map);
    console.log('OSM basemap added successfully');
    
    // Apply optimization to OSM layer
    optimizeTileLayer(basemapLayers.osm, 'OpenStreetMap');
    
    // Preload and optimize all other basemap layers
    Object.keys(basemapLayers).forEach(key => {
      if (key !== 'osm' && key !== 'none' && basemapLayers[key]) {
        optimizeTileLayer(basemapLayers[key], key);
      }
    });
  }
  
  if (map) {
    L.control.scale().addTo(map);
    console.log('Scale control added successfully');
  }
} catch (error) {
  console.error('Error adding basemap or controls:', error);
}

// Add Democratic Republic of Congo label with error handling
try {
  if (map) {
    const congoLabel = L.divIcon({
      className: 'congo-label',
      html: '<div style="background: rgba(0,0,0,0.7); color: white; padding: 8px 12px; border-radius: 4px; font-size: 16px; font-weight: bold; text-align: center; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">Democratic Republic of Congo</div>',
      iconSize: [250, 40],
      iconAnchor: [125, 20]
    });
    L.marker(CONGO_CENTER, { icon: congoLabel }).addTo(map);
    console.log('Congo label added successfully');
  }
} catch (error) {
    console.error('Error adding Congo label:', error);
  }

  // Initialize measurement layer
  try {
    if (map) {
      measurementLayer = new L.FeatureGroup();
      map.addLayer(measurementLayer);
      console.log('Measurement layer initialized successfully');
      
      // Set up measurement events
      setupMeasurementEvents();
      
      // Set up coordinate display
      setupCoordinateDisplay();
      
      // Set up drawing events
      setupDrawingEvents();
      
      // Initialize sitrep layer
      sitrepLayer = L.layerGroup().addTo(map);
      
      // Initialize edit feature group
      editFeatureGroup = new L.FeatureGroup().addTo(map);
    }
  } catch (error) {
    console.error('Error initializing measurement layer:', error);
  }

  // Enhanced basemap switching with preloading and smooth transitions
  try {
    const basemapItems = document.querySelectorAll("#basemaps-tab ul li");
    let currentBasemap = 'osm';
    
    // Preload function for smooth switching
    function preloadBasemap(baseName) {
      if (baseName !== 'none' && basemapLayers[baseName] && !map.hasLayer(basemapLayers[baseName])) {
        // Add layer temporarily to trigger tile loading, then remove
        const tempLayer = basemapLayers[baseName];
        tempLayer.addTo(map);
        tempLayer.setOpacity(0);
        
        // Remove after tiles start loading
        setTimeout(() => {
          if (map.hasLayer(tempLayer) && currentBasemap !== baseName) {
            map.removeLayer(tempLayer);
          }
        }, 100);
      }
    }
    
    // Enhanced basemap switching function
    function switchBasemap(baseName) {
      console.log(`Switching to basemap: ${baseName}`);
      
      // Remove current tile layers with fade effect
      map.eachLayer((lyr) => {
        if (lyr instanceof L.TileLayer) {
          lyr.setOpacity(0);
          setTimeout(() => {
            if (map.hasLayer(lyr)) {
              map.removeLayer(lyr);
            }
          }, 200);
        }
      });
      
      // Add new basemap with fade in effect
      if (baseName !== "none" && basemapLayers[baseName]) {
        setTimeout(() => {
          const newLayer = basemapLayers[baseName];
          newLayer.setOpacity(0);
          newLayer.addTo(map);
          
          // Fade in the new layer
          let opacity = 0;
          const fadeIn = setInterval(() => {
            opacity += 0.1;
            newLayer.setOpacity(opacity);
            if (opacity >= 1) {
              clearInterval(fadeIn);
              console.log(`Basemap ${baseName} loaded successfully`);
            }
          }, 20);
        }, 200);
      }
      
      currentBasemap = baseName;
    }
    
    basemapItems.forEach((item) => {
      const baseName = item.getAttribute("data-basemap");
      
      // Preload on hover for instant switching
      item.addEventListener("mouseenter", () => {
        preloadBasemap(baseName);
      });
      
      // Enhanced click handler
      item.addEventListener("click", () => {
        switchBasemap(baseName);
        
        // Update UI to show active basemap
        basemapItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
    
    // Set initial active state
    const osmItem = document.querySelector('[data-basemap="osm"]');
    if (osmItem) osmItem.classList.add('active');
    
    console.log('Enhanced basemap switching with preloading set up successfully');
  } catch (error) {
    console.error('Error setting up basemap switching:', error);
  }

}

/**************************************
 * Helper to remove all tile layers 
 * (for basemap switching)
 **************************************/
function removeTileLayers() {
  map.eachLayer((lyr) => {
    if (lyr instanceof L.TileLayer) map.removeLayer(lyr);
  });
}

/**********************************************
 *  1) BASEMAP SWITCHING (via <li data-basemap>)
 *  Note: Event listeners are now set up in initializeMap()
 **********************************************/

/********************************************************
 *  2) LAYER CONTROL & SEARCH (From server endpoints)
 ********************************************************/
// We'll keep a "layers" object for storing local loaded layers
const layers = {}; // { layerName: L.GeoJSON }
const layerVisibility = {};
window.layerDataStore = {}; // for queries
window.attributeStore = {}; // for query attribute keys

// Distinct color schema per AOR layer
const AOR_LAYER_STYLES = {
  "Govt Cont Area": { color: "#1f78b4", fillColor: "#1f78b4" }, // blue
  "Rebel Cont Area": { color: "#e31a1c", fillColor: "#e31a1c" }, // red
  "BNs & Force": { color: "#33a02c", fillColor: "#33a02c" }, // green
  "COB": { color: "#ff7f00", fillColor: "#ff7f00" }, // orange
  "Buffer Z": { color: "#6a3d9a", fillColor: "#6a3d9a" }, // purple
  "UN Patrol Routes": { color: "#00bcd4", fillColor: "#00bcd4" }, // teal for patrol routes
};

const layerList = document.getElementById("layer-list");
const layerSearch = document.getElementById("layer-search");
window.tocLayerItems = {};

// Infra layers and their icon mapping
const INFRA_LAYER_SET = new Set(["Jetties", "Airfd", "Hosp", "Schools", "POC IDP camp"]);
const INFRA_LAYER_ICON_EMOJI = {
  "Jetties": "⚓",
  "Airfd": "✈️",
  "Hosp": "🏥",
  "Schools": "🎓",
  "POC IDP camp": "⛺",
};
function getInfraIcon(layerName) {
  const emoji = INFRA_LAYER_ICON_EMOJI[layerName] || "📍";
  return L.divIcon({
    className: "infra-div-icon",
    html: `<span class="infra-emoji">${emoji}</span>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

// Activity Marking layers (virtual)
const ACTIVITY_LAYER_NAMES = ["own", "local govt", "rebel", "other", "NGOs", "route disruptions"];
const ACTIVITY_TO_SOURCE = {
  "own": "own",
  "local govt": "local",
  "rebel": "rebel",
  "other": "other",
  "NGOs": "ngo",
};
const ACTIVITY_LAYER_SET = new Set(ACTIVITY_LAYER_NAMES);
// Track whether UN Patrol Routes was auto-toggled by the "route disruptions" virtual layer
let routeLayerAutoToggledByDisruptions = false;

// Fetch available layer names from /data/layers
fetch("/data/layers")
  .then((res) => {
    if (!res.ok) throw new Error("Failed to fetch layer list");
    return res.json();
  })
  .then((layerNames) => {
    populateLayerList(layerNames);
    layerSearch.addEventListener("input", () => filterLayers(layerNames));
    // Do not auto-toggle any layer on load; user controls visibility
  })
  .catch((err) => console.error(err));

function populateLayerList(layerNames) {
  layerList.innerHTML = "";
  // Build categories: split current layers into AOR vs Infra
  const infraNames = layerNames.filter((n) => INFRA_LAYER_SET.has(n));
  const aorNames = layerNames.filter((n) => !INFRA_LAYER_SET.has(n));
  const categories = {
    "AOR Marking": aorNames,
    "Activity Marking": ACTIVITY_LAYER_NAMES,
    "Infra": infraNames,
  };

  Object.entries(categories).forEach(([catName, names]) => {
    const catLi = document.createElement("li");
    catLi.className = "toc-category";

    // Category header
    const header = document.createElement("div");
    header.className = "toc-header";
    header.innerHTML = `<span class="toc-title">${catName}</span>`;
    catLi.appendChild(header);

    // Nested layer list
    const nested = document.createElement("ul");
    nested.className = "toc-list";

    names.forEach((ln) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="selected-check">✓</span><span>${ln}</span>`;
      li.className = "layer-control-button";
      if (layerVisibility[ln]) li.classList.add("layer-selected");
      li.addEventListener("mouseover", () => {
        if (!li.classList.contains("layer-selected")) li.style.backgroundColor = "#e6e6e6";
      });
      li.addEventListener("mouseout", () => {
        if (!li.classList.contains("layer-selected")) li.style.backgroundColor = "";
      });
      li.addEventListener("click", () => toggleLayer(ln, li));
      nested.appendChild(li);
      window.tocLayerItems[ln] = li;
    });

    // Category click: expand/collapse to show layers; no auto-plotting
    header.addEventListener("click", () => {
      catLi.classList.toggle("expanded");
    });

    catLi.appendChild(nested);
    layerList.appendChild(catLi);
  });
}

function filterLayers(layerNames) {
  const searchVal = layerSearch.value.toLowerCase();
  const filtered = layerNames.filter((ln) => ln.toLowerCase().includes(searchVal));
  populateLayerList(filtered);
}

function toggleLayer(layerName, listItem) {
  // Activity Marking virtual layers: fetch SITREPs for last 7 days by selected category
  if (ACTIVITY_LAYER_SET.has(layerName)) {
    const src = ACTIVITY_TO_SOURCE[layerName];
    // Create sitrepLayer if needed
    if (typeof sitrepLayer === "undefined" || !sitrepLayer) {
      if (map) {
        sitrepLayer = L.layerGroup().addTo(map);
      } else {
        console.error('Map not initialized when trying to create sitrepLayer');
        return;
      }
    }
    if (layerVisibility[layerName]) {
      // Deactivate this activity source
      layerVisibility[layerName] = false;
      listItem.classList.remove("layer-selected");
      listItem.style.backgroundColor = "";
      // No coupling with UN Patrol Routes when disabling 'route disruptions'
      routeLayerAutoToggledByDisruptions = false;
    } else {
      // Activate this activity source
      layerVisibility[layerName] = true;
      listItem.classList.add("layer-selected");
      listItem.style.backgroundColor = "#cce5ff";
      // Do not auto-enable UN Patrol Routes when enabling 'route disruptions'
    }
    // Refresh SITREPs for all currently active activity sources using current filters (range/from/to)
    (async () => {
      try {
        // Build filters based on UI controls, but ensure sources reflect active Activity selections
        const filters = getSitrepFilters();
        const activeSources = ACTIVITY_LAYER_NAMES
          .filter((name) => layerVisibility[name])
          .map((name) => ACTIVITY_TO_SOURCE[name])
          .filter(Boolean);

        // If no activity sources are active, clear incidents and stop
        if (!activeSources.length) {
          if (typeof sitrepLayer !== "undefined" && sitrepLayer) {
            sitrepLayer.clearLayers();
          }
          return;
        }

        filters.sources = activeSources;
        // If the special virtual layer "route disruptions" is active, filter by incident type client-side
        if (layerVisibility["route disruptions"]) {
          filters.incidentType = "route_disruption";
        }
        // Default range to 30 days if none provided
        if (!filters.rangeDays && !filters.fromDate && !filters.toDate) {
          filters.rangeDays = 30;
        }
        await refreshSitreps(filters);
      } catch (err) {
        console.error("Failed to load activity marking:", err);
      }
    })();
    return;
  }
  if (!layers[layerName]) {
    // If not loaded yet, fetch from server
    fetch(`/data/${layerName}`)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load layer: ${layerName}`);
        return r.json();
      })
      .then((data) => {
        const geojsonData = data;
        const feats = geojsonData.features || [];
        const geoLyr = L.geoJSON(geojsonData, {
          style: (feature) => {
            const s = AOR_LAYER_STYLES[layerName] || { color: getRandomColor(), fillColor: getRandomColor() };
            if (feature.geometry.type !== "Point") {
              // Increase patrol route width and vary styles per route
              if (layerName === "UN Patrol Routes") {
                const nameStr = (feature.properties?.name || "");
                const hash = nameStr.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
                const variants = [
                  { weight: 8, dashArray: "8,4" },
                  { weight: 7, dashArray: "4,2,1,2" },
                  { weight: 9, dashArray: null },
                  { weight: 6, dashArray: "2,6" },
                  { weight: 8, dashArray: "1" },
                ];
                const v = variants[hash % variants.length];
                return {
                  color: s.color,
                  weight: v.weight,
                  dashArray: v.dashArray || undefined,
                  opacity: 0.95,
                  lineCap: "round",
                  lineJoin: "round",
                };
              }
              // Default styling for other non-point features
              return { color: s.color, weight: 2, fillColor: s.fillColor, fillOpacity: 0.35 };
            }
            return {};
          },
          pointToLayer: (feat, latlng) => {
            // Use Infra-specific icons if applicable
            if (INFRA_LAYER_SET.has(layerName)) {
              const icon = getInfraIcon(layerName);
              const marker = L.marker(latlng, { icon });
              if (feat.properties?.name) {
                marker.bindTooltip(feat.properties.name, {
                  permanent: false,
                  direction: "top",
                  offset: [0, -4],
                });
              }
              return marker;
            }
            // Default circle markers for non-Infra
            const pop = feat.properties?.population || 0;
            let radius = pop > 100000 ? 12 : pop >= 50000 ? 8 : pop >= 10000 ? 5 : 3;
            const s = AOR_LAYER_STYLES[layerName] || { color: "#000", fillColor: "#ff7800" };
            const marker = L.circleMarker(latlng, {
              radius,
              fillColor: s.fillColor,
              color: s.color,
              weight: 1,
              fillOpacity: 0.85,
            });
            if (feat.properties?.name) {
              marker.bindTooltip(feat.properties.name, {
                permanent: false,
                direction: "top",
                offset: [0, -4],
              });
            }
            return marker;
          },
          onEachFeature: (feature, lyr) => {
            const props = feature.properties || {};
            if (layerName === "UN Patrol Routes") {
              const html = `<b>${props.name || "UN Patrol Route"}</b><br/>Unit: ${props.unit || "N/A"}<br/>Status: ${props.status || "N/A"}${props.notes ? `<br/>Notes: ${props.notes}` : ""}`;
              lyr.bindPopup(html);
              lyr.on("click", () => {
                showFeatureInfoInSidePanel(feature);
                lyr.openPopup();
              });
              lyr.on("mouseover", () => lyr.setStyle({ weight: (lyr.options.weight || 8) + 1 }));
              lyr.on("mouseout", () => lyr.setStyle({ weight: (lyr.options.weight || 8) }));
            } else {
              if (props.name) lyr.bindPopup(`<b>${props.name}</b>`);
              lyr.on("click", () => showFeatureInfoInSidePanel(feature));
            }
          },
        }).addTo(map);
        if (layerName === "UN Patrol Routes") {
          geoLyr.eachLayer((l) => l.bringToFront());
        }
        layers[layerName] = geoLyr;
        layerVisibility[layerName] = true;
        listItem.classList.add("layer-selected");
        listItem.style.backgroundColor = "#cce5ff";
        try {
          const b = geoLyr.getBounds();
          if (b.isValid()) map.fitBounds(b);
        } catch (e) {}
        window.layerDataStore[layerName] = { geojson: geoLyr, features: feats };
        registerLayerForQuery(layerName, feats);
      })
      .catch((err) => console.error(err));
  } else {
    // Toggle existing
    const existing = layers[layerName];
    if (map.hasLayer(existing)) {
      map.removeLayer(existing);
      layerVisibility[layerName] = false;
      listItem.classList.remove("layer-selected");
      listItem.style.backgroundColor = "";
    } else {
      existing.addTo(map);
      layerVisibility[layerName] = true;
      listItem.classList.add("layer-selected");
      listItem.style.backgroundColor = "#cce5ff";
      try {
        const b = existing.getBounds();
        if (b.isValid()) map.fitBounds(b);
      } catch (e) {}
    }
  }
}

function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let c = "#";
  for (let i = 0; i < 6; i++) c += letters[Math.floor(Math.random() * 16)];
  return c;
}

/**********************************************
 *  3) INFO PANEL (DRAGGABLE) FOR FEATURE INFO
 **********************************************/
function showFeatureInfoInSidePanel(feature) {
  const infoPanel = document.getElementById("info-panel");
  const infoContent = document.getElementById("info-content");
  infoPanel.style.display = "block";
  infoContent.innerHTML = "";
  if (!infoPanel.querySelector("button")) {
    const closeButton = document.createElement("button");
    closeButton.textContent = "✖";
    Object.assign(closeButton.style, {
      position: "absolute",
      top: "10px",
      right: "10px",
      background: "none",
      border: "none",
      cursor: "pointer",
      fontSize: "1.2rem",
      color: "#333",
    });
    closeButton.title = "Close";
    closeButton.addEventListener("click", () => {
      infoPanel.style.display = "none";
    });
    infoPanel.appendChild(closeButton);
  }
  if (!feature.properties) {
    infoContent.innerHTML = '<p style="font-size:1rem; color:#777;">No properties available.</p>';
    return;
  }
  let html = "<table>";
  for (const key in feature.properties) {
    html += `<tr><td style="font-weight:bold; color:#555;">${key}</td><td style="color:#444;">${feature.properties[key]}</td></tr>`;
  }
  html += "</table>";
  infoContent.innerHTML = html;
}
function makeInfoPanelDraggable() {
  const infoPanel = document.getElementById("info-panel");
  let isDragging = false,
    startX,
    startY;
  infoPanel.addEventListener("mousedown", (e) => {
    if (e.target.tagName === "BUTTON") return;
    isDragging = true;
    startX = e.clientX - infoPanel.offsetLeft;
    startY = e.clientY - infoPanel.offsetTop;
    infoPanel.style.cursor = "move";
  });
  document.addEventListener("mousemove", (e) => {
    if (!isDragging) return;
    infoPanel.style.left = `${e.clientX - startX}px`;
    infoPanel.style.top = `${e.clientY - startY}px`;
  });
  document.addEventListener("mouseup", () => {
    isDragging = false;
    infoPanel.style.cursor = "default";
  });
}
makeInfoPanelDraggable();

/*************************************************
 *  4) GEOCODING (Nominatim + GeoNames) 
 *************************************************/
const GEO_NAMES_USERNAME = "eswar96";
const searchBtn = document.getElementById("search-btn");
searchBtn.addEventListener("click", async () => {
  const q = document.getElementById("search").value.trim();
  const searchInput = document.getElementById("search");
  
  // Input validation
  if (!q) {
    alert("Please enter a location to search");
    searchInput.focus();
    return;
  }
  
  // Show loading state
  const originalText = searchBtn.textContent;
  searchBtn.textContent = "Searching...";
  searchBtn.disabled = true;
  searchInput.disabled = true;
  
  try {
    let coordinates, display_name;
    
    try {
      // Try Mapbox first
      searchBtn.textContent = "Finding Location (Mapbox)...";
      const mapboxUrl = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(q)}.json?access_token=${MAPBOX_ACCESS_TOKEN}&country=cd&limit=1&bbox=${CONGO_BOUNDS[0][1]},${CONGO_BOUNDS[0][0]},${CONGO_BOUNDS[1][1]},${CONGO_BOUNDS[1][0]}`;
      
      const mapboxRes = await fetch(mapboxUrl);
      if (!mapboxRes.ok) {
        throw new Error(`Mapbox API error: ${mapboxRes.status}`);
      }
      
      const mapboxData = await mapboxRes.json();
      if (!mapboxData.features || !mapboxData.features.length) {
        throw new Error("Mapbox: Location not found");
      }
      
      const [lon, lat] = mapboxData.features[0].center;
      coordinates = [parseFloat(lat), parseFloat(lon)];
      display_name = mapboxData.features[0].place_name;
      
    } catch (mapboxError) {
      console.warn('Mapbox geocoding failed, trying Nominatim:', mapboxError.message);
      
      // Fallback to Nominatim
      searchBtn.textContent = "Finding Location (Nominatim)...";
      const nominatimUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
        q + " Democratic Republic of Congo"
      )}&format=json&countrycodes=cd&bounded=1&viewbox=${CONGO_BOUNDS[0][1]},${CONGO_BOUNDS[1][0]},${CONGO_BOUNDS[1][1]},${CONGO_BOUNDS[0][0]}`;
      
      const nomRes = await fetch(nominatimUrl);
      if (!nomRes.ok) {
        throw new Error(`Network error: ${nomRes.status}`);
      }
      
      const nomData = await nomRes.json();
      if (!nomData.length) {
        throw new Error("Location not found in the Democratic Republic of Congo. Please try a different search term or check the spelling.");
      }
      
      const { lat, lon } = nomData[0];
      coordinates = [parseFloat(lat), parseFloat(lon)];
      display_name = nomData[0].display_name;
    }
    
    // Validate coordinates are within expected bounds
    if (!isWithinCongoBounds(coordinates)) {
      throw new Error("Found location is outside the Democratic Republic of Congo bounds.");
    }
    
    // Get additional details from GeoNames
    searchBtn.textContent = "Getting Details...";
    let popupContent = `<strong>${display_name}</strong>`;
    
    try {
      const geoNamesUrl = `http://api.geonames.org/searchJSON?q=${encodeURIComponent(
        q
      )}&maxRows=1&username=${GEO_NAMES_USERNAME}`;
      const geoRes = await fetch(geoNamesUrl);
      
      if (geoRes.ok) {
        const geoData = await geoRes.json();
        if (geoData.geonames && geoData.geonames.length > 0) {
          const place = geoData.geonames[0];
          const { countryName, adminName1, population } = place;
          popupContent += `<br><b>Country:</b> ${countryName || "N/A"}`;
          popupContent += `<br><b>State/Region:</b> ${adminName1 || "N/A"}`;
          popupContent += `<br><b>Population:</b> ${population ? population.toLocaleString() : "N/A"}`;
        } else {
          popupContent += `<br><em>Additional details not available.</em>`;
        }
      } else {
        popupContent += `<br><em>Additional details not available.</em>`;
      }
    } catch (geoError) {
      console.warn("GeoNames lookup failed:", geoError);
      popupContent += `<br><em>Additional details not available.</em>`;
    }
    
    // Show location on map
    map.setView(coordinates, 12);
    L.popup()
      .setLatLng(coordinates)
      .setContent(popupContent)
      .openOn(map);
    
    // Success feedback
    searchBtn.textContent = "Location Found!";
    setTimeout(() => {
      searchBtn.textContent = originalText;
    }, 2000);
    
  } catch (error) {
    console.error("Geocoding error:", error);
    let errorMessage = "Error searching for location. Please try again.";
    
    if (error.message.includes("not found")) {
      errorMessage = error.message;
    } else if (error.message.includes("bounds")) {
      errorMessage = "The location found is outside the Democratic Republic of Congo. Please search for locations within DRC.";
    } else if (error.message.includes("Network") || error.message.includes("fetch")) {
      errorMessage = "Network error. Please check your internet connection and try again.";
    }
    
    alert(errorMessage);
    searchInput.focus();
  } finally {
    // Reset UI state
    searchBtn.disabled = false;
    searchInput.disabled = false;
    if (searchBtn.textContent !== originalText && !searchBtn.textContent.includes("Location Found")) {
      searchBtn.textContent = originalText;
    }
  }
});

/******************************************
 *  5) CLEAR BUTTON => RELOAD PAGE
 ******************************************/
document.getElementById("clear-btn").addEventListener("click", () => {
  window.location.reload();
});

/**********************************************
 *  6) MEASUREMENT TOOL (Leaflet.Draw)
 **********************************************/
const measureBtn = document.getElementById("measure-btn");
const measureTool = document.getElementById("measure-tool");
let measurementLayer; // Will be initialized when map is ready

let activeMeasurementTool = null; // To track which measurement tool is active

measureBtn.addEventListener("click", () => {
  if (measureTool.style.display === "block") {
    measureTool.style.display = "none";
    measureBtn.style.backgroundColor = "";
    activeMeasurementTool = null; // Reset active tool
  } else {
    measureTool.style.display = "block";
    measureBtn.style.backgroundColor = "#ff9800";
  }
});

// Use a flag to indicate measurement mode
let isMeasurementMode = false;

document.getElementById("draw-line-btn").addEventListener("click", () => {
  isMeasurementMode = true;
  activeMeasurementTool = "line";
  new L.Draw.Polyline(map, {
    shapeOptions: { color: "red" },
    showLength: true,
  }).enable();
});

document.getElementById("draw-polygon-btn").addEventListener("click", () => {
  isMeasurementMode = true;
  activeMeasurementTool = "polygon";
  new L.Draw.Polygon(map, {
    shapeOptions: { color: "orange" },
    showArea: true,
  }).enable();
});

document.getElementById("delete-shapes-btn").addEventListener("click", () => {
  measurementLayer.clearLayers(); // Clear only measurement shapes
});

// Handle measurement tool events - will be set up after map initialization
function setupMeasurementEvents() {
  if (!map) return;
  
  map.on(L.Draw.Event.CREATED, (e) => {
  if (isMeasurementMode) {
    const layer = e.layer;
    measurementLayer.addLayer(layer);

    if (e.layerType === "polyline") {
      let distance = 0;
      const latlngs = layer.getLatLngs();
      for (let i = 0; i < latlngs.length - 1; i++) {
        distance += latlngs[i].distanceTo(latlngs[i + 1]);
      }
      const distText =
        distance > 1000
          ? (distance / 1000).toFixed(2) + " km"
          : distance.toFixed(2) + " m";
      layer.bindPopup(`<b>Distance:</b> ${distText}`).openPopup();
    } else if (e.layerType === "polygon") {
      const latlngs = layer.getLatLngs()[0];
      const area = L.GeometryUtil.geodesicArea(latlngs); // Area in m²
      const km2 = (area / 1e6).toFixed(2); // Convert to km²
      layer.bindPopup(`<b>Area:</b> ${km2} km²`).openPopup();
    }
  }
  });
}

// Ensure area calculations use geodesic (correct) method
if (typeof L.GeometryUtil === "undefined") {
  L.GeometryUtil = {
    geodesicArea(latlngs) {
      let area = 0;
      const len = latlngs.length;
      if (len < 3) return 0; // Not a valid polygon
      for (let i = 0; i < len; i++) {
        const p1 = latlngs[i];
        const p2 = latlngs[(i + 1) % len];
        area += p1.lng * p2.lat - p2.lng * p1.lat;
      }
      return Math.abs(area * 12365.1612); // Convert to square meters
    },
  };
}

/************************************************
 * 7) KML/KMZ FILE LOADER
 ************************************************/
const kmlFileInput = document.getElementById("kml-file-input");
const loadKmlBtn = document.getElementById("load-kml-btn");
const kmlStatus = document.getElementById("kml-status");
let kmlLayer = null;
loadKmlBtn.addEventListener("click", () => {
  const file = kmlFileInput.files?.[0];
  if (!file) {
    alert("Please select a KML/KMZ file first.");
    return;
  }
  kmlStatus.textContent = `Loading ${file.name}...`;
  if (kmlLayer) {
    map.removeLayer(kmlLayer);
    kmlLayer = null;
  }
  const ext = file.name.toLowerCase().split(".").pop();
  if (ext === "kml") {
    loadKMLFile(file);
  } else if (ext === "kmz") {
    loadKMZFile(file);
  } else {
    kmlStatus.textContent = "Unsupported file format.";
  }
});
function loadKMLFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    parseKML(e.target.result);
  };
  reader.readAsText(file);
}
function loadKMZFile(file) {
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const zipData = e.target.result;
      const jszip = new JSZip();
      const zip = await jszip.loadAsync(zipData);
      const kmlFile = zip.file(/\.kml$/i)[0];
      if (!kmlFile) {
        kmlStatus.textContent = "No KML file found inside KMZ.";
        return;
      }
      const kmlText = await kmlFile.async("text");
      parseKML(kmlText);
    } catch (err) {
      console.error(err);
      kmlStatus.textContent = "Error loading KMZ.";
    }
  };
  reader.readAsArrayBuffer(file);
}
function parseKML(kmlText) {
  try {
    if (typeof toGeoJSON === "undefined") {
      kmlStatus.textContent = "Missing togeojson.";
      return;
    }
    const parser = new DOMParser();
    const kmlDom = parser.parseFromString(kmlText, "text/xml");
    const geojson = toGeoJSON.kml(kmlDom);
    kmlLayer = L.geoJSON(geojson, {
      style: { color: "purple", weight: 2 },
      onEachFeature: (feat, lyr) => {
        const nm = feat.properties.name || "KML Feature";
        lyr.bindPopup(`<b>${nm}</b>`);
      },
    }).addTo(map);
    try {
      map.fitBounds(kmlLayer.getBounds());
    } catch (e) {}
    kmlStatus.textContent = "KML/KMZ loaded successfully!";
  } catch (e) {
    console.error(e);
    kmlStatus.textContent = "Error parsing KML.";
  }
}

/****************************************
 * 8) COORDINATE DISPLAY (on mousemove)
 ****************************************/
function setupCoordinateDisplay() {
  if (!map) return;
  
  map.on("mousemove", (e) => {
    const coordDiv = document.getElementById("coord-text");
    if (!coordDiv) return;
    coordDiv.textContent = `Lat: ${e.latlng.lat.toFixed(5)}, Lng: ${e.latlng.lng.toFixed(5)}`;
  });
}

/*******************************************************************
 * 9) ATTRIBUTE QUERY, VIEWING, THEMATIC STYLING
 *    (Using "window.layerDataStore" for loaded data)
 ******************************************************************/
function registerLayerForQuery(layerName, features) {
  const queryLayerSel = document.getElementById("query-layer-select");
  let found = false;
  for (let i = 0; i < queryLayerSel.options.length; i++) {
    if (queryLayerSel.options[i].value === layerName) {
      found = true;
      break;
    }
  }
  if (!found) {
    const opt = document.createElement("option");
    opt.value = layerName;
    opt.textContent = layerName;
    queryLayerSel.appendChild(opt);
  }
  const attrSet = new Set();
  features.forEach((f) => {
    if (f.properties) Object.keys(f.properties).forEach((k) => attrSet.add(k));
  });
  window.attributeStore[layerName] = Array.from(attrSet);
}
const queryLayerSelect = document.getElementById("query-layer-select");
const queryAttrSelect = document.getElementById("query-attribute-select");
queryLayerSelect.addEventListener("change", () => {
  queryAttrSelect.innerHTML = '<option value="">-- Select Attribute --</option>';
  const layerName = queryLayerSelect.value;
  if (!layerName) return;
  const attributes = window.attributeStore[layerName] || [];
  attributes.forEach((attr) => {
    const opt = document.createElement("option");
    opt.value = attr;
    opt.textContent = attr;
    queryAttrSelect.appendChild(opt);
  });
});
const queryOpSelect = document.getElementById("query-operator");
const queryValInput = document.getElementById("query-value");
document.getElementById("query-btn").addEventListener("click", () => {
  const ln = queryLayerSelect.value;
  const attr = queryAttrSelect.value;
  const op = queryOpSelect.value;
  const val = queryValInput.value;
  if (!ln || !attr || !op || !val) {
    alert("Please select layer, attribute, operator, and value.");
    return;
  }
  runAttributeQuery(ln, attr, op, val);
});
function runAttributeQuery(layerName, attribute, operator, value) {
  const store = window.layerDataStore[layerName];
  if (!store) {
    alert(`No data store for layer: ${layerName}`);
    return;
  }
  const { geojson, features } = store;
  geojson.clearLayers();
  const matched = features.filter((f) => {
    const propVal = f.properties[attribute];
    if (propVal === undefined || propVal === null) return false;
    switch (operator) {
      case "=":
        return String(propVal) === String(value);
      case ">":
        return parseFloat(propVal) > parseFloat(value);
      case "<":
        return parseFloat(propVal) < parseFloat(value);
      case "contains":
        return String(propVal).toLowerCase().includes(value.toLowerCase());
      default:
        return false;
    }
  });
  const newFC = { type: "FeatureCollection", features: matched };
  const newGeo = L.geoJSON(newFC, {
    style: { color: "red", weight: 2 },
    pointToLayer: (feat, latlng) => {
      const marker = L.circleMarker(latlng, {
        radius: 5,
        fillColor: "#ff0000",
        color: "#000",
        weight: 1,
        fillOpacity: 0.8,
      });
      if (feat.properties?.name) {
        marker.bindTooltip(feat.properties.name, { permanent: true, direction: "center", className: "point-label-tooltip" });
      }
      return marker;
    },
    onEachFeature: (feat, lyr) => {
      if (feat.properties?.name) lyr.bindPopup(`<b>${feat.properties.name}</b>`);
      lyr.on("click", () => showFeatureInfoInSidePanel(feat));
    },
  }).addTo(map);
  store.geojson = newGeo;
  try {
    map.fitBounds(newGeo.getBounds());
  } catch (e) {}
  alert(`Matched: ${matched.length} features.`);
}
document.getElementById("view-attributes-btn").addEventListener("click", () => {
  const ln = queryLayerSelect.value;
  if (!ln) {
    alert("Select a layer first.");
    return;
  }
  const store = window.layerDataStore[ln];
  if (!store) {
    alert("Layer data not loaded yet.");
    return;
  }
  const feats = store.features;
  if (!feats.length) {
    alert("No features in this layer.");
    return;
  }
  const attrs = window.attributeStore[ln] || [];
  let html = `<h3>Attributes for ${ln} (Server Edit)</h3>
    <p>Changes are posted to the server to rewrite the .geojson.</p>
    <table border="1" style="width:100%;font-size:0.9rem;" id="attr-table"><tr>`;
  attrs.forEach((a) => { html += `<th>${a}</th>`; });
  html += "</tr>";
  for (let i = 0; i < feats.length; i++) {
    html += `<tr data-feature-index="${i}">`;
    attrs.forEach((a) => {
      const rawVal = feats[i].properties[a] == null ? "" : String(feats[i].properties[a]);
      const val = rawVal.replace(/"/g, "&quot;");
      html += `<td><input style="width:100%;" data-attr="${a}" value="${val}" /></td>`;
    });
    html += "</tr>";
  }
  html += `</table><br/><button id="save-attrs-btn" style="padding:6px 10px;">Save to Server</button>`;
  const w = window.open("", "Attributes", "width=800,height=600,scrollbars=yes");
  w.document.write(html);
  w.document.close();
  const saveBtn = w.document.getElementById("save-attrs-btn");
  saveBtn.addEventListener("click", async () => {
    const table = w.document.getElementById("attr-table");
    const rows = table.querySelectorAll("tr[data-feature-index]");
    rows.forEach((row) => {
      const fIndex = row.getAttribute("data-feature-index");
      const inputs = row.querySelectorAll("input[data-attr]");
      inputs.forEach((inp) => {
        const attr = inp.getAttribute("data-attr");
        feats[fIndex].properties[attr] = inp.value;
      });
    });
    try {
      const res = await fetch(`/data/${ln}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ features: feats }),
      });
      const result = await res.json();
      if (!res.ok) {
        alert("Error saving to server: " + JSON.stringify(result));
        return;
      }
      alert(`Server update success: ${result.updatedCount} features in ${ln}.geojson`);
      reRenderLayer(ln);
    } catch (ex) {
      console.error(ex);
      alert("Server error: " + ex.message);
    }
  });
});
function reRenderLayer(layerName) {
  const store = window.layerDataStore[layerName];
  if (!store) return;
  if (store.geojson) map.removeLayer(store.geojson);
  const newFC = { type: "FeatureCollection", features: store.features };
  const newGeo = L.geoJSON(newFC, {
    style: (f) => (f.geometry.type !== "Point" ? { color: getRandomColor(), weight: 2 } : {}),
    pointToLayer: (feat, latlng) => {
      const pop = feat.properties?.population || 0;
      let radius = pop > 100000 ? 12 : pop >= 50000 ? 8 : pop >= 10000 ? 5 : 3;
      const marker = L.circleMarker(latlng, { radius, fillColor: "#ff7800", color: "#000", weight: 1, fillOpacity: 0.8 });
      if (feat.properties?.name) {
        marker.bindTooltip(feat.properties.name, { permanent: false, direction: "top", offset: [0, -4] });
      }
      marker.on("click", () => showFeatureInfoInSidePanel(feat));
      return marker;
    },
  }).addTo(map);
  store.geojson = newGeo;
  try {
    map.fitBounds(newGeo.getBounds());
  } catch (e) {}
}
document.getElementById("apply-thematic-btn").addEventListener("click", () => {
  const layerName = queryLayerSelect.value;
  const attribute = queryAttrSelect.value;
  if (!layerName || !attribute) {
    alert("Select layer and attribute for Thematic Symbology.");
    return;
  }
  applyThematicSymbology(layerName, attribute);
});
function applyThematicSymbology(layerName, attribute) {
  const store = window.layerDataStore[layerName];
  if (!store) {
    alert(`No data store for layer: ${layerName}`);
    return;
  }
  const { geojson, features } = store;
  let minVal = Infinity,
    maxVal = -Infinity;
  features.forEach((f) => {
    const val = parseFloat(f.properties[attribute]);
    if (!isNaN(val)) {
      if (val < minVal) minVal = val;
      if (val > maxVal) maxVal = val;
    }
  });
  if (minVal === Infinity || maxVal === -Infinity) {
    alert("No numeric data found to apply thematics.");
    return;
  }
  geojson.eachLayer((lyr) => {
    if (!lyr.feature || !lyr.feature.properties) return;
    const val = parseFloat(lyr.feature.properties[attribute]) || 0;
    const ratio = (val - minVal) / (maxVal - minVal);
    const r = Math.floor(255 * ratio);
    const g = Math.floor(255 * (1 - ratio));
    const b = 50;
    const color = `rgb(${r},${g},${b})`;
    if (/Polygon/.test(lyr.feature.geometry.type)) {
      lyr.setStyle({ color, fillColor: color, fillOpacity: 0.6, weight: 2 });
    } else if (/Point/.test(lyr.feature.geometry.type)) {
      const newRadius = 3 + 12 * ratio;
      if (lyr.setStyle) lyr.setStyle({ fillColor: color });
      if (lyr.setRadius) lyr.setRadius(newRadius);
    }
  });
  alert(`Thematic style applied to "${layerName}" by "${attribute}".`);
}

/********************************************************
 * 10) DIRECTIONS (Mapbox) 
 ********************************************************/
let routePolyline = null;
let startMarker = null;
let endMarker = null;
let routeDetailsPopup = null;
let disruptionCircle = null;
let sitrepLayer = null;
async function fetchCoordinatesFromMapbox(placeName) {
  // Use Mapbox Geocoding API with focus on Democratic Republic of Congo
  const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(placeName)}.json?access_token=${MAPBOX_ACCESS_TOKEN}&country=cd&limit=1&bbox=${CONGO_BOUNDS[0][1]},${CONGO_BOUNDS[0][0]},${CONGO_BOUNDS[1][1]},${CONGO_BOUNDS[1][0]}`;
  
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Mapbox API error: ${res.status} ${res.statusText}`);
  }
  
  const data = await res.json();
  if (!data.features || !data.features.length) {
    throw new Error(`Place "${placeName}" not found in Democratic Republic of Congo.`);
  }
  
  const [lon, lat] = data.features[0].center;
  return [parseFloat(lat), parseFloat(lon)];
}

// Fallback function that tries Mapbox first, then Nominatim
async function fetchCoordinatesFromNominatim(placeName) {
  try {
    // Try Mapbox first
    return await fetchCoordinatesFromMapbox(placeName);
  } catch (mapboxError) {
    console.warn('Mapbox geocoding failed, trying Nominatim:', mapboxError.message);
    
    // Fallback to Nominatim
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
      placeName + " Democratic Republic of Congo"
    )}&format=json&limit=1&countrycodes=cd&bounded=1&viewbox=${CONGO_BOUNDS[0][1]},${CONGO_BOUNDS[1][0]},${CONGO_BOUNDS[1][1]},${CONGO_BOUNDS[0][0]}`;
    const res = await fetch(url);
    const data = await res.json();
    if (!data || !data.length) throw new Error(`Place "${placeName}" not found in Democratic Republic of Congo.`);
    const { lat, lon } = data[0];
    return [parseFloat(lat), parseFloat(lon)];
  }
}
function calculateStraightLineRoute(startCoords, endCoords) {
  // Calculate straight-line distance using Haversine formula
  const R = 6371; // Earth's radius in kilometers
  const dLat = (endCoords[0] - startCoords[0]) * Math.PI / 180;
  const dLon = (endCoords[1] - startCoords[1]) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(startCoords[0] * Math.PI / 180) * Math.cos(endCoords[0] * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  const distance = R * c * 1000; // Distance in meters
  
  // Estimate duration (assuming average speed of 50 km/h)
  const duration = (distance / 1000) * 72; // seconds (50 km/h = 72 seconds per km)
  
  return {
    geometry: {
      coordinates: [[startCoords[1], startCoords[0]], [endCoords[1], endCoords[0]]]
    },
    distance: distance,
    duration: duration
  };
}
function drawRoute(startCoords, endCoords, route) {
  const coords = route.geometry.coordinates.map((c) => [c[1], c[0]]);
  const distance = (route.distance / 1000).toFixed(2);
  const duration = (route.duration / 60).toFixed(1);
  if (routePolyline) map.removeLayer(routePolyline);
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);
  if (disruptionCircle) map.removeLayer(disruptionCircle);
  startMarker = L.marker(startCoords, { title: "Start Point" }).addTo(map);
  endMarker = L.marker(endCoords, { title: "End Point" }).addTo(map);
  routePolyline = L.polyline(coords, { color: "blue", weight: 6 }).addTo(map);
  routePolyline.on("mouseover", (e) => {
    if (routeDetailsPopup) map.closePopup(routeDetailsPopup);
    routeDetailsPopup = L.popup()
      .setLatLng(e.latlng)
      .setContent(`<b>Distance:</b> ${distance} km<br><b>Time:</b> ${duration} min`)
      .openOn(map);
  });
  routePolyline.on("click", (e) => {
    if (routeDetailsPopup) map.closePopup(routeDetailsPopup);
    routeDetailsPopup = L.popup()
      .setLatLng(e.latlng)
      .setContent(`<b>Distance:</b> ${distance} km<br><b>Time:</b> ${duration} min`)
      .openOn(map);
  });
  routePolyline.on("mouseout", () => {
    if (routeDetailsPopup) map.closePopup(routeDetailsPopup);
  });
  // Avoid Disruptions proximity indicator
  updateDisruptionProximity(routePolyline);
  map.fitBounds(routePolyline.getBounds());
}
function updateDisruptionProximity(currentRoutePolyline) {
  try {
    const avoid = document.getElementById("avoid-disruptions")?.checked;
    if (disruptionCircle) {
      map.removeLayer(disruptionCircle);
      disruptionCircle = null;
    }
    if (!avoid || !sitrepLayer || !currentRoutePolyline) return;

    // Collect disruption points from sitrepLayer
    const disruptionPoints = [];
    sitrepLayer.eachLayer((gj) => {
      if (gj && gj.eachLayer) {
        gj.eachLayer((ptLayer) => {
          const props = ptLayer.feature?.properties || {};
          if (String(props.incident_type || "") === "route_disruption") {
            const ll = ptLayer.getLatLng?.();
            if (ll) disruptionPoints.push(ll);
          }
        });
      }
    });
    if (!disruptionPoints.length) return;

    // Flatten route vertices and compute accurate point-to-segment distances (meters)
    const routeLatLngsRaw = currentRoutePolyline.getLatLngs();
    const flatten = (arr) => arr.flatMap((v) => (Array.isArray(v) ? flatten(v) : [v]));
    const routeLatLngs = flatten(routeLatLngsRaw);

    const project = (ll) => map.options.crs.project(L.latLng(ll.lat, ll.lng));
    const distPointToSegmentMeters = (pLL, aLL, bLL) => {
      const p = project(pLL);
      const a = project(aLL);
      const b = project(bLL);
      const abx = b.x - a.x;
      const aby = b.y - a.y;
      const apx = p.x - a.x;
      const apy = p.y - a.y;
      const ab2 = abx * abx + aby * aby;
      const t = ab2 === 0 ? 0 : Math.max(0, Math.min(1, (apx * abx + apy * aby) / ab2));
      const x = a.x + t * abx;
      const y = a.y + t * aby;
      const dx = p.x - x;
      const dy = p.y - y;
      return Math.sqrt(dx * dx + dy * dy);
    };

    let minDist = Infinity;
    let closestPoint = null;

    disruptionPoints.forEach((p) => {
      for (let i = 0; i < routeLatLngs.length - 1; i++) {
        const d = distPointToSegmentMeters(p, routeLatLngs[i], routeLatLngs[i + 1]);
        if (!Number.isNaN(d) && d < minDist) {
          minDist = d;
          closestPoint = p;
        }
      }
    });

    if (minDist < 2000 && closestPoint) {
      disruptionCircle = L.circle(closestPoint, {
        radius: 2000,
        color: "#ff3b30",
        weight: 2,
        fillColor: "#ff3b30",
        fillOpacity: 0.15,
      }).addTo(map);
    }
  } catch (err) {
    console.error("Failed to update disruption proximity:", err);
  }
}

document.getElementById("route-btn").addEventListener("click", async () => {
  const startPlace = document.getElementById("start-latlng").value;
  const endPlace = document.getElementById("end-latlng").value;
  const routeBtn = document.getElementById("route-btn");
  
  // Input validation
  if (!startPlace || !endPlace) {
    alert("Please enter both start and end places.");
    return;
  }
  
  // Show loading state
  const originalText = routeBtn.textContent;
  routeBtn.textContent = "Calculating Route...";
  routeBtn.disabled = true;
  
  try {
    let startCoords, endCoords;
    const coordRegex = /^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/;
    const startMatch = startPlace.match(coordRegex);
    const endMatch = endPlace.match(coordRegex);
    
    if (startMatch && endMatch) {
      // Direct coordinates provided
      startCoords = [parseFloat(startMatch[1]), parseFloat(startMatch[2])];
      endCoords = [parseFloat(endMatch[1]), parseFloat(endMatch[2])];
      
      // Validate coordinates are within DRC bounds
      if (!isWithinCongoBounds(startCoords) || !isWithinCongoBounds(endCoords)) {
        throw new Error("Coordinates must be within the Democratic Republic of Congo bounds.");
      }
    } else {
      // Need to geocode place names
      routeBtn.textContent = "Finding Locations...";
      [startCoords, endCoords] = await Promise.all([
        fetchCoordinatesFromNominatim(startPlace),
        fetchCoordinatesFromNominatim(endPlace),
      ]);
      
      if (!startCoords || !endCoords) {
        throw new Error("Could not find one or both locations. Please check the spelling or try using coordinates.");
      }
    }
    
    routeBtn.textContent = "Drawing Route...";
    const route = calculateStraightLineRoute(startCoords, endCoords);
    drawRoute(startCoords, endCoords, route);
    
    // Success feedback
    routeBtn.textContent = "Route Calculated!";
    setTimeout(() => {
      routeBtn.textContent = originalText;
    }, 2000);
    
  } catch (error) {
    console.error("Route calculation error:", error);
    let errorMessage = "Error calculating route. Please try again.";
    
    if (error.message.includes("bounds")) {
      errorMessage = "Please ensure both locations are within the Democratic Republic of Congo.";
    } else if (error.message.includes("find")) {
      errorMessage = error.message;
    } else if (error.message.includes("network") || error.message.includes("fetch")) {
      errorMessage = "Network error. Please check your internet connection and try again.";
    }
    
    alert(errorMessage);
  } finally {
    // Reset button state
    routeBtn.disabled = false;
    if (routeBtn.textContent !== originalText && !routeBtn.textContent.includes("Route Calculated")) {
      routeBtn.textContent = originalText;
    }
  }
});

// Helper function to check if coordinates are within Congo bounds
function isWithinCongoBounds(coords) {
  const [lat, lon] = coords;
  return lat >= CONGO_BOUNDS[0][0] && lat <= CONGO_BOUNDS[1][0] && 
         lon >= CONGO_BOUNDS[0][1] && lon <= CONGO_BOUNDS[1][1];
}

/********************************************************
 * 11) AUTO-SUGGESTIONS (Nominatim for DRC) 
 ********************************************************/
async function fetchSuggestions(query) {
  if (query.length < 3) return [];
  const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
    query + " Democratic Republic of Congo"
  )}&format=json&limit=5&countrycodes=cd&bounded=1&viewbox=${CONGO_BOUNDS[0][1]},${CONGO_BOUNDS[1][0]},${CONGO_BOUNDS[1][1]},${CONGO_BOUNDS[0][0]}`;
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data.map((item) => item.display_name);
  } catch (error) {
    console.error("Error fetching suggestions:", error);
    return [];
  }
}
function populateSuggestions(inputId, listId) {
  const input = document.getElementById(inputId);
  const suggestionsList = document.getElementById(listId);
  input.addEventListener("input", async () => {
    const query = input.value;
    suggestionsList.innerHTML = "";
    const suggestions = await fetchSuggestions(query);
    suggestions.forEach((s) => {
      const opt = document.createElement("div");
      opt.textContent = s;
      opt.className = "suggestion-item";
      opt.addEventListener("click", () => {
        input.value = s;
        suggestionsList.innerHTML = "";
      });
      suggestionsList.appendChild(opt);
    });
  });
}
populateSuggestions("start-latlng", "start-suggestions");
populateSuggestions("end-latlng", "end-suggestions");

/****************************************************
 * 12) CONVERT TO GEOJSON (Modal)
 ****************************************************/
const convertBtn = document.getElementById("convert-btn");
const convertModal = document.getElementById("convert-modal");
const convertFileInput = document.getElementById("convert-file");
const convertForm = document.getElementById("convert-form");
const modalOverlay = document.getElementById("modal-overlay");
convertBtn.addEventListener("click", () => {
  convertModal.style.display = "block";
  if (modalOverlay) modalOverlay.style.display = "block";
});
window.addEventListener("click", (e) => {
  if (e.target.id === "convert-modal" || e.target.id === "modal-overlay") {
    convertModal.style.display = "none";
    if (modalOverlay) modalOverlay.style.display = "none";
    convertFileInput.value = "";
  }
});
convertForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const file = convertFileInput.files[0];
  if (!file) {
    alert("Please select a file to convert.");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch("/convert", { method: "POST", body: formData });
    const result = await response.json();
    if (response.ok) alert(`File converted successfully: ${result.geojson_file}`);
    else alert(`Error during conversion: ${result.error}`);
  } catch (error) {
    console.error("Error:", error);
    alert("An unexpected error occurred.");
  } finally {
    convertModal.style.display = "none";
    if (modalOverlay) modalOverlay.style.display = "none";
    convertFileInput.value = "";
  }
});

// SITREP modal open/close handlers
const openSitrepBtn = document.getElementById("open-sitrep-modal");
const sitrepModal = document.getElementById("sitrep-modal");
const closeSitrepModalBtn = document.getElementById("close-sitrep-modal");
if (openSitrepBtn && sitrepModal) {
  openSitrepBtn.addEventListener("click", () => {
    sitrepModal.style.display = "block";
    if (modalOverlay) modalOverlay.style.display = "block";
  });
}
if (closeSitrepModalBtn) {
  closeSitrepModalBtn.addEventListener("click", () => {
    sitrepModal.style.display = "none";
    if (modalOverlay) modalOverlay.style.display = "none";
  });
}

// Air Support Demand modal open/close handlers
const openAirspBtn = document.getElementById("open-airsp-modal");
const airspModal = document.getElementById("airsp-modal");
const closeAirspModalBtn = document.getElementById("close-airsp-modal");
if (openAirspBtn && airspModal) {
  openAirspBtn.addEventListener("click", () => {
    airspModal.style.display = "block";
    if (modalOverlay) modalOverlay.style.display = "block";
  });
}
if (closeAirspModalBtn) {
  closeAirspModalBtn.addEventListener("click", () => {
    airspModal.style.display = "none";
    if (modalOverlay) modalOverlay.style.display = "none";
  });
}

// Air Support Demand submit handler
const airspSubmitBtn = document.getElementById("airsp-submit");
if (airspSubmitBtn) {
  airspSubmitBtn.addEventListener("click", async () => {
    try {
      const category = document.getElementById("airsp-category")?.value || "routine";
      const requester = document.getElementById("airsp-requester")?.value?.trim();
      const title = document.getElementById("airsp-title")?.value?.trim();
      const latStr = document.getElementById("airsp-lat")?.value?.trim();
      const lonStr = document.getElementById("airsp-lon")?.value?.trim();
      const desc = document.getElementById("airsp-desc")?.value?.trim();

      if (!requester || !title || !latStr || !lonStr) {
        alert("Please fill Requester, Title, Latitude and Longitude.");
        return;
      }
      const lat = parseFloat(latStr);
      const lon = parseFloat(lonStr);
      if (Number.isNaN(lat) || Number.isNaN(lon)) {
        alert("Latitude/Longitude must be valid numbers.");
        return;
      }

      const payload = { category, requester, title, lat, lon, description: desc };
      const res = await fetch("/api/airsp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const txt = await res.text();
        alert("Failed to submit Air Support Demand: " + txt);
        return;
      }

      // Clear form
      document.getElementById("airsp-category").value = "routine";
      document.getElementById("airsp-requester").value = "";
      document.getElementById("airsp-title").value = "";
      document.getElementById("airsp-lat").value = "";
      document.getElementById("airsp-lon").value = "";
      document.getElementById("airsp-desc").value = "";

      alert("Air Support Demand submitted.");
      airspModal.style.display = "none";
      if (modalOverlay) modalOverlay.style.display = "none";
    } catch (err) {
      console.error(err);
      alert("Unexpected error while submitting Air Support Demand.");
    }
  });
}

// Import Layer modal open/close handlers
const openImportLayerBtn = document.getElementById("open-import-layer-modal");
const importLayerModal = document.getElementById("import-layer-modal");
const closeImportLayerModalBtn = document.getElementById("close-import-layer-modal");
if (openImportLayerBtn && importLayerModal) {
  openImportLayerBtn.addEventListener("click", () => {
    importLayerModal.style.display = "block";
    if (modalOverlay) modalOverlay.style.display = "block";
  });
}
if (closeImportLayerModalBtn) {
  closeImportLayerModalBtn.addEventListener("click", () => {
    importLayerModal.style.display = "none";
    if (modalOverlay) modalOverlay.style.display = "none";
  });
}


/****************************************************************************
 * main.js — A Complete "Data Tools" Integration
 * 
 * Features:
 * 1) Create new layers with custom attributes.
 * 2) Import local GeoJSON (placeholder for TIFF/GPKG).
 * 3) Coordinate search (lat/lon).
 * 4) Layer management with right-click for attribute table / export.
 * 5) Export single layer & multiple layers (ZIP).
 * 6) Save entire project as JSON.
 * 7) Draw new features & prompt user for attributes.
 * 8) Modify geometry (move points, reshape lines/polygons).
 * 9) Delete, Undo, Redo.
 * 10) Snapping placeholder toggle.
 ****************************************************************************/

/***************************************************************************
 * GLOBALS & Data Structures
 **************************************************************************/
let advancedFields = [];    // For "Create New Layer" advanced wizard

// For geometry editing, shapes should be added to this group:
let editFeatureGroup = null;

// A dictionary storing in-memory layers by name.
// e.g.: layers["DraftLineLayer"] = {
//   layer: L.GeoJSON,
//   type: "line"|"point"|"polygon",
//   attributes: [ { name, type } ],
//   features: [ {...} ]
// };


// For undo/redo
let actionStack = [];
let undoneStack = [];
let drawHandler = null;
let snappingEnabled = false;



// Track the currently active layer (for drawing)
let activeLayerName = null;

// 2) DOM REFERENCES
// (These IDs must match those in index.html)
const importInput        = document.getElementById("import-layer-file");
const importButton       = document.getElementById("import-layer-btn");
const layerListManagement= document.getElementById("layer-list-management");
const exportZipBtn       = document.getElementById("export-zip-btn");
const openAdvancedBtn    = document.getElementById("open-advanced-layer-modal");
const closeAdvancedBtn   = document.getElementById("close-advanced-layer-modal");
const addFieldBtn        = document.getElementById("advanced-add-field");
const createLayerBtn     = document.getElementById("advanced-create-layer");
const advLayerNameInput  = document.getElementById("advanced-layer-name");
const geomTypeSelect     = document.getElementById("advanced-geom-type");
const advFieldNameInput  = document.getElementById("advanced-field-name");
const advFieldTypeSelect = document.getElementById("advanced-field-type");
const advFieldsTableBody = document.querySelector("#advanced-fields-table tbody");

const loadAorDemoBtn     = document.getElementById("load-aor-demo-btn");

const latInput           = document.getElementById("latitude");
const lonInput           = document.getElementById("longitude");
const goCoordsBtn        = document.getElementById("go-coordinates-btn");

// Optional single-layer export
const exportLayerBtn     = document.getElementById("export-layer-btn");
const exportDropdown     = document.getElementById("export-layer-select");

// Save project
const saveProjectBtn     = document.getElementById("save-project-btn");

// Feature attribute modal
const attrModal          = document.getElementById("feature-attribute-modal");
const attrFormDiv        = document.getElementById("feature-attr-form");
const attrSaveBtn        = document.getElementById("feature-attr-save-btn");
const attrCancelBtn      = document.getElementById("feature-attr-cancel-btn");

// Editing buttons
const btnPoint    = document.getElementById("tool-point");
const btnLine     = document.getElementById("tool-line");
const btnPolygon  = document.getElementById("tool-polygon");
const btnModify   = document.getElementById("tool-modify");
const btnDelete   = document.getElementById("tool-delete");
const btnUndo     = document.getElementById("tool-undo");
const btnRedo     = document.getElementById("tool-redo");
const btnSnapping = document.getElementById("tool-snapping");

// 3) HELPER: random color for polygons/lines
function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

// 4) HELPER: update drawing tools enable/disable
function updateDrawingToolAvailability() {
  const layerExists = activeLayerName && layers[activeLayerName];
  if (btnPoint)   btnPoint.disabled   = !layerExists;
  if (btnLine)    btnLine.disabled    = !layerExists;
  if (btnPolygon) btnPolygon.disabled = !layerExists;
}

// 5) ADVANCED CREATE LAYER
if (openAdvancedBtn) {
  openAdvancedBtn.addEventListener("click", () => {
    advancedFields = [];
    refreshAdvancedFieldsTable();
    advLayerNameInput.value = "";
    geomTypeSelect.value = "Point";
    document.getElementById("advanced-layer-modal").style.display = "block";
  });
}
if (closeAdvancedBtn) {
  closeAdvancedBtn.addEventListener("click", () => {
    document.getElementById("advanced-layer-modal").style.display = "none";
  });
}
if (addFieldBtn) {
  addFieldBtn.addEventListener("click", () => {
    const fName = advFieldNameInput.value.trim();
    const fType = advFieldTypeSelect.value;
    if (!fName) {
      alert("Please provide a valid field name.");
      return;
    }
    advancedFields.push({ name: fName, type: fType });
    advFieldNameInput.value = "";
    refreshAdvancedFieldsTable();
  });
}
function refreshAdvancedFieldsTable() {
  advFieldsTableBody.innerHTML = "";
  advancedFields.forEach((field) => {
    const tr = document.createElement("tr");
    const tdName = document.createElement("td");
    tdName.textContent = field.name;
    tr.appendChild(tdName);
    const tdType = document.createElement("td");
    tdType.textContent = field.type;
    tr.appendChild(tdType);
    advFieldsTableBody.appendChild(tr);
  });
}
if (createLayerBtn) {
  createLayerBtn.addEventListener("click", () => {
    const layerName = advLayerNameInput.value.trim();
    if (!layerName) {
      alert("Please provide a layer name.");
      return;
    }
    if (!advancedFields.length) {
      alert("Please add at least one field.");
      return;
    }
    let chosenGeom = geomTypeSelect.value;
    let layerType = "point";
    if (chosenGeom === "LineString" || chosenGeom === "Line") layerType = "line";
    else if (chosenGeom === "Polygon") layerType = "polygon";

    const newLayer = L.geoJSON(null, {
      style: (feature) => {
        if (feature && feature.geometry.type !== "Point") {
          return { color: getRandomColor(), weight: 2 };
        }
        return {};
      },
      pointToLayer: stylePointMarker,
    }).addTo(map);

    layers[layerName] = {
      layer: newLayer,
      type: layerType,
      attributes: advancedFields.slice(),
      features: []
    };

    addLayerToManagement(layerName);
    activeLayerName = layerName;
    updateDrawingToolAvailability();

    // If you have a dropdown for export:
    if (exportDropdown) {
      const opt = document.createElement("option");
      opt.value = layerName;
      opt.textContent = layerName;
      exportDropdown.appendChild(opt);
      exportDropdown.value = layerName;
    }

    document.getElementById("advanced-layer-modal").style.display = "none";
    alert(`Layer "${layerName}" created successfully!`);
  });
}

// 6) STYLE POINT MARKERS
function stylePointMarker(feature, latlng) {
  const pop = feature.properties?.population || 0;
  let radius = 3;
  if (pop > 100000) radius = 12;
  else if (pop >= 50000) radius = 8;
  else if (pop >= 10000) radius = 5;
  return L.circleMarker(latlng, {
    radius,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    fillOpacity: 0.8,
  });
}

// GIS Tools: AOR Demo Layers
if (loadAorDemoBtn) {
  loadAorDemoBtn.addEventListener("click", () => {
    const aorCategories = [
      { name: "Govt Cont Area", type: "polygon", color: "#2e86de" },
      { name: "Rebel Cont Area", type: "polygon", color: "#c0392b" },
      { name: "BNs & Force", type: "point", color: "#16a085" },
      { name: "COB", type: "point", color: "#8e44ad" },
      { name: "Buffer Z", type: "polygon", color: "#f1c40f" },
    ];

    const drcBounds = { minLat: -13, maxLat: 5, minLng: 12, maxLng: 31 };
    const randLat = () => drcBounds.minLat + Math.random() * (drcBounds.maxLat - drcBounds.minLat);
    const randLng = () => drcBounds.minLng + Math.random() * (drcBounds.maxLng - drcBounds.minLng);

    const makePolygonFeature = () => {
      const centerLat = randLat();
      const centerLng = randLng();
      const dLat = (Math.random() * 1.5) + 0.5;
      const dLng = (Math.random() * 1.5) + 0.5;
      const coords = [
        [centerLng - dLng, centerLat - dLat],
        [centerLng + dLng, centerLat - dLat],
        [centerLng + dLng, centerLat + dLat],
        [centerLng - dLng, centerLat + dLat],
        [centerLng - dLng, centerLat - dLat],
      ];
      return { type: "Feature", properties: { name: "AOR Area", status: "active" }, geometry: { type: "Polygon", coordinates: [coords] } };
    };

    const makePointFeature = (label) => ({
      type: "Feature",
      properties: { name: label, status: "active" },
      geometry: { type: "Point", coordinates: [randLng(), randLat()] },
    });

    aorCategories.forEach((cat) => {
      const features = [];
      if (cat.type === "polygon") {
        for (let i = 0; i < 5; i++) features.push(makePolygonFeature());
      } else {
        for (let i = 0; i < 20; i++) features.push(makePointFeature(cat.name + " #" + (i + 1)));
      }
      const geojson = { type: "FeatureCollection", features };
      const layer = L.geoJSON(geojson, {
        style: (feat) => (feat.geometry.type !== "Point" ? { color: cat.color, weight: 2, fillOpacity: 0.25 } : {}),
        pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 6, color: "#000", weight: 1, fillColor: cat.color, fillOpacity: 0.85 }),
      }).addTo(map);

      layers[cat.name] = { layer, type: cat.type === "point" ? "point" : "polygon", attributes: [{ name: "name", type: "string" }, { name: "status", type: "string" }], features };
      addLayerToManagement(cat.name);
    });

    const group = L.featureGroup(aorCategories.map((c) => layers[c.name].layer));
    try { map.fitBounds(group.getBounds()); } catch {}

    alert("AOR demo layers loaded: Govt Cont Area, Rebel Cont Area, BNs & Force, COB, Buffer Z.");
  });
}

/****************************************************
 * 7) IMPORT LAYERS — Single "Import" button 
 ****************************************************/
if (importButton) {
  importButton.addEventListener("click", () => {
    if (!importInput) return;
    const files = importInput.files;
    if (!files || !files.length) {
      alert("Please select at least one file to import.");
      return;
    }

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const fileName = file.name.toLowerCase();

      if (fileName.endsWith(".mbtiles")) {
        // MBTiles
        importLocalMBTiles(file);

      } else if (fileName.endsWith(".tif") || fileName.endsWith(".tiff")) {
        // GeoTIFF
        importLocalTIFF(file);

      } else if (fileName.endsWith(".gpkg")) {
        // GeoPackage
        importLocalGeoPackage(file);

      } else if (
        fileName.endsWith(".geojson") ||
        fileName.endsWith(".json")
      ) {
        // GeoJSON
        importLocalGeoJSON(file);

      } else if (fileName.endsWith(".pbf")) {
        importLocalPBF(file); // Ensure this function is properly defined

      } else {
        alert("Unsupported file format: " + file.name);
      }
    }
  });
}

/****************************************************
 * 1) MBTiles => L.TileLayer.MBTiles
 ****************************************************/
function importLocalMBTiles(file) {
  if (!file) {
    console.error("No file selected");
    alert("Please select a valid .mbtiles file.");
    return;
  }
  const blobURL = URL.createObjectURL(file);
  const layer = L.tileLayer.mbTiles(blobURL, {
    minZoom: 0,
    maxZoom: 22,
    attribution: "MBTiles Layer",
  });

  layer.on("databaseloaded", function () {
    console.log("MBTiles database loaded.");
    layer.addTo(map);
    const layerName = file.name.replace(/\.[^/.]+$/, ""); // Remove extension for layer name
    layers[layerName] = { layer, type: "raster-tile" };
    addLayerToManagement(layerName); // Add to your management logic
  });

  layer.on("error", function (err) {
    console.error("Error loading MBTiles:", err);
    alert("Failed to load MBTiles. Please check the file format.");
  });
}

/****************************************************
 * 2) TIFF/GeoTIFF => georaster-layer-for-leaflet
 ****************************************************/
async function importLocalTIFF(file) {
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const arrayBuffer = e.target.result;
      const georaster = await parseGeoraster(arrayBuffer);

      const rasterLayer = new GeoRasterLayer({
        georaster,
        opacity: 1.0,
        pixelPerfect: false,
      });

      rasterLayer.addTo(map);
      map.fitBounds(rasterLayer.getBounds());
      const baseName = file.name.replace(/\.[^/.]+$/, "");
      layers[baseName] = {
        layer: rasterLayer,
        type: "raster-tiff",
        attributes: [],
        features: [],
      };
      addLayerToManagement(baseName);
      alert(`TIFF layer "${baseName}" imported successfully!`);
    } catch (err) {
      console.error(err);
      alert(`Failed to load TIFF: ${file.name}`);
    }
  };
  reader.readAsArrayBuffer(file);
}

/****************************************************
 * 3) GeoPackage => gpkg.js
 ****************************************************/
function importLocalGeoPackage(file) {
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const arrayBuffer = e.target.result;
      // Prefer window.GeoPackage.open if available, else use GeoPackageAPI.open
      let geoPackage;
      if (window.GeoPackage && typeof window.GeoPackage.open === 'function') {
        geoPackage = await window.GeoPackage.open(new Uint8Array(arrayBuffer));
      } else if (window.GeoPackage && window.GeoPackage.GeoPackageAPI && typeof window.GeoPackage.GeoPackageAPI.open === 'function') {
        geoPackage = await window.GeoPackage.GeoPackageAPI.open(new Uint8Array(arrayBuffer));
      } else {
        alert('GeoPackage library not loaded.');
        return;
      }
      const featureTables = geoPackage.getFeatureTables();
      if (!featureTables || !featureTables.length) {
        alert("No feature tables found in this .gpkg!");
        return;
      }
      const tableName = featureTables[0];
      const features = geoPackage.queryForGeoJSONFeaturesInTable(tableName);
      const geojson = { type: 'FeatureCollection', features };
      const baseName = file.name.replace(/\.[^/.]+$/, "");
      const newLayer = L.geoJSON(geojson, {
        style: (feat) => (feat.geometry.type !== "Point" ? { color: getRandomColor(), weight: 2 } : {}),
        pointToLayer: stylePointMarker,
      }).addTo(map);

      const attributes = Array.from(new Set((geojson.features || []).flatMap(f => Object.keys(f.properties || {}))))
        .map(name => ({ name, type: "string" }));

      layers[baseName] = {
        layer: newLayer,
        features: geojson.features || [],
        attributes,
        type: "gpkg-vector",
      };
      addLayerToManagement(baseName);
      try { map.fitBounds(newLayer.getBounds()); } catch {}
      alert(`GeoPackage vector layer "${baseName}" imported!`);
    } catch (ex) {
      console.error(ex);
      alert(`Failed to parse GeoPackage: ${file.name}`);
    }
  };
  reader.readAsArrayBuffer(file);
}

/****************************************************
 * 4) GeoJSON => Native Leaflet
 ****************************************************/
function importLocalGeoJSON(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const geojson = JSON.parse(e.target.result);
      const baseName = file.name.replace(/\.[^/.]+$/, "");
      const newLayer = L.geoJSON(geojson, {
        style: (feat) => (feat.geometry.type !== "Point" ? { color: getRandomColor(), weight: 2 } : {}),
        pointToLayer: stylePointMarker,
      }).addTo(map);

      const attributes = Array.from(new Set(geojson.features.flatMap(f => Object.keys(f.properties || {}))))
        .map(name => ({ name, type: "string" }));

      layers[baseName] = {
        layer: newLayer,
        features: geojson.features || [],
        attributes,
        type: "geojson-vector",
      };
      addLayerToManagement(baseName);
      map.fitBounds(newLayer.getBounds());
      alert(`Vector layer "${baseName}" imported successfully!`);
    } catch (err) {
      console.error(err);
      alert(`Failed to load GeoJSON: ${file.name}`);
    }
  };
  reader.readAsText(file);
}

/****************************************************
 * 5) PBF => Vector Tiles
 ****************************************************/
function importLocalPBF(file) {
  console.log("Importing PBF file:", file.name); // Debugging log

  if (!file) {
    alert("Please select a valid .pbf file.");
    return;
  }

  const blobURL = URL.createObjectURL(file);
  console.log("Blob URL created for PBF:", blobURL); // Debugging log

  const layer = L.vectorGrid.protobuf(blobURL, {
    vectorTileLayerStyles: {
      default: {
        weight: 1,
        color: "#3388ff",
        fillColor: "#3388ff",
        fillOpacity: 0.5,
      },
    },
    maxZoom: 22,
  });

  layer.on("load", () => {
    console.log("PBF file loaded successfully.");
    layer.addTo(map);

    const layerName = file.name.replace(/\.[^/.]+$/, "");
    layers[layerName] = { layer, type: "pbf-vector" };
    addLayerToManagement(layerName);
  });

  layer.on("tileerror", (err) => {
    console.error("Error loading PBF tiles:", err);
    alert("Failed to load PBF. Please check the file format.");
  });
}



/****************************************************
 * stylePointMarker(feature, latlng)
 *   - Helper for point features (in vector layers)
 ****************************************************/
function stylePointMarker(feature, latlng) {
  const pop = feature.properties?.population || 0;
  let radius = 3;
  if (pop > 100000) radius = 12;
  else if (pop >= 50000) radius = 8;
  else if (pop >= 10000) radius = 5;

  return L.circleMarker(latlng, {
    radius,
    fillColor: "#ff7800",
    color: "#000",
    weight: 1,
    fillOpacity: 0.8,
  });
}

/****************************************************
 * getRandomColor()
 *   - For styling lines/polygons
 ****************************************************/
function getRandomColor() {
  const letters = "0123456789ABCDEF";
  let color = "#";
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}


// 8) COORDINATE SEARCH
if (goCoordsBtn) {
  goCoordsBtn.addEventListener("click", () => {
    const latVal = parseFloat(latInput.value);
    const lonVal = parseFloat(lonInput.value);
    if (isNaN(latVal) || isNaN(lonVal)) {
      alert("Invalid coordinates.");
      return;
    }
    map.setView([latVal, lonVal], 12);
    L.marker([latVal, lonVal])
      .addTo(map)
      .bindPopup(`Location: ${latVal}, ${lonVal}`)
      .openPopup();
  });
}

// 9) LAYER MANAGEMENT
function addLayerToManagement(layerName) {
  const li = document.createElement("li");

  // Checkbox
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  checkbox.addEventListener("change", () => {
    if (checkbox.checked) {
      layers[layerName].layer.addTo(map);
    } else {
      map.removeLayer(layers[layerName].layer);
    }
  });
  li.appendChild(checkbox);

  // Name span (click => set active layer)
  const nameSpan = document.createElement("span");
  nameSpan.classList.add("layer-name");
  nameSpan.textContent = layerName;
  nameSpan.addEventListener("click", () => {
    activeLayerName = layerName;
    updateDrawingToolAvailability();
  });
  li.appendChild(nameSpan);

  // The three-dots icon => show context menu
  const optionsIcon = document.createElement("i");
  optionsIcon.classList.add("fa-solid", "fa-ellipsis-vertical", "layer-menu-btn");
  optionsIcon.addEventListener("click", (evt) => {
    evt.stopPropagation();
    showLayerContextMenu(evt, layerName);
  });
  const optionsSpan = document.createElement("span");
  optionsSpan.classList.add("layer-options");
  optionsSpan.appendChild(optionsIcon);
  li.appendChild(optionsSpan);

  layerListManagement.appendChild(li);

  // If none is active yet, set this one
  if (!activeLayerName) {
    activeLayerName = layerName;
    updateDrawingToolAvailability();
  }
}

// The custom menu logic
// Show menu above the dots icon
function showLayerContextMenu(evt, layerName) {
  const menu = document.getElementById("layer-context-menu");
  menu.style.display = "block";

  // Approach: use boundingRect of the clicked icon
  const iconRect = evt.target.getBoundingClientRect();
  const scrollX = window.scrollX || document.documentElement.scrollLeft;
  const scrollY = window.scrollY || document.documentElement.scrollTop;

  // Force show so we can measure
  const menuHeight = menu.offsetHeight || 120;
  const menuWidth  = menu.offsetWidth  || 160;

  // Position the menu so it appears above the icon
  let finalLeft = iconRect.left + scrollX;
  let finalTop  = iconRect.top + scrollY - menuHeight;

  // If it goes off top of the screen:
  if (finalTop < 0) {
    finalTop = iconRect.bottom + scrollY; // place below instead
  }
  // If it goes off right side:
  if ((finalLeft + menuWidth) > (window.innerWidth + scrollX)) {
    finalLeft = window.innerWidth + scrollX - menuWidth - 10;
  }

  menu.style.left = finalLeft + "px";
  menu.style.top  = finalTop + "px";

  menu.dataset.layerName = layerName;
}

// Hide menu if user clicks outside
document.addEventListener("click", (e) => {
  const menu = document.getElementById("layer-context-menu");
  // If the click is not inside the menu & not on the .layer-menu-btn icon
  if (!menu.contains(e.target) && !e.target.classList.contains("layer-menu-btn")) {
    menu.style.display = "none";
  }
});

// Attach click handlers for each menu item
document.addEventListener("DOMContentLoaded", () => {
  const menu = document.getElementById("layer-context-menu");
  menu.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => {
      const action = li.getAttribute("data-action");
      const layerName = menu.dataset.layerName;
      if (!layerName) return;
      if (action === "attr-table") openAttributeTable(layerName);
      else if (action === "edit-style") editLayerStyle(layerName);
      else if (action === "export") exportSingleLayer(layerName);
      else if (action === "bring-front") layers[layerName].layer.bringToFront();
      menu.style.display = "none";
    });
  });
});

function openAttributeTable(layerName) {
  const store = layers[layerName];
  if (!store) {
    alert(`No data for layer "${layerName}".`);
    return;
  }
  const { features, attributes } = store;
  if (!features.length) {
    alert("No features in this layer yet.");
    return;
  }
  let html = `<h2>Attribute Table for ${layerName}</h2>
    <p>Edit the attribute values and click "Save Changes".</p>
    <table border="1" style="width:100%;font-size:0.9rem;" id="attr-table">
      <tr>`;
  attributes.forEach((attr) => {
    html += `<th>${attr.name}</th>`;
  });
  html += `</tr>`;

  features.forEach((feat, fIndex) => {
    html += `<tr data-index="${fIndex}">`;
    attributes.forEach((attr) => {
      const val = feat.properties[attr.name] || "";
      html += `<td><input data-attr="${attr.name}" style="width:100%;" value="${val}" /></td>`;
    });
    html += `</tr>`;
  });
  html += `</table><br/>
    <button id="save-attrs-btn" style="padding:8px 12px;">Save Changes</button>`;

  const w = window.open("", "_blank", "width=800,height=600,scrollbars=yes");
  w.document.write(html);
  w.document.close();

  const saveBtn = w.document.getElementById("save-attrs-btn");
  saveBtn.addEventListener("click", () => {
    const rows = w.document.querySelectorAll("tr[data-index]");
    rows.forEach((row) => {
      const fIdx = row.getAttribute("data-index");
      const inputs = row.querySelectorAll("input[data-attr]");
      inputs.forEach((inp) => {
        const attrName = inp.getAttribute("data-attr");
        store.features[fIdx].properties[attrName] = inp.value;
      });
    });
    alert(`Attributes updated for layer "${layerName}".`);
  });
}

function editLayerStyle(layerName) {
  alert(`(Placeholder) Edit style for "${layerName}".`);
}

// USER LAYER MANAGEMENT FUNCTIONS
let userLayers = {}; // Store user-created layers
const userLayerList = document.getElementById("user-layer-list");

// PERSISTENCE FUNCTIONS
async function saveUserLayersToStorage() {
  try {
    // Save each user layer to Supabase bucket individually
    const savePromises = Object.keys(userLayers).map(async (layerName) => {
      const userLayer = userLayers[layerName];
      try {
        const response = await fetch(`/data/user_${layerName}/update`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            features: userLayer.data.features || []
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          console.log(`✅ User layer "${layerName}" saved to ${result.storage || 'storage'}`);
          return { layerName, success: true, storage: result.storage };
        } else {
          console.warn(`⚠️ Failed to save user layer "${layerName}" to remote storage`);
          return { layerName, success: false };
        }
      } catch (error) {
        console.error(`❌ Error saving user layer "${layerName}":`, error);
        return { layerName, success: false };
      }
    });
    
    const results = await Promise.all(savePromises);
    const failedSaves = results.filter(r => !r.success);
    
    // Fallback to localStorage for failed saves or as backup
    const layersData = {};
    Object.keys(userLayers).forEach(layerName => {
      const userLayer = userLayers[layerName];
      layersData[layerName] = {
        data: userLayer.data,
        visible: userLayer.visible
      };
    });
    localStorage.setItem('userLayers', JSON.stringify(layersData));
    
    if (failedSaves.length > 0) {
      console.warn(`⚠️ ${failedSaves.length} user layers saved to localStorage as fallback`);
    }
  } catch (error) {
    console.error('Failed to save user layers:', error);
    // Fallback to localStorage only
    try {
      const layersData = {};
      Object.keys(userLayers).forEach(layerName => {
        const userLayer = userLayers[layerName];
        layersData[layerName] = {
          data: userLayer.data,
          visible: userLayer.visible
        };
      });
      localStorage.setItem('userLayers', JSON.stringify(layersData));
    } catch (localError) {
      console.error('Failed to save user layers to localStorage:', localError);
    }
  }
}

function loadUserLayersFromStorage() {
  try {
    const savedLayers = localStorage.getItem('userLayers');
    if (savedLayers) {
      const layersData = JSON.parse(savedLayers);
      Object.keys(layersData).forEach(layerName => {
        const layerData = layersData[layerName];
        
        // Recreate the Leaflet layer from GeoJSON data
        const layer = L.geoJSON(layerData.data, {
          style: {
            color: getRandomColor(),
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.3
          },
          pointToLayer: function(feature, latlng) {
            return L.circleMarker(latlng, {
              radius: 6,
              fillColor: getRandomColor(),
              color: "#000",
              weight: 1,
              opacity: 1,
              fillOpacity: 0.8
            });
          }
        });
        
        // Add click handlers to each feature for info display
        layer.eachLayer(function(featureLayer) {
          featureLayer.on('click', function(e) {
            // Get the feature data
            const feature = featureLayer.feature;
            if (feature) {
              // Add layer name to feature properties for display
              const enhancedFeature = {
                ...feature,
                properties: {
                  ...feature.properties,
                  'Layer Name': layerName,
                  'Layer Type': 'User Layer'
                }
              };
              showFeatureInfoInSidePanel(enhancedFeature);
            }
          });
        });
        
        // Store the user layer - hide by default on page refresh
        userLayers[layerName] = {
          layer: layer,
          data: layerData.data,
          visible: false  // Always hide layers by default on page refresh
        };
        
        // Don't add to map on page load - layers are hidden by default
      });
      
      // Update the display
      updateUserLayersDisplay();
    }
  } catch (error) {
    console.error('Failed to load user layers from localStorage:', error);
  }
}

function addUserLayer(layerName, layer, geojsonData) {
  // Add click handlers to each feature for info display
  layer.eachLayer(function(featureLayer) {
    featureLayer.on('click', function(e) {
      // Get the feature data
      const feature = featureLayer.feature;
      if (feature) {
        // Add layer name to feature properties for display
        const enhancedFeature = {
          ...feature,
          properties: {
            ...feature.properties,
            'Layer Name': layerName,
            'Layer Type': 'User Layer'
          }
        };
        showFeatureInfoInSidePanel(enhancedFeature);
      }
    });
  });
  
  // Store the user layer
  userLayers[layerName] = {
    layer: layer,
    data: geojsonData,
    visible: true
  };
  
  // Add to map
  layer.addTo(map);
  
  // Save to Supabase bucket (with localStorage fallback)
  saveUserLayersToStorage();
  
  // Update the User Layers section in Table of Contents
  updateUserLayersDisplay();
}

function updateUserLayersDisplay() {
  if (!userLayerList) return;
  
  // Clear existing content
  userLayerList.innerHTML = '';
  
  if (Object.keys(userLayers).length === 0) {
    // Show empty state
    const emptyState = document.createElement('div');
    emptyState.className = 'empty-state';
    emptyState.textContent = 'No user layers created yet. Export a layer to see it here.';
    userLayerList.appendChild(emptyState);
    return;
  }
  
  // Add each user layer
  Object.keys(userLayers).forEach(layerName => {
    const userLayer = userLayers[layerName];
    const listItem = document.createElement('li');
    listItem.className = `user-layer-item ${userLayer.visible ? 'visible' : ''}`;
    
    listItem.innerHTML = `
      <div class="user-layer-info">
        <i class="fas fa-layer-group"></i>
        <span class="user-layer-name">${layerName}</span>
      </div>
      <div class="user-layer-controls">
        <button class="user-layer-toggle" title="${userLayer.visible ? 'Hide layer' : 'Show layer'}">
          <i class="fas ${userLayer.visible ? 'fa-eye' : 'fa-eye-slash'}"></i>
        </button>
        <button class="user-layer-remove" title="Remove layer">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    `;
    
    // Add event listeners
    const toggleBtn = listItem.querySelector('.user-layer-toggle');
    const removeBtn = listItem.querySelector('.user-layer-remove');
    
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleUserLayer(layerName);
    });
    
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeUserLayer(layerName);
    });
    
    // Click on layer name to zoom to layer
    listItem.querySelector('.user-layer-info').addEventListener('click', () => {
      zoomToUserLayer(layerName);
    });
    
    userLayerList.appendChild(listItem);
  });
}

function toggleUserLayer(layerName) {
  const userLayer = userLayers[layerName];
  if (!userLayer) return;
  
  if (userLayer.visible) {
    map.removeLayer(userLayer.layer);
    userLayer.visible = false;
  } else {
    userLayer.layer.addTo(map);
    userLayer.visible = true;
  }
  
  // Save to localStorage
  saveUserLayersToStorage();
  
  updateUserLayersDisplay();
}

function removeUserLayer(layerName) {
  const userLayer = userLayers[layerName];
  if (!userLayer) return;
  
  // Remove from map
  if (userLayer.visible) {
    map.removeLayer(userLayer.layer);
  }
  
  // Remove from storage
  delete userLayers[layerName];
  
  // Save to localStorage
  saveUserLayersToStorage();
  
  // Update display
  updateUserLayersDisplay();
}

function zoomToUserLayer(layerName) {
  const userLayer = userLayers[layerName];
  if (!userLayer || !userLayer.visible) return;
  
  try {
    const bounds = userLayer.layer.getBounds();
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  } catch (error) {
    console.warn('Could not zoom to layer bounds:', error);
  }
}

function exportSingleLayer(layerName) {
  const store = layers[layerName];
  if (!store) return;
  const { layer, features } = store;
  const updated = [];
  layer.eachLayer((lyr) => updated.push(lyr.toGeoJSON()));
  store.features = updated;
  const geojson = { type: "FeatureCollection", features: updated };
  
  // Create a copy of the layer for user layers
  const userLayerCopy = L.geoJSON(geojson, {
    style: layer.options.style || {
      color: getRandomColor(),
      weight: 2,
      opacity: 0.8,
      fillOpacity: 0.3
    },
    pointToLayer: layer.options.pointToLayer || stylePointMarker,
    onEachFeature: (feature, layer) => {
      if (feature.properties) {
        let popupContent = '<div class="feature-popup">';
        Object.keys(feature.properties).forEach(key => {
          popupContent += `<strong>${key}:</strong> ${feature.properties[key]}<br>`;
        });
        popupContent += '</div>';
        layer.bindPopup(popupContent);
      }
    }
  });
  
  // Add to user layers
  addUserLayer(`${layerName}`, userLayerCopy, geojson);
  
  alert(`Layer "${layerName}" saved to User Layers!`);
}

// 10) SAVE SELECTED LAYERS TO USER LAYERS
if (exportZipBtn) {
  exportZipBtn.addEventListener("click", () => {
    const liElements = layerListManagement.querySelectorAll("li");
    const checkedNames = [];
    liElements.forEach((li) => {
      const chk = li.querySelector('input[type="checkbox"]');
      const nmSpan = li.querySelector(".layer-name");
      if (chk && chk.checked && nmSpan) {
        checkedNames.push(nmSpan.textContent);
      }
    });
    if (!checkedNames.length) {
      alert("No layers selected to save.");
      return;
    }
    
    let savedCount = 0;
    checkedNames.forEach((nm) => {
      const store = layers[nm];
      if (!store) return;
      const { layer } = store;
      const updated = [];
      layer.eachLayer((lyr) => updated.push(lyr.toGeoJSON()));
      store.features = updated;
      const geojson = { type: "FeatureCollection", features: updated };
      
      // Create a copy of the layer for user layers
      const userLayerCopy = L.geoJSON(geojson, {
        style: layer.options.style || {
          color: getRandomColor(),
          weight: 2,
          opacity: 0.8,
          fillOpacity: 0.3
        },
        pointToLayer: layer.options.pointToLayer || stylePointMarker,
        onEachFeature: (feature, layer) => {
          if (feature.properties) {
            let popupContent = '<div class="feature-popup">';
            Object.keys(feature.properties).forEach(key => {
              popupContent += `<strong>${key}:</strong> ${feature.properties[key]}<br>`;
            });
            popupContent += '</div>';
            layer.bindPopup(popupContent);
          }
        }
      });
      
      // Add to user layers
      addUserLayer(`${nm}`, userLayerCopy, geojson);
      savedCount++;
    });
    
    alert(`${savedCount} layer(s) saved to User Layers!`);
  });
}

// 11) SAVE PROJECT (if you have a button for that)
if (saveProjectBtn) {
  saveProjectBtn.addEventListener("click", () => {
    const projectData = {};
    Object.keys(layers).forEach((nm) => {
      const store = layers[nm];
      const updated = [];
      store.layer.eachLayer((lyr) => updated.push(lyr.toGeoJSON()));
      store.features = updated;
      projectData[nm] = {
        features: updated,
        attributes: store.attributes,
        type: store.type
      };
    });
    // store map center/zoom
    projectData.mapState = {
      center: map.getCenter(),
      zoom: map.getZoom()
    };

    const blob = new Blob([JSON.stringify(projectData, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = "sam_un_project.json";
    a.click();
    URL.revokeObjectURL(url);
    alert("Project saved!");
  });
}

// 12) DRAWING & FEATURE ATTRIBUTE MODAL
let pendingDrawLayer = null;

function setupDrawingEvents() {
  if (!map) return;
  
  // Distinguish drawing from measurement using the isMeasurementMode flag
  map.on(L.Draw.Event.CREATED, (evt) => {
    if (isMeasurementMode) return; // Ignore this for measurement tools

    if (!activeLayerName || !layers[activeLayerName]) {
      alert("Please select or create a layer first.");
      return;
    }

    // Add shape to the edit group so user can see it
    pendingDrawLayer = evt.layer;
    editFeatureGroup.addLayer(pendingDrawLayer);

    // Build dynamic form for that layer's attributes
    const store = layers[activeLayerName];
    attrFormDiv.innerHTML = "";
    store.attributes.forEach((attr) => {
      const label = document.createElement("label");
      label.textContent = attr.name + ":";
      const input = document.createElement("input");
      input.type =
        attr.type === "integer" || attr.type === "float" ? "number" : "text";
      input.dataset.attrName = attr.name;
      attrFormDiv.appendChild(label);
      attrFormDiv.appendChild(input);
    });

    // Show the attribute modal
    attrModal.style.display = "block";
  });
}

if (attrSaveBtn) {
  attrSaveBtn.addEventListener("click", async () => {
    if (!pendingDrawLayer || !activeLayerName || !layers[activeLayerName]) {
      attrModal.style.display = "none";
      return;
    }
    const store = layers[activeLayerName];
    const inputs = attrFormDiv.querySelectorAll("input[data-attr-name]");
    const propObj = {};
    inputs.forEach((inp) => {
      propObj[inp.dataset.attrName] = inp.value || null;
    });

    // Build final feature
    const geometry = pendingDrawLayer.toGeoJSON().geometry;
    const newFeature = {
      type: "Feature",
      properties: propObj,
      geometry,
    };
    
    // Add to store and layer locally first
    store.features.push(newFeature);
    store.layer.addData(newFeature);

    // Keep it in editFeatureGroup for future modifications
    actionStack.push({ type: "add", layer: pendingDrawLayer });
    undoneStack = [];

    // Save to Supabase bucket (with local fallback)
    try {
      const response = await fetch(`/data/${activeLayerName}/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          features: store.features
        })
      });
      
      const result = await response.json();
      if (response.ok) {
        console.log(`✅ Layer "${activeLayerName}" saved to ${result.storage || 'storage'}`);
        alert(`Feature added to "${activeLayerName}" and saved to ${result.storage === 'supabase' ? 'Supabase bucket' : 'local storage'}!`);
      } else {
        console.warn(`⚠️ Failed to save layer "${activeLayerName}":`, result.error);
        alert(`Feature added to "${activeLayerName}" locally, but failed to save to remote storage.`);
      }
    } catch (error) {
      console.error(`❌ Error saving layer "${activeLayerName}":`, error);
      alert(`Feature added to "${activeLayerName}" locally, but failed to save to remote storage.`);
    }

    // Hide modal
    attrModal.style.display = "none";
    pendingDrawLayer = null;
  });
}
if (attrCancelBtn) {
  attrCancelBtn.addEventListener("click", () => {
    if (pendingDrawLayer) editFeatureGroup.removeLayer(pendingDrawLayer);
    pendingDrawLayer = null;
    attrModal.style.display = "none";
  });
}

// 13) EDITING TOOLBAR BUTTONS
function clearActiveTool() {
  if (drawHandler) {
    drawHandler.disable();
    drawHandler = null;
  }
  [
    btnPoint, btnLine, btnPolygon, 
    btnModify, btnDelete, btnUndo, btnRedo, btnSnapping
  ].forEach((b) => b && b.classList.remove("active-tool"));
  updateDrawingToolAvailability();
}

// POINT
if (btnPoint) {
  btnPoint.addEventListener("click", () => {
    if (!activeLayerName || !layers[activeLayerName]) {
      alert("No active layer selected!");
      return;
    }
    clearActiveTool();
    btnPoint.classList.add("active-tool");
    drawHandler = new L.Draw.Marker(map, {});
    drawHandler.enable();
  });
}

// LINE
if (btnLine) {
  btnLine.addEventListener("click", () => {
    if (!activeLayerName || !layers[activeLayerName]) {
      alert("No active layer selected!");
      return;
    }
    clearActiveTool();
    btnLine.classList.add("active-tool");
    drawHandler = new L.Draw.Polyline(map, {
      shapeOptions: { color: "blue", weight: 3 },
    });
    drawHandler.enable();
  });
}

// POLYGON
if (btnPolygon) {
  btnPolygon.addEventListener("click", () => {
    if (!activeLayerName || !layers[activeLayerName]) {
      alert("No active layer selected!");
      return;
    }
    clearActiveTool();
    btnPolygon.classList.add("active-tool");
    drawHandler = new L.Draw.Polygon(map, {
      shapeOptions: { color: "green", weight: 2 },
      showArea: true,
    });
    drawHandler.enable();
  });
}

// MODIFY => only edits existing shapes
if (btnModify) {
  btnModify.addEventListener("click", () => {
    clearActiveTool();
    btnModify.classList.add("active-tool");
    const drawToolbar = document.querySelector(".leaflet-draw-toolbar-top");
    if (drawToolbar) drawToolbar.style.display = "block";

    // Enable editing on each shape in editFeatureGroup
    editFeatureGroup.eachLayer((lyr) => {
      if (lyr.editing) lyr.editing.enable();
    });
  });
}

const finishModifyBtn = document.getElementById("finish-modify");
finishModifyBtn.addEventListener("click", () => {
  // 1) Disable editing for all shapes
  editFeatureGroup.eachLayer((lyr) => {
    if (lyr.editing && lyr.editing.enabled()) {
      lyr.editing.disable();
      // 2) Capture new geometry if needed
      //    (Find matching feature in your store, update geometry)
      const updatedGeo = lyr.toGeoJSON();
      const store = layers[activeLayerName];
      if (store) {
        // If the layer's 'features' has a matching feature (by some ID or index),
        // update its geometry. If you lack an ID system, you can do approximate matching.
      }
    }
  });
  alert("Geometry changes saved (editing disabled)!");
});


// DELETE => remove shape on next map click
if (btnDelete) {
  btnDelete.addEventListener("click", () => {
    clearActiveTool();
    btnDelete.classList.add("active-tool");
    map.once("click", (e) => {
      map.eachLayer((lyr) => {
        if (lyr instanceof L.Polygon || lyr instanceof L.Polyline || lyr instanceof L.Marker) {
          if (lyr._containsPoint && lyr._containsPoint(e.layerPoint)) {
            map.removeLayer(lyr);
            actionStack.push({ type: "delete", layer: lyr });
            undoneStack = [];
          }
        }
      });
    });
  });
}

// UNDO
if (btnUndo) {
  btnUndo.addEventListener("click", () => {
    if (!actionStack.length) return;
    const lastAction = actionStack.pop();
    btnUndo.classList.add("active-tool");
    setTimeout(() => btnUndo.classList.remove("active-tool"), 500);

    if (lastAction.type === "add") {
      map.removeLayer(lastAction.layer);
    } else if (lastAction.type === "delete") {
      map.addLayer(lastAction.layer);
    }
    undoneStack.push(lastAction);
  });
}

// REDO
if (btnRedo) {
  btnRedo.addEventListener("click", () => {
    if (!undoneStack.length) return;
    const undone = undoneStack.pop();
    btnRedo.classList.add("active-tool");
    setTimeout(() => btnRedo.classList.remove("active-tool"), 500);

    if (undone.type === "add") {
      map.addLayer(undone.layer);
      actionStack.push(undone);
    } else if (undone.type === "delete") {
      map.removeLayer(undone.layer);
      actionStack.push(undone);
    }
  });
}

// SNAPPING (placeholder)
if (btnSnapping) {
  btnSnapping.addEventListener("click", () => {
    snappingEnabled = !snappingEnabled;
    if (snappingEnabled) {
      btnSnapping.classList.add("active-tool");
      alert("Snapping ON (placeholder).");
    } else {
      btnSnapping.classList.remove("active-tool");
      alert("Snapping OFF.");
    }
  });
}

// ==========================
// DAILY SITREP MVP (Phase 1)
// ==========================
// Dedicated layer for SITREPs
// Create layer lazily only when user visualizes

function sitrepSeverityColor(severity) {
  const sev = String(severity || "").toLowerCase();
  switch (sev) {
    case "critical":
    case "red":
      return "#d73027";
    case "high":
    case "orange":
      return "#fc8d59";
    case "medium":
    case "moderate":
    case "yellow":
      return "#fee08b";
    case "low":
    case "green":
      return "#1a9850";
    default:
      return "#2c7fb8"; // default blue
  }
}

// Military marker configuration for different source categories and incident types
// Make it globally accessible for chatbot
const MILITARY_MARKERS = {
  source_categories: {
    "own": {
      icon: "fas fa-shield-alt", // Shield for own forces
      color: "#2b8a3e", // green
      bgColor: "#ffffff",
      shape: "square"
    },
    "local": {
      icon: "fas fa-building", // Building for local government
      color: "#1f78b4", // blue
      bgColor: "#ffffff", 
      shape: "circle"
    },
    "rebel": {
      icon: "fas fa-exclamation-triangle", // Warning triangle for rebel groups
      color: "#e31a1c", // red
      bgColor: "#ffffff",
      shape: "diamond"
    },
    "ngo": {
      icon: "fas fa-hands-helping", // Helping hands for NGOs
      color: "#ff7f00", // orange
      bgColor: "#ffffff",
      shape: "circle"
    },
    "other": {
      icon: "fas fa-question-circle", // Question mark for other sources
      color: "#6a3d9a", // purple
      bgColor: "#ffffff",
      shape: "circle"
    }
  },
  incident_types: {
    "route_disruption": {
      icon: "fas fa-road", // Road icon for route disruptions
      color: "#ff3b30", // red
      bgColor: "#ffffff",
      shape: "triangle",
      size: "large"
    },
    "security_incident": {
      icon: "fas fa-shield-virus", // Security shield
      color: "#dc3545", // danger red
      bgColor: "#ffffff",
      shape: "diamond",
      size: "large"
    },
    "medical_emergency": {
      icon: "fas fa-plus-circle", // Medical cross
      color: "#28a745", // success green
      bgColor: "#ffffff",
      shape: "circle",
      size: "large"
    },
    "logistics": {
      icon: "fas fa-truck", // Truck for logistics
      color: "#17a2b8", // info blue
      bgColor: "#ffffff",
      shape: "square",
      size: "medium"
    },
    "intelligence": {
      icon: "fas fa-eye", // Eye for intelligence
      color: "#6f42c1", // purple
      bgColor: "#ffffff",
      shape: "diamond",
      size: "medium"
    },
    "patrol": {
      icon: "fas fa-walking", // Walking figure for patrol
      color: "#20c997", // teal
      bgColor: "#ffffff",
      shape: "circle",
      size: "medium"
    }
  }
};

// Make MILITARY_MARKERS globally accessible for chatbot
window.MILITARY_MARKERS = MILITARY_MARKERS;

// Create military marker icon
function createMilitaryMarker(config, size = "medium") {
  const sizes = {
    small: { width: 24, height: 24, fontSize: "10px" },
    medium: { width: 32, height: 32, fontSize: "14px" },
    large: { width: 40, height: 40, fontSize: "18px" }
  };
  
  const sizeConfig = sizes[size] || sizes.medium;
  const shape = config.shape || "circle";
  
  let shapeStyle = "";
  switch (shape) {
    case "square":
      shapeStyle = "border-radius: 3px;";
      break;
    case "diamond":
      shapeStyle = "transform: rotate(45deg); border-radius: 3px;";
      break;
    case "triangle":
      shapeStyle = "clip-path: polygon(50% 0%, 0% 100%, 100% 100%); border-radius: 0;";
      break;
    case "circle":
    default:
      shapeStyle = "border-radius: 50%;";
      break;
  }
  
  const iconHtml = `
    <div style="
      width: ${sizeConfig.width}px; 
      height: ${sizeConfig.height}px; 
      background-color: ${config.bgColor}; 
      border: 2px solid ${config.color}; 
      ${shapeStyle}
      display: flex; 
      align-items: center; 
      justify-content: center;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    ">
      <i class="${config.icon}" style="
        color: ${config.color}; 
        font-size: ${sizeConfig.fontSize};
        ${shape === "diamond" ? "transform: rotate(-45deg);" : ""}
      "></i>
    </div>
  `;
  
  return L.divIcon({
    className: "military-marker",
    html: iconHtml,
    iconSize: [sizeConfig.width, sizeConfig.height],
    iconAnchor: [sizeConfig.width / 2, sizeConfig.height / 2],
    popupAnchor: [0, -sizeConfig.height / 2]
  });
}

function sitrepSourceColor(category) {
  const cat = String(category || "").toLowerCase();
  switch (cat) {
    case "own":
      return "#2b8a3e"; // green
    case "local":
      return "#1f78b4"; // blue
    case "rebel":
      return "#e31a1c"; // red
    case "ngo":
      return "#ff7f00"; // orange
    case "other":
      return "#6a3d9a"; // purple
    default:
      return "#2c7fb8"; // fallback blue
  }
}

function renderSitrepPoint(feature, latlng) {
  const props = feature.properties || {};
  const incidentType = String(props.incident_type || "").toLowerCase();
  const sourceCategory = String(props.source_category || "").toLowerCase();
  
  // Check if route disruptions layer is active for route disruption incidents
  const isDisruption = incidentType === "route_disruption";
  const routeDisruptionsLayerActive = layerVisibility["route disruptions"];
  
  // Priority: incident type markers override source category markers
  // But only show route disruption markers if the route disruptions layer is active
  if (incidentType && MILITARY_MARKERS.incident_types[incidentType]) {
    if (isDisruption && !routeDisruptionsLayerActive) {
      // Don't show route disruption markers unless route disruptions layer is active
      // Fall through to source category markers instead
    } else {
      const config = MILITARY_MARKERS.incident_types[incidentType];
      const size = config.size || "medium";
      return L.marker(latlng, { 
        icon: createMilitaryMarker(config, size)
      });
    }
  }
  
  // Fallback to source category markers
  if (sourceCategory && MILITARY_MARKERS.source_categories[sourceCategory]) {
    const config = MILITARY_MARKERS.source_categories[sourceCategory];
    return L.marker(latlng, { 
      icon: createMilitaryMarker(config, "medium")
    });
  }
  
  // Legacy fallback for route disruptions (backward compatibility)
  // Only show if route disruptions layer is active
  if (isDisruption && routeDisruptionsLayerActive) {
    const config = MILITARY_MARKERS.incident_types["route_disruption"];
    return L.marker(latlng, { 
      icon: createMilitaryMarker(config, "large")
    });
  }
  
  // Final fallback to simple circle markers
  const color = sitrepSourceColor(props.source_category);
  return L.circleMarker(latlng, {
    radius: 7,
    color,
    weight: 2,
    fillColor: color,
    fillOpacity: 0.6,
  });
}

function sitrepPopupHtml(props = {}) {
  const source = props.source || "N/A";
  const sourceCategory = props.source_category || "";
  const title = props.title || "Untitled";
  const description = props.description || "";
  const severity = props.severity || "unknown";
  const status = props.status || "";
  const unit = props.unit || "";
  const contact = props.contact || "";
  const created = props.created_at || "";
  const incidentType = props.incident_type || "";
  return `
    <div class="sitrep-popup">
      <strong>${title}</strong><br/>
      <em>Source:</em> ${source}${sourceCategory ? ` (${sourceCategory})` : ""}<br/>
      ${status ? `<em>Status:</em> ${status}<br/>` : ""}
      ${unit ? `<em>Unit:</em> ${unit}<br/>` : ""}
      ${contact ? `<em>POC:</em> ${contact}<br/>` : ""}
      ${incidentType ? `<em>Incident:</em> ${incidentType}<br/>` : ""}
      <em>Severity:</em> ${severity}<br/>
      <em>Reported:</em> ${created}<br/>
      <div style="margin-top:6px; max-width:240px; white-space:pre-wrap;">${description}</div>
    </div>
  `;
}

function getSitrepFilters() {
  const rangeEl = document.getElementById("sitrep-range");
  const fromEl = document.getElementById("sitrep-from-date");
  const toEl = document.getElementById("sitrep-to-date");
  const sourceEls = document.querySelectorAll(".sitrep-source-option");
  const filters = {};
  const rangeVal = rangeEl?.value?.trim();
  const fromVal = fromEl?.value?.trim();
  const toVal = toEl?.value?.trim();
  if (rangeVal) filters.rangeDays = parseInt(rangeVal, 10);
  if (fromVal) filters.fromDate = fromVal;
  if (toVal) filters.toDate = toVal;
  
  // Preferred sources from explicit checkboxes (if present)
  const sources = [];
  sourceEls.forEach((el) => { if (el.checked) sources.push(el.value); });
  if (sources.length) {
    filters.sources = sources;
  } else {
    // Fallback to currently selected Activity Marking virtual layers
    const selectedActivity = ACTIVITY_LAYER_NAMES
      .filter((name) => layerVisibility[name])
      .map((name) => ACTIVITY_TO_SOURCE[name])
      .filter(Boolean); // Remove any undefined/null values
    if (selectedActivity.length) {
      filters.sources = selectedActivity;
    }
  }
  
  // Handle route disruptions special filtering
  if (layerVisibility["route disruptions"]) {
    filters.incidentType = "route_disruption";
  }
  
  return filters;
}

async function refreshSitreps(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.rangeDays) params.set("rangeDays", String(filters.rangeDays));
    if (filters.fromDate) params.set("fromDate", String(filters.fromDate));
    if (filters.toDate) params.set("toDate", String(filters.toDate));
    if (Array.isArray(filters.sources) && filters.sources.length) {
      params.set("sources", filters.sources.join(","));
    }
    const url = params.toString() ? `/api/sitreps.geojson?${params.toString()}` : "/api/sitreps.geojson";
    const res = await fetch(url);
    if (!res.ok) throw new Error(await res.text());
    const geojson = await res.json();

    sitrepLayer.clearLayers();
    const gj = L.geoJSON(geojson, {
      filter: (feature) => {
        if (filters.incidentType) {
          return String(feature?.properties?.incident_type || "") === filters.incidentType;
        }
        return true;
      },
      pointToLayer: renderSitrepPoint,
      onEachFeature: (feature, layer) => {
        layer.bindPopup(sitrepPopupHtml(feature.properties));
      },
    });
    sitrepLayer.addLayer(gj);
    if (routePolyline) {
      updateDisruptionProximity(routePolyline);
    }
  } catch (err) {
    console.error("Failed to refresh SITREPs:", err);
  }
}

const sitrepSubmitBtn = document.getElementById("sitrep-submit");
if (sitrepSubmitBtn) {
  sitrepSubmitBtn.addEventListener("click", async () => {
    try {
      const source = document.getElementById("sitrep-source")?.value?.trim();
      const title = document.getElementById("sitrep-title")?.value?.trim();
      const description = document.getElementById("sitrep-desc")?.value?.trim();
      const severity = document.getElementById("sitrep-severity")?.value?.trim();
      const latStr = document.getElementById("sitrep-lat")?.value?.trim();
      const lonStr = document.getElementById("sitrep-lon")?.value?.trim();

      if (!source || !title || !latStr || !lonStr) {
        alert("Please fill Source, Title, Latitude and Longitude.");
        return;
      }
      const lat = parseFloat(latStr);
      const lon = parseFloat(lonStr);
      if (Number.isNaN(lat) || Number.isNaN(lon)) {
        alert("Latitude/Longitude must be valid numbers.");
        return;
      }

      const sourceCategory = document.getElementById("sitrep-source-category")?.value || "";
      const status = document.getElementById("sitrep-status-field")?.value || "";
      const unit = document.getElementById("sitrep-unit")?.value?.trim() || "";
      const contact = document.getElementById("sitrep-contact")?.value?.trim() || "";
      const incidentType = document.getElementById("sitrep-incident-type")?.value || "";
      const payload = { source, source_category: sourceCategory, status, unit, contact, title, description, severity, incident_type: incidentType, lat, lon };
      const res = await fetch("/api/sitreps", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const txt = await res.text();
        alert("Failed to submit SITREP: " + txt);
        return;
      }

      // Clear form
      document.getElementById("sitrep-source").value = "";
      document.getElementById("sitrep-source-category") && (document.getElementById("sitrep-source-category").value = "");
      document.getElementById("sitrep-status-field") && (document.getElementById("sitrep-status-field").value = "reported");
      document.getElementById("sitrep-unit") && (document.getElementById("sitrep-unit").value = "");
      document.getElementById("sitrep-contact") && (document.getElementById("sitrep-contact").value = "");
      document.getElementById("sitrep-title").value = "";
      document.getElementById("sitrep-desc").value = "";
      document.getElementById("sitrep-severity").value = "";
      document.getElementById("sitrep-incident-type") && (document.getElementById("sitrep-incident-type").value = "");
      document.getElementById("sitrep-lat").value = "";
      document.getElementById("sitrep-lon").value = "";

      // Do not auto-refresh; require user to click Visualize to show markers
      alert("SITREP submitted.");
    } catch (err) {
      console.error(err);
      alert("Unexpected error while submitting SITREP.");
    }
  });
}

// SITREP filter Apply/Reset
const applyFiltersBtn = document.getElementById("sitrep-filter-apply");
if (applyFiltersBtn) {
  applyFiltersBtn.addEventListener("click", () => {
    const filters = getSitrepFilters();
    
    // Apply activity marking layer filters if any are active
    const activeActivityLayers = ACTIVITY_LAYER_NAMES.filter((name) => layerVisibility[name]);
    if (activeActivityLayers.length > 0) {
      // Map activity layers to their corresponding sources
      const activeSources = activeActivityLayers
        .map((name) => ACTIVITY_TO_SOURCE[name])
        .filter(Boolean);
      
      // Only override sources if no explicit sources were selected in checkboxes
      if (!filters.sources || filters.sources.length === 0) {
        filters.sources = activeSources;
      }
      
      // Handle route disruptions special case
      if (layerVisibility["route disruptions"]) {
        filters.incidentType = "route_disruption";
      }
    }
    
    // Ensure the SITREP layer group exists and is attached
    if (typeof sitrepLayer === "undefined" || !sitrepLayer) {
      if (map) {
        sitrepLayer = L.layerGroup().addTo(map);
      } else {
        console.error('Map not initialized when trying to create sitrepLayer for heatmap');
        return;
      }
    }
    refreshSitreps(filters);
  });
}
const resetFiltersBtn = document.getElementById("sitrep-filter-reset");
if (resetFiltersBtn) {
  resetFiltersBtn.addEventListener("click", () => {
    const rangeEl = document.getElementById("sitrep-range");
    const fromEl = document.getElementById("sitrep-from-date");
    const toEl = document.getElementById("sitrep-to-date");
    const sourceEls = document.querySelectorAll(".sitrep-source-option");
    if (rangeEl) rangeEl.value = "30"; // default to last 30 days
    if (fromEl) fromEl.value = "";
    if (toEl) toEl.value = "";
    sourceEls.forEach((el) => { el.checked = false; });
    // Clear SITREP markers from map
    if (typeof sitrepLayer !== "undefined" && sitrepLayer) {
      sitrepLayer.clearLayers();
    }
  });
}

// Heat Map functionality
let heatmapLayer = null;
let isHeatmapVisible = false;

// Function to get active activity layers for filtering
function getActiveActivitySources() {
  // Use the same logic as getSitrepFilters() for consistency
  const sourceEls = document.querySelectorAll(".sitrep-source-option");
  
  // First check for explicit source checkboxes
  const sources = [];
  sourceEls.forEach((el) => { if (el.checked) sources.push(el.value); });
  if (sources.length) {
    return sources;
  }
  
  // Fallback to currently selected Activity Marking virtual layers
  const selectedActivity = ACTIVITY_LAYER_NAMES
    .filter((name) => layerVisibility[name])
    .map((name) => ACTIVITY_TO_SOURCE[name])
    .filter(Boolean); // Remove any undefined/null values
  
  // If no activity layers are explicitly selected, return all sources for backward compatibility
  if (selectedActivity.length === 0) {
    return Object.values(ACTIVITY_TO_SOURCE).filter(Boolean);
  }
  
  return selectedActivity;
}

// Heat map toggle button event listener
const heatmapToggleBtn = document.getElementById("heatmap-toggle");
if (heatmapToggleBtn) {
  heatmapToggleBtn.addEventListener("click", async () => {
    if (isHeatmapVisible) {
      // Hide heatmap and show SITREP markers
      if (heatmapLayer) {
        map.removeLayer(heatmapLayer);
        isHeatmapVisible = false;
        heatmapToggleBtn.innerHTML = '<i class="fa-solid fa-fire"></i> Show Heat Map';
        
        // Show SITREP markers again
        if (sitrepLayer && !map.hasLayer(sitrepLayer)) {
          map.addLayer(sitrepLayer);
        }
      }
    } else {
      // Hide SITREP markers and generate/show heatmap
      if (sitrepLayer && map.hasLayer(sitrepLayer)) {
        map.removeLayer(sitrepLayer);
      }
      
      // Generate and show heatmap using active activity layers
      await generateHeatmap();
    }
  });
}

// Function to generate heat map
async function generateHeatmap() {
  try {
    // Get current date range filters if they exist
    const filters = getSitrepFilters();
    
    // Get active activity layer sources
    const activeSources = getActiveActivitySources();
    console.log('Active activity sources for heatmap:', activeSources);
    console.log('Layer visibility state:', layerVisibility);
    
    // Build query parameters
    const params = new URLSearchParams();
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    // Add active sources as a comma-separated string (if any are selected)
    if (activeSources.length > 0) {
      params.append('sources', activeSources.join(','));
    }
    
    // Fetch heat map data
    const response = await fetch(`/api/sitreps/heatmap?${params.toString()}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const heatmapResponse = await response.json();
    
    // Remove existing heat map layer
    if (heatmapLayer && isHeatmapVisible) {
      map.removeLayer(heatmapLayer);
    }
    
    // Extract heatPoints from the response object
    const heatmapData = heatmapResponse.heatPoints || [];
    
    // Convert data to heat map format [lat, lng, intensity]
    const heatPoints = heatmapData.map(point => [
      point.lat,
      point.lng,
      point.intensity
    ]);
    
    if (heatPoints.length === 0) {
      const sourceText = activeSources.length > 0 ? `active sources (${activeSources.join(', ')})` : 'selected filters';
      alert(`No data available for the ${sourceText}.`);
      return;
    }
    
    // Calculate max intensity for better scaling
    const maxIntensity = Math.max(...heatPoints.map(p => p[2]));
    
    // Create heat map layer with improved visibility settings
    heatmapLayer = L.heatLayer(heatPoints, {
      radius: 50,        // Increased from 25 for better visibility
      blur: 25,          // Increased from 15 for smoother gradients
      maxZoom: 17,
      max: maxIntensity > 1 ? maxIntensity : 1, // Ensure proper scaling
      minOpacity: 0.3,   // Add minimum opacity for better visibility
      gradient: {
        0.0: '#313695',
        0.1: '#4575b4',
        0.2: '#74add1',
        0.3: '#abd9e9',
        0.4: '#e0f3f8',
        0.5: '#ffffcc',
        0.6: '#fee090',
        0.7: '#fdae61',
        0.8: '#f46d43',
        0.9: '#d73027',
        1.0: '#a50026'
      }
    });
    
    // Add heat map to map
    heatmapLayer.addTo(map);
    isHeatmapVisible = true;
    
    // Update button text
    const heatmapToggleBtn = document.getElementById("heatmap-toggle");
    if (heatmapToggleBtn) {
      heatmapToggleBtn.innerHTML = '<i class="fa-solid fa-fire"></i> Hide Heat Map';
    }
    
    const sourceText = activeSources.length > 0 ? `sources: ${activeSources.join(', ')}` : 'all sources';
    const metadata = heatmapResponse.metadata || {};
    console.log(`Heat map generated with ${heatPoints.length} data points for ${sourceText}`, {
      totalIncidents: metadata.totalIncidents,
      gridSize: metadata.gridSize,
      criticalAreas: metadata.criticalAreas?.length || 0
    });
    
  } catch (error) {
    console.error("Error generating heat map:", error);
    alert("Error generating heat map. Please try again.");
  }
}

// Do not auto-load SITREPs on page load; user must click "Visualize SITREPs" to show markers
document.addEventListener("DOMContentLoaded", () => {
  // Initialize the map first
  initializeMap();
  
  // Load user layers from localStorage
  loadUserLayersFromStorage();
  
  // Initialize user layers display (will be updated by loadUserLayersFromStorage if there are saved layers)
  updateUserLayersDisplay();
});