import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { SYSTEM_COORDINATES, SystemMarkerData, GeographicViewProps } from '../types/geographic';
import HeatMapLayer from './HeatMapLayer';

// Custom hook to fit map bounds to show all systems
function MapBounds({ systems }: { systems: SystemMarkerData[] }) {
  const map = useMap();
  
  useEffect(() => {
    if (systems.length > 0) {
      const bounds = new LatLngBounds(
        systems.map(system => [system.lat, system.lng] as [number, number])
      );
      map.fitBounds(bounds, { padding: [20, 20] });
    }
  }, [map, systems]);
  
  return null;
}

// Map marker component for water systems
function SystemMarker({ system, onSystemClick, isSelected }: {
  system: SystemMarkerData;
  onSystemClick: (pwsid: string, systemName: string) => void;
  isSelected: boolean;
}) {
  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'critical': return '#dc2626'; // red-600
      case 'high': return '#ea580c'; // orange-600  
      case 'medium': return '#d97706'; // amber-600
      case 'low': return '#16a34a'; // green-600
      default: return '#6b7280'; // gray-500
    }
  };

  const getMarkerSize = (population: number) => {
    if (population > 3000000) return 25;
    if (population > 2000000) return 22;
    if (population > 1000000) return 18;
    if (population > 500000) return 15;
    if (population > 100000) return 12;
    return 8;
  };

  const formatPopulation = (pop: number) => {
    if (pop >= 1000000) return `${(pop / 1000000).toFixed(1)}M`;
    if (pop >= 1000) return `${(pop / 1000).toFixed(0)}K`;
    return pop.toString();
  };

  return (
    <CircleMarker
      center={[system.lat, system.lng]}
      radius={getMarkerSize(system.population)}
      pathOptions={{
        color: isSelected ? '#1d4ed8' : getRiskColor(system.risk),
        weight: isSelected ? 4 : 2,
        fillColor: getRiskColor(system.risk),
        fillOpacity: 0.7,
        opacity: 1
      }}
      eventHandlers={{
        click: () => onSystemClick(system.pwsid, system.name)
      }}
    >
      <Popup>
        <div className="min-w-64">
          <h3 className="font-bold text-lg mb-2">{system.name}</h3>
          <div className="space-y-1 text-sm">
            <div><span className="font-medium">PWSID:</span> {system.pwsid}</div>
            <div><span className="font-medium">Population:</span> {formatPopulation(system.population)} people</div>
            <div><span className="font-medium">State:</span> {system.state}</div>
            <div>
              <span className="font-medium">Risk Level:</span> 
              <span className={`ml-1 px-2 py-1 rounded text-xs font-medium ${
                system.risk === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                system.risk === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                system.risk === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                system.risk === 'LOW' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {system.risk}
              </span>
            </div>
            {system.violations > 0 && (
              <div><span className="font-medium">Violations:</span> {system.violations}</div>
            )}
            {system.violationTypes.length > 0 && (
              <div>
                <span className="font-medium">Contaminants:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {system.violationTypes.slice(0, 3).map((type, idx) => (
                    <span key={idx} className="px-1 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                      {type}
                    </span>
                  ))}
                  {system.violationTypes.length > 3 && (
                    <span className="px-1 py-0.5 bg-gray-100 text-gray-700 rounded text-xs">
                      +{system.violationTypes.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
          <button
            onClick={() => onSystemClick(system.pwsid, system.name)}
            className="mt-3 w-full bg-epa-blue text-white px-3 py-2 rounded text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            🔍 Analyze System
          </button>
        </div>
      </Popup>
    </CircleMarker>
  );
}

// Legend component
function MapLegend({ showHeatMap }: { showHeatMap: boolean }) {
  const riskLevels = [
    { level: 'CRITICAL', color: '#dc2626', description: 'Immediate action required' },
    { level: 'HIGH', color: '#ea580c', description: 'Significant violations' },
    { level: 'MEDIUM', color: '#d97706', description: 'Moderate issues' },
    { level: 'LOW', color: '#16a34a', description: 'Minor or no violations' }
  ];

  const heatMapGradient = [
    { color: '#ff0000', description: 'Critical contamination density' },
    { color: '#ff8000', description: 'High contamination density' },
    { color: '#ffff00', description: 'Moderate contamination density' },
    { color: '#00ff00', description: 'Low contamination density' }
  ];

  return (
    <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg border max-w-xs" style={{ zIndex: 10000 }}>
      <h4 className="font-semibold text-sm mb-2">🎯 Map Legend</h4>
      
      {/* Marker Legend */}
      <div className="mb-3">
        <h5 className="font-medium text-xs mb-1">Water System Markers</h5>
        <div className="space-y-1">
          {riskLevels.map((item) => (
            <div key={item.level} className="flex items-center gap-2 text-xs">
              <div 
                className="w-3 h-3 rounded-full border border-gray-300"
                style={{ backgroundColor: item.color }}
              />
              <span className="font-medium">{item.level}</span>
              <span className="text-gray-600">- {item.description}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Heat Map Legend */}
      {showHeatMap && (
        <div className="mb-2 pt-2 border-t border-gray-200">
          <h5 className="font-medium text-xs mb-1">🔥 Heat Map Density</h5>
          <div className="space-y-1">
            {heatMapGradient.map((item, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs">
                <div 
                  className="w-3 h-2 border border-gray-300 rounded-sm"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-gray-600">{item.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="pt-2 border-t border-gray-200 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <span className="text-lg">○</span>
          <span>Circle size = Population served</span>
        </div>
        {showHeatMap && (
          <div className="flex items-center gap-1 mt-1">
            <span className="text-lg">🔥</span>
            <span>Heat intensity = Risk × Population</span>
          </div>
        )}
      </div>
    </div>
  );
}

const MapVisualization: React.FC<GeographicViewProps> = ({ 
  results, 
  onSystemClick,
  selectedSystem 
}) => {
  const [systems, setSystems] = useState<SystemMarkerData[]>([]);
  const [showHeatMap, setShowHeatMap] = useState(true); // Heat map visible by default

  // Transform EPA results data into map markers
  useEffect(() => {
    const systemsData: SystemMarkerData[] = Object.values(SYSTEM_COORDINATES).map(coord => {
      // Extract data from results if available
      let violations = 0;
      let risk: SystemMarkerData['risk'] = 'UNKNOWN';
      let violationTypes: string[] = [];

      // If we have results and they match this system
      if (results && results.epa_data && results.epa_data.pwsid === coord.pwsid) {
        violations = results.violations?.length || 0;
        
        // Extract risk from summary
        if (results.summary?.executive_summary?.overall_risk) {
          risk = results.summary.executive_summary.overall_risk.toUpperCase() as SystemMarkerData['risk'];
        } else if (results.summary?.ai_assessment?.analyst_risk) {
          risk = results.summary.ai_assessment.analyst_risk.toUpperCase() as SystemMarkerData['risk'];
        }

        // Extract violation types
        if (results.violations) {
          violationTypes = [...new Set(
            results.violations.map((v: any) => v.parameter).filter(Boolean)
          )];
        }
      } else {
        // Default risk based on system (for demo purposes)
        if (coord.pwsid === 'CA1910067') risk = 'CRITICAL'; // Los Angeles
        else if (coord.pwsid === 'TX1010013') risk = 'HIGH'; // Houston  
        else if (coord.pwsid === 'FL4130871') risk = 'HIGH'; // Miami-Dade
        else if (coord.pwsid === 'OH1801212') risk = 'MEDIUM'; // Cleveland
        else if (coord.pwsid === 'CA3710020') risk = 'MEDIUM'; // San Diego
        else if (coord.pwsid === 'OH7700001') risk = 'LOW'; // Clinton Machine
      }

      return {
        ...coord,
        violations,
        risk,
        violationTypes,
        hasRealData: results?.epa_data?.pwsid === coord.pwsid
      };
    });

    setSystems(systemsData);
  }, [results]);

  return (
    <div className="space-y-4">
      {/* Map Controls - Outside of map container */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Interactive EPA contamination map with {systems.length} water systems
        </div>
        <button
          onClick={() => setShowHeatMap(!showHeatMap)}
          className={`flex items-center gap-2 px-3 py-2 rounded text-sm font-medium transition-colors border ${
            showHeatMap 
              ? 'bg-red-100 text-red-800 hover:bg-red-200 border-red-300' 
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-gray-300'
          }`}
        >
          <span className="text-base">🔥</span>
          <span>{showHeatMap ? 'Hide Heat Map' : 'Show Heat Map'}</span>
        </button>
      </div>

      {/* Map Container */}
      <div className="relative h-96 w-full rounded-lg overflow-hidden border border-gray-200">
        <MapContainer
          center={[39.8283, -98.5795]} // Geographic center of US
          zoom={4}
          style={{ height: '100%', width: '100%' }}
          zoomControl={true}
          scrollWheelZoom={true}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          <MapBounds systems={systems} />
          
          {/* Heat Map Layer */}
          <HeatMapLayer systems={systems} isVisible={showHeatMap} />
          
          {systems.map((system) => (
            <SystemMarker
              key={system.pwsid}
              system={system}
              onSystemClick={onSystemClick}
              isSelected={selectedSystem === system.pwsid}
            />
          ))}
        </MapContainer>
      </div>

      {/* Legend - Outside of map container */}
      <div className="bg-white p-3 rounded-lg shadow-lg border max-w-2xl">
        <h4 className="font-semibold text-sm mb-2">🎯 Map Legend</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Marker Legend */}
          <div>
            <h5 className="font-medium text-xs mb-2">Water System Markers</h5>
            <div className="space-y-1">
              {[
                { level: 'CRITICAL', color: '#dc2626', description: 'Immediate action' },
                { level: 'HIGH', color: '#ea580c', description: 'Significant violations' },
                { level: 'MEDIUM', color: '#d97706', description: 'Moderate issues' },
                { level: 'LOW', color: '#16a34a', description: 'Minor/no violations' }
              ].map((item) => (
                <div key={item.level} className="flex items-center gap-2 text-xs">
                  <div 
                    className="w-3 h-3 rounded-full border border-gray-300"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="font-medium">{item.level}</span>
                  <span className="text-gray-600">- {item.description}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Heat Map Legend */}
          {showHeatMap && (
            <div>
              <h5 className="font-medium text-xs mb-2">🔥 Contamination Density</h5>
              <div className="space-y-1">
                {[
                  { color: '#ff0000', description: 'Critical contamination density' },
                  { color: '#ff8000', description: 'High contamination density' },
                  { color: '#ffff00', description: 'Moderate contamination density' },
                  { color: '#00ff00', description: 'Low contamination density' }
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    <div 
                      className="w-3 h-2 border border-gray-300 rounded-sm"
                      style={{ backgroundColor: item.color }}
                    />
                    <span className="text-gray-600">{item.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="mt-3 pt-2 border-t border-gray-200 text-xs text-gray-600 flex flex-wrap gap-4">
          <div className="flex items-center gap-1">
            <span className="text-lg">○</span>
            <span>Circle size = Population served</span>
          </div>
          {showHeatMap && (
            <div className="flex items-center gap-1">
              <span className="text-lg">🔥</span>
              <span>Heat intensity = Risk × Population</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapVisualization;