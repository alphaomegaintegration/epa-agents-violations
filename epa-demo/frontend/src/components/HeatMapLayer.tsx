import { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import { SystemMarkerData } from '../types/geographic';

// Extend Leaflet types to include heatLayer
declare module 'leaflet' {
  namespace L {
    function heatLayer(
      latlngs: Array<[number, number, number]>,
      options?: any
    ): any;
  }
}

interface HeatMapLayerProps {
  systems: SystemMarkerData[];
  isVisible: boolean;
}

const HeatMapLayer: React.FC<HeatMapLayerProps> = ({ systems, isVisible }) => {
  const map = useMap();

  useEffect(() => {
    if (!isVisible || systems.length === 0) return;

    // Calculate heat map data points
    const heatPoints = generateHeatMapData(systems);
    
    // Create heat layer with enhanced visibility
    const heatLayer = L.heatLayer(heatPoints, {
      radius: 120,          // Increased radius for larger heat zones
      blur: 60,             // Reduced blur for sharper edges
      maxZoom: 18,
      max: 1.0,
      minOpacity: 0.4,      // Minimum opacity to ensure visibility
      gradient: {
        0.0: 'rgba(0, 255, 0, 0.8)',    // Green with higher opacity
        0.3: 'rgba(255, 255, 0, 0.9)',  // Yellow with higher opacity
        0.6: 'rgba(255, 128, 0, 0.95)', // Orange with higher opacity
        1.0: 'rgba(255, 0, 0, 1.0)'     // Red with full opacity
      }
    });

    // Add to map
    heatLayer.addTo(map);

    // Cleanup function
    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, systems, isVisible]);

  return null; // This component doesn't render anything visible directly
};

// Generate heat map data points from water systems
function generateHeatMapData(systems: SystemMarkerData[]): Array<[number, number, number]> {
  const heatPoints: Array<[number, number, number]> = [];
  
  systems.forEach(system => {
    const intensity = calculateIntensity(system);
    const baseRadius = getRegionalRadius(system.population);
    
    // Add main system point
    heatPoints.push([system.lat, system.lng, intensity]);
    
    // Add surrounding points to create regional effect for large systems
    if (system.population > 1000000) {
      const offsets = [
        [-0.2, -0.2], [0.2, -0.2], [-0.2, 0.2], [0.2, 0.2], // Corners
        [-0.3, 0], [0.3, 0], [0, -0.3], [0, 0.3]             // Sides
      ];
      
      offsets.forEach(([latOffset, lngOffset]) => {
        heatPoints.push([
          system.lat + latOffset, 
          system.lng + lngOffset, 
          intensity * 0.4 // Reduced intensity for surrounding points
        ]);
      });
    }
    
    // Add metropolitan area effect for major systems
    if (system.population > 2000000) {
      const largeOffsets = [
        [-0.5, -0.5], [0.5, -0.5], [-0.5, 0.5], [0.5, 0.5]
      ];
      
      largeOffsets.forEach(([latOffset, lngOffset]) => {
        heatPoints.push([
          system.lat + latOffset,
          system.lng + lngOffset,
          intensity * 0.2
        ]);
      });
    }
  });
  
  return heatPoints;
}

// Calculate contamination intensity based on violations and risk (enhanced for visibility)
function calculateIntensity(system: SystemMarkerData): number {
  let baseIntensity = 0.3; // Increased minimum intensity for better visibility
  
  // Risk-based intensity with enhanced values
  switch (system.risk) {
    case 'CRITICAL':
      baseIntensity = 1.0;
      break;
    case 'HIGH':
      baseIntensity = 0.85; // Increased from 0.75
      break;
    case 'MEDIUM':
      baseIntensity = 0.65; // Increased from 0.5
      break;
    case 'LOW':
      baseIntensity = 0.45; // Increased from 0.25
      break;
    default:
      baseIntensity = 0.3;  // Increased from 0.1
  }
  
  // Population weighting (larger systems have broader impact)
  const populationFactor = Math.min(system.population / 3500000, 1.8); // Enhanced factor
  
  // Violation count boost
  const violationBoost = Math.min(system.violations * 0.15, 0.4); // Enhanced boost
  
  return Math.min(baseIntensity * populationFactor + violationBoost, 1.0);
}

// Get regional radius based on population served
function getRegionalRadius(population: number): number {
  if (population > 3000000) return 0.8; // Major metropolitan areas
  if (population > 2000000) return 0.6;
  if (population > 1000000) return 0.4;
  if (population > 500000) return 0.2;
  return 0.1;
}

export default HeatMapLayer;