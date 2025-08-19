export interface WaterSystemCoordinates {
  lat: number;
  lng: number;
  name: string;
  pwsid: string;
  population: number;
  state: string;
}

export interface SystemMarkerData extends WaterSystemCoordinates {
  violations: number;
  risk: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN';
  violationTypes: string[];
  hasRealData: boolean;
}

export interface GeographicViewProps {
  results?: any;
  onSystemClick: (pwsid: string, systemName: string) => void;
  selectedSystem?: string;
}

// Static coordinates for the 6 major EPA water systems
export const SYSTEM_COORDINATES: Record<string, WaterSystemCoordinates> = {
  "CA1910067": {
    lat: 34.0522,
    lng: -118.2437,
    name: "Los Angeles Department of Water and Power",
    pwsid: "CA1910067",
    population: 3856043,
    state: "California"
  },
  "TX1010013": {
    lat: 29.7604,
    lng: -95.3698,
    name: "City of Houston",
    pwsid: "TX1010013", 
    population: 2202531,
    state: "Texas"
  },
  "FL4130871": {
    lat: 25.7617,
    lng: -80.1918,
    name: "Miami-Dade Water and Sewer Authority",
    pwsid: "FL4130871",
    population: 2300000,
    state: "Florida"
  },
  "OH1801212": {
    lat: 41.4993,
    lng: -81.6944,
    name: "Cleveland Public Water System",
    pwsid: "OH1801212",
    population: 1308955,
    state: "Ohio"
  },
  "CA3710020": {
    lat: 32.7157,
    lng: -117.1611,
    name: "San Diego, City of",
    pwsid: "CA3710020",
    population: 1385379,
    state: "California"
  },
  "OH7700001": {
    lat: 39.4042,
    lng: -83.0389,
    name: "Clinton Machine PWS",
    pwsid: "OH7700001",
    population: 76,
    state: "Ohio"
  }
};