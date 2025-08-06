#!/usr/bin/env python3
"""
EPA Natural Language Compliance System - FastAPI Backend
Natural language interface for EPA compliance analysis
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from serpapi import GoogleSearch

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import our existing EPA agents
import sys
sys.path.append('..')
from intelligent_agentic_system import IntelligentAgenticSystem, IntelligentAgent, RealEPADataSource, RealViolationData

# Real EPA Water Systems Database (with real violation data available)
AVAILABLE_EPA_SYSTEMS = {
    "OH7700001": {
        "name": "Clinton Machine PWS",
        "description": "Small workplace water system in Ohio",
        "population": 76,
        "type": "NTNCWS",
        "has_real_violations": True,
        "fallback_csv": "demo/springfield_lab_results.csv"
    },
    "OH1801212": {
        "name": "Cleveland Public Water System", 
        "description": "Major municipal system serving Cleveland, OH",
        "population": 1308955,
        "type": "CWS",
        "has_real_violations": True,
        "fallback_csv": None
    },
    "FL4130871": {
        "name": "Miami-Dade Water and Sewer Authority",
        "description": "Major regional utility serving Miami-Dade County",
        "population": 2300000,
        "type": "CWS", 
        "has_real_violations": True,
        "fallback_csv": None
    },
    "CA3710020": {
        "name": "San Diego, City of",
        "description": "Large municipal water utility",
        "population": 1385379,
        "type": "CWS",
        "has_real_violations": True,
        "fallback_csv": None
    },
    "TX1010013": {
        "name": "City of Houston",
        "description": "Major municipal water system",
        "population": 2202531,
        "type": "CWS",
        "has_real_violations": True,
        "fallback_csv": None
    },
    "CA1910067": {
        "name": "Los Angeles Department of Water and Power",
        "description": "Mega-scale municipal utility",
        "population": 3856043,
        "type": "CWS",
        "has_real_violations": True,
        "fallback_csv": None
    }
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EPA Natural Language Compliance System",
    description="AI-powered EPA compliance analysis with natural language interface",
    version="1.0.0"
)

# Debug environment variable loading
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_RAW.split(",")]

# Log the CORS configuration for debugging
logger.info(f"🌐 CORS Configuration:")
logger.info(f"   Raw ALLOWED_ORIGINS env var: '{ALLOWED_ORIGINS_RAW}'")
logger.info(f"   Parsed ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
logger.info(f"   Environment variables available: {list(os.environ.keys())}")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class IntentResponse(BaseModel):
    intent: str
    parameters: Dict[str, Any]
    pwsid: Optional[str] = None
    location: Optional[str] = None
    contaminant: Optional[str] = None

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send message to all connected clients"""
        if self.active_connections:
            message_str = json.dumps(message)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message_str)
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for conn in disconnected:
                self.disconnect(conn)

manager = ConnectionManager()

class RealViolationDataLoader:
    """Load real EPA violation data with fallback to mock data"""
    
    def __init__(self):
        # Try multiple possible locations for the violations file
        possible_paths = [
            "real_epa_violations_20250731_144819.json",  # Mounted in container
            "../real_epa_violations_20250731_144819.json",  # Parent directory
            "/app/real_epa_violations_20250731_144819.json"  # Absolute path in container
        ]
        
        self.real_violations_file = None
        for path in possible_paths:
            if os.path.exists(path):
                self.real_violations_file = path
                break
        
        self.real_violations_cache = None
        self._load_real_violations()
    
    def _load_real_violations(self):
        """Load real EPA violations with error handling"""
        try:
            if self.real_violations_file and os.path.exists(self.real_violations_file):
                with open(self.real_violations_file, 'r') as f:
                    self.real_violations_cache = json.load(f)
                logger.info(f"✅ Loaded real EPA violations for {len(self.real_violations_cache)} systems from {self.real_violations_file}")
            else:
                logger.warning("⚠️ Real violations file not found - using fallback data only")
                self.real_violations_cache = {}
        except Exception as e:
            logger.error(f"❌ Error loading real violations: {e}")
            self.real_violations_cache = {}
    
    def get_violations_for_system(self, pwsid: str) -> List[Dict[str, Any]]:
        """Get violations for a system with fallback"""
        
        # Try real violations first
        if self.real_violations_cache and pwsid in self.real_violations_cache:
            real_violations = self.real_violations_cache[pwsid].get("sdwis_violations", [])
            if real_violations:
                logger.info(f"📊 Using {len(real_violations)} real EPA violations for {pwsid}")
                return self._convert_real_violations(real_violations, pwsid)
        
        # Fallback to mock data for OH7700001
        if pwsid == "OH7700001":
            logger.info(f"📄 Using fallback CSV data for {pwsid}")
            violation_data = RealViolationData()
            lab_data = violation_data.load_lab_results()
            return violation_data.analyze_violations(lab_data)
        
        # No data available
        logger.warning(f"⚠️ No violation data available for {pwsid}")
        return []
    
    def _convert_real_violations(self, real_violations: List[Dict], pwsid: str) -> List[Dict[str, Any]]:
        """Convert real EPA violations to our format"""
        
        converted = []
        
        for violation in real_violations[:10]:  # Limit for demo
            # Extract key fields from real EPA data
            viol_code = violation.get("violation_code", "Unknown")
            contaminant_code = violation.get("contaminant_code", "Unknown")
            compl_date = violation.get("compl_per_begin_date", "Unknown")
            
            # Map EPA contaminant codes to readable names
            contaminant_name = self._map_contaminant_code(contaminant_code)
            
            # Create standardized violation record
            converted_violation = {
                "parameter": contaminant_name,
                "result": "EPA Violation Detected",
                "mcl": "See EPA Standards",
                "violation_type": f"EPA Violation Code {viol_code}",
                "tier": self._determine_tier(contaminant_code, viol_code),
                "severity": self._determine_severity(contaminant_code, viol_code),
                "sample_location": "Multiple Locations", 
                "health_risk": f"{contaminant_name} regulatory violation",
                "violation_date": compl_date,
                "epa_violation_code": viol_code,
                "epa_contaminant_code": contaminant_code,
                "data_source": "Real EPA SDWIS"
            }
            
            converted.append(converted_violation)
        
        return converted
    
    def _map_contaminant_code(self, code: str) -> str:
        """Map EPA contaminant codes to readable names"""
        code_mapping = {
            "PB90": "Lead",
            "0300": "Chlorine", 
            "0800": "Total Trihalomethanes",
            "1040": "Nitrate",
            "2950": "Copper",
            "2456": "Arsenic",
            "5000": "Total Coliform",
            "0700": "Benzene",
            "3100": "Radium",
            "8000": "Turbidity"
        }
        return code_mapping.get(code, f"Contaminant {code}")
    
    def _determine_tier(self, contaminant_code: str, violation_code: str) -> str:
        """Determine notification tier based on contaminant"""
        # Acute violations (Tier 1)
        if contaminant_code in ["5000", "1040"]:  # Coliform, Nitrate
            return "Tier 1"
        # Most violations are Tier 2
        return "Tier 2"
    
    def _determine_severity(self, contaminant_code: str, violation_code: str) -> str:
        """Determine severity based on contaminant"""
        critical_contaminants = ["PB90", "5000", "1040", "2456"]  # Lead, Coliform, Nitrate, Arsenic
        if contaminant_code in critical_contaminants:
            return "CRITICAL"
        return "HIGH"

# Initialize real violation loader
real_violation_loader = RealViolationDataLoader()

class RemediationSpecialist:
    """Enhanced remediation specialist with real-time EPA guidance search"""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERP_API_KEY")
        if not self.serpapi_key:
            raise ValueError("SERP_API_KEY is required for remediation specialist")
            
    async def get_latest_treatment_guidance(self, contaminant: str, violation_type: str) -> Dict[str, Any]:
        """Get current EPA treatment guidance using Google search"""
        
        logger.info(f"🔍 Searching for latest {contaminant} remediation guidance...")
        
        search_queries = [
            f"EPA {contaminant} drinking water treatment technology guidance 2024",
            f"EPA {contaminant} remediation best practices",
            f"EPA drinking water {violation_type} corrective action"
        ]
        
        all_results = []
        
        for query in search_queries:
            logger.info(f"   📡 Query: {query}")
            
            params = {
                "engine": "google",
                "q": query,
                "api_key": self.serpapi_key,
                "num": 5,
                "gl": "us",
                "hl": "en"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "organic_results" in results:
                for result in results["organic_results"]:
                    if "epa.gov" in result.get("link", ""):  # Only EPA sources
                        all_results.append({
                            "title": result.get("title", ""),
                            "link": result.get("link", ""),
                            "snippet": result.get("snippet", "")
                        })
            
            await asyncio.sleep(0.5)  # Rate limiting
        
        logger.info(f"✅ Found {len(all_results)} EPA guidance documents")
        
        return {
            "search_timestamp": datetime.now().isoformat(),
            "epa_guidance": all_results[:10],  # Top 10 EPA results
            "contaminant": contaminant,
            "violation_type": violation_type
        }

# Initialize remediation specialist
remediation_specialist = RemediationSpecialist()

class NaturalLanguageProcessor:
    """Process natural language questions about EPA compliance"""
    
    def __init__(self):
        self.intent_agent = IntelligentAgent("Intent Parser")
    
    async def parse_intent(self, question: str) -> IntentResponse:
        """Parse user question to extract intent and parameters"""
        
        # Create intent parsing prompt
        intent_prompt = f"""
You are an EPA compliance question parser. Analyze this user question and extract:

QUESTION: "{question}"

Your task:
1. Determine the INTENT (what does the user want?)
2. Extract PARAMETERS (PWSID, location, contaminant, etc.)
3. Respond in JSON format

Valid intents:
- "violation_analysis": User wants to know about violations
- "system_lookup": User wants info about a water system
- "notification_requirements": User wants public notification info
- "compliance_status": User wants overall compliance status
- "general_info": General EPA information

Respond in this JSON format:
{{
    "intent": "violation_analysis",
    "parameters": {{
        "pwsid": "OH7700001",
        "location": "Springfield",
        "contaminant": "lead"
    }},
    "pwsid": "OH7700001",
    "location": "Springfield", 
    "contaminant": "lead"
}}

Extract any PWSID (format like OH7700001), location names, contaminant names (lead, copper, E.coli, PFOA, etc).
"""
        
        try:
            # Use our intelligent agent to parse intent
            thinking_result = await self.intent_agent.think_about(
                "Parse this EPA compliance question for intent and parameters",
                {"question": question, "context": "natural_language_processing"}
            )
            
            # Extract structured response from agent thinking
            if "thinking_process" in thinking_result:
                thinking_text = thinking_result["thinking_process"]
                
                # Try to extract JSON from the response
                json_match = re.search(r'\{.*\}', thinking_text, re.DOTALL)
                if json_match:
                    try:
                        parsed_json = json.loads(json_match.group())
                        return IntentResponse(**parsed_json)
                    except:
                        pass
            
            # Fallback: simple keyword matching
            return self._simple_intent_parsing(question)
            
        except Exception as e:
            logger.error(f"Intent parsing error: {e}")
            return self._simple_intent_parsing(question)
    
    def _simple_intent_parsing(self, question: str) -> IntentResponse:
        """Fallback simple intent parsing using keywords"""
        
        question_lower = question.lower()
        
        # Extract PWSID if present
        pwsid_match = re.search(r'[A-Z]{2}\d{7}', question.upper())
        pwsid = pwsid_match.group() if pwsid_match else None
        
        # Map city/system names to PWSIDs
        if not pwsid:
            system_keywords = {
                'cleveland': 'OH1801212',
                'miami': 'FL4130871', 
                'dade': 'FL4130871',
                'san diego': 'CA3710020',
                'houston': 'TX1010013',
                'los angeles': 'CA1910067',
                'ladwp': 'CA1910067',
                'clinton': 'OH7700001',
                'machine': 'OH7700001',
                'springfield': 'OH7700001'
            }
            
            for keyword, system_pwsid in system_keywords.items():
                if keyword in question_lower:
                    pwsid = system_pwsid
                    break
            
            # Default to Clinton Machine if no match
            if not pwsid:
                pwsid = "OH7700001"
        
        # Determine intent based on keywords
        if any(word in question_lower for word in ['violation', 'contamination', 'exceed', 'mcl']):
            intent = "violation_analysis"
        elif any(word in question_lower for word in ['notification', 'notice', 'public', 'alert']):
            intent = "notification_requirements"
        elif any(word in question_lower for word in ['system', 'water', 'info', 'about']):
            intent = "system_lookup"
        elif any(word in question_lower for word in ['compliance', 'status', 'compliant']):
            intent = "compliance_status"
        else:
            intent = "general_info"
        
        # Extract contaminant
        contaminant = None
        contaminants = ['lead', 'copper', 'e.coli', 'ecoli', 'pfoa', 'pfas', 'nitrate', 'chlorine']
        for cont in contaminants:
            if cont in question_lower:
                contaminant = cont
                break
        
        return IntentResponse(
            intent=intent,
            parameters={"pwsid": pwsid, "contaminant": contaminant},
            pwsid=pwsid,
            contaminant=contaminant
        )

# Initialize components
nlp_processor = NaturalLanguageProcessor()
epa_system = IntelligentAgenticSystem()

@app.get("/")
async def root():
    return {"message": "EPA Natural Language Compliance System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/systems")
async def list_available_systems():
    """List available EPA water systems for analysis"""
    
    systems_with_status = {}
    
    for pwsid, info in AVAILABLE_EPA_SYSTEMS.items():
        # Check if real violation data is available
        violations_available = real_violation_loader.real_violations_cache and pwsid in real_violation_loader.real_violations_cache
        violation_count = 0
        
        if violations_available:
            violation_count = len(real_violation_loader.real_violations_cache[pwsid].get("sdwis_violations", []))
        
        systems_with_status[pwsid] = {
            **info,
            "violations_available": violations_available,
            "violation_count": violation_count,
            "data_source": "Real EPA SDWIS" if violations_available else "Mock/Fallback"
        }
    
    return {
        "available_systems": systems_with_status,
        "total_systems": len(systems_with_status),
        "systems_with_real_data": sum(1 for s in systems_with_status.values() if s["violations_available"])
    }

@app.post("/parse-intent")
async def parse_intent(request: QuestionRequest):
    """Parse natural language question to extract intent"""
    
    try:
        intent_result = await nlp_processor.parse_intent(request.question)
        return intent_result
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Intent parsing failed: {str(e)}")

@app.post("/analyze")
async def analyze_question(request: QuestionRequest):
    """Analyze EPA compliance question using intelligent agents"""
    
    try:
        # Broadcast start of analysis
        await manager.broadcast({
            "type": "analysis_start",
            "question": request.question,
            "timestamp": datetime.now().isoformat()
        })
        
        # Parse intent
        await manager.broadcast({
            "type": "status",
            "message": "🧠 Parsing your question...",
            "stage": "intent_parsing"
        })
        
        intent_result = await nlp_processor.parse_intent(request.question)
        
        await manager.broadcast({
            "type": "intent_parsed",
            "intent": intent_result.intent,
            "parameters": intent_result.parameters
        })
        
        # Use default PWSID if none extracted
        pwsid = intent_result.pwsid or "OH7700001"
        
        # Run intelligent agentic analysis
        await manager.broadcast({
            "type": "status", 
            "message": f"🚀 Starting EPA agent analysis for {pwsid}...",
            "stage": "agent_analysis"
        })
        
        # Create a custom agentic system that broadcasts updates
        results = await run_analysis_with_updates(pwsid, request.question, intent_result)
        
        # Generate natural language response
        natural_response = generate_natural_response(results, request.question, intent_result)
        
        await manager.broadcast({
            "type": "analysis_complete",
            "results": results,
            "natural_response": natural_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "question": request.question,
            "intent": intent_result,
            "results": results,
            "natural_response": natural_response
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        await manager.broadcast({
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        })
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def run_analysis_with_updates(pwsid: str, question: str, intent: IntentResponse) -> Dict[str, Any]:
    """Run EPA analysis with real-time WebSocket updates"""
    
    try:
        # Step 1: EPA Data
        await manager.broadcast({
            "type": "agent_update",
            "agent": "epa_data",
            "status": "running",
            "message": f"🌐 Fetching EPA data for {pwsid}..."
        })
        
        epa_data = epa_system.epa_data_source.get_water_system_info(pwsid)
        
        await manager.broadcast({
            "type": "agent_update", 
            "agent": "epa_data",
            "status": "complete",
            "message": f"✅ Found: {epa_data.get('pws_name', 'Unknown System')}"
        })
        
        # Step 2: Violation Data
        await manager.broadcast({
            "type": "agent_update",
            "agent": "violation_data",
            "status": "running", 
            "message": "📊 Loading violation data..."
        })
        
        # Try real violations first, fallback to CSV for OH7700001
        violations = real_violation_loader.get_violations_for_system(pwsid)
        lab_data = []  # Real violations don't need lab_data
        
        await manager.broadcast({
            "type": "agent_update",
            "agent": "violation_data", 
            "status": "complete",
            "message": f"🚨 Found {len(violations)} violations"
        })
        
        # Combine data for agents
        real_data = {
            "epa_system_info": epa_data,
            "violations": violations,
            "lab_data": lab_data
        }
        
        # Step 3: Agent Analysis
        agent_results = {}
        
        for agent_name, agent_display in [
            ("data-validator", "Data Validator"),
            ("violation-analyst", "Violation Analyst"),
            ("notification-specialist", "Notification Specialist"),
            ("remediation-specialist", "Remediation Specialist")
        ]:
            await manager.broadcast({
                "type": "agent_update",
                "agent": agent_name,
                "status": "thinking",
                "message": f"🤔 {agent_display} analyzing...",
                "thinking_stream": f"Starting analysis of {len(violations)} violations for {epa_data.get('pws_name', 'water system')}..."
            })
            
            # Create specialized prompt based on intent
            situation = create_specialized_prompt(question, intent, agent_name, epa_data, violations)
            
            # Send thinking progress update
            await manager.broadcast({
                "type": "agent_update", 
                "agent": agent_name,
                "status": "thinking",
                "message": f"🧠 {agent_display} reasoning about EPA compliance...",
                "thinking_stream": f"Processing {len(violations)} violations for {epa_data.get('pws_name', 'water system')}..."
            })
            
            # Special handling for Remediation Specialist with SerpAPI
            if agent_name == "remediation-specialist" and violations:
                # Get primary contaminant for search
                primary_contaminant = violations[0].get('parameter', 'Unknown')
                violation_type = violations[0].get('violation_type', 'Unknown')
                
                # Update status to show SerpAPI search
                await manager.broadcast({
                    "type": "agent_update",
                    "agent": agent_name,
                    "status": "thinking",
                    "message": f"🔍 Searching for latest EPA {primary_contaminant} guidance...",
                    "thinking_stream": f"Using SerpAPI to find current EPA treatment technologies for {primary_contaminant}..."
                })
                
                try:
                    # Get latest EPA guidance using SerpAPI
                    guidance = await remediation_specialist.get_latest_treatment_guidance(
                        primary_contaminant, violation_type
                    )
                    
                    # Add guidance to real_data for the agent
                    real_data["latest_epa_guidance"] = guidance
                    
                    # Update status with search results
                    guidance_count = len(guidance.get("epa_guidance", []))
                    await manager.broadcast({
                        "type": "agent_update",
                        "agent": agent_name,
                        "status": "thinking",
                        "message": f"✅ Found {guidance_count} EPA guidance documents",
                        "thinking_stream": f"Analyzing latest EPA guidance for {primary_contaminant} remediation..."
                    })
                    
                    # Log search results for debugging
                    logger.info(f"🔍 SerpAPI Results for {primary_contaminant}:")
                    for i, result in enumerate(guidance.get("epa_guidance", [])[:5]):
                        logger.info(f"   📄 {i+1}. {result.get('title', 'No title')}")
                        logger.info(f"   🔗    {result.get('link', 'No link')}")
                    
                except Exception as e:
                    logger.error(f"❌ SerpAPI search failed: {e}")
                    real_data["latest_epa_guidance"] = {"error": str(e), "epa_guidance": []}
                    
                    await manager.broadcast({
                        "type": "agent_update",
                        "agent": agent_name,
                        "status": "thinking",
                        "message": f"⚠️ SerpAPI search failed, using baseline knowledge",
                        "thinking_stream": f"Proceeding with standard remediation analysis..."
                    })
            
            thinking_result = await epa_system.agents[agent_name].think_about(situation, real_data)
            agent_results[agent_name.replace("-", "_")] = thinking_result
            
            # Debug logging to see what we got from the agent
            logger.info(f"🧠 {agent_name} thinking result keys: {list(thinking_result.keys())}")
            logger.info(f"🧠 {agent_name} full thinking result: {thinking_result}")
            
            if "thinking_process" in thinking_result:
                thinking_preview_log = thinking_result["thinking_process"][:300] + "..." if len(thinking_result["thinking_process"]) > 300 else thinking_result["thinking_process"]
                logger.info(f"🧠 {agent_name} thinking preview: {thinking_preview_log}")
            else:
                logger.warning(f"⚠️ {agent_name} has no thinking_process field")
            
            # Extract actual thinking from AI response - handle JSON format
            thinking_text = "Agent completed analysis"
            
            # The AI often returns thinking in JSON format, let's extract it properly
            raw_thinking = thinking_result.get("thinking_process", "")
            
            if raw_thinking:
                # Check if it's JSON wrapped in markdown
                if "```json" in raw_thinking:
                    try:
                        # Extract JSON from markdown code block - use DOTALL and non-greedy match
                        import re
                        json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_thinking, re.DOTALL)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            thinking_text = json_data.get("thinking_process", json_data.get("assessment", raw_thinking))
                            logger.info(f"✅ Successfully parsed JSON thinking for {agent_name}")
                        else:
                            thinking_text = raw_thinking
                            logger.warning(f"⚠️ Could not extract JSON from markdown for {agent_name}")
                    except Exception as e:
                        thinking_text = raw_thinking
                        logger.error(f"❌ JSON parsing error for {agent_name}: {e}")
                # Check if it starts with JSON directly
                elif raw_thinking.startswith("{"):
                    try:
                        json_data = json.loads(raw_thinking)
                        thinking_text = json_data.get("thinking_process", json_data.get("assessment", raw_thinking))
                        logger.info(f"✅ Successfully parsed direct JSON for {agent_name}")
                    except Exception as e:
                        thinking_text = raw_thinking
                        logger.error(f"❌ Direct JSON parsing error for {agent_name}: {e}")
                else:
                    # Use the raw thinking as-is
                    thinking_text = raw_thinking
            
            # Create preview (limit to reasonable length)
            if len(thinking_text) > 400:
                thinking_preview = thinking_text[:400] + "..."
            else:
                thinking_preview = thinking_text
            
            # Extract decisions and actions from JSON if present
            decisions = thinking_result.get("decisions", [])
            next_actions = thinking_result.get("next_actions", [])
            
            # For Remediation Specialist, add SerpAPI results to the output
            if agent_name == "remediation-specialist" and "latest_epa_guidance" in real_data:
                guidance_data = real_data["latest_epa_guidance"]
                epa_sources = guidance_data.get("epa_guidance", [])
                
                if epa_sources:
                    # Add EPA sources to next_actions for display
                    next_actions.extend([
                        f"Reference: {source.get('title', 'EPA Guidance')} - {source.get('link', '')}"
                        for source in epa_sources[:3]  # Show top 3 sources
                    ])
            
            # If thinking was in JSON format, try to extract from there too
            if raw_thinking and ("```json" in raw_thinking or raw_thinking.startswith("{")):
                try:
                    if "```json" in raw_thinking:
                        json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_thinking, re.DOTALL)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                    else:
                        json_data = json.loads(raw_thinking)
                    
                    decisions = json_data.get("decisions", decisions)
                    next_actions = json_data.get("next_actions", next_actions)
                    
                    # Also update risk assessment and confidence from the detailed JSON
                    if "risk_assessment" in json_data:
                        thinking_result["risk_assessment"] = json_data["risk_assessment"]
                    if "confidence" in json_data:
                        thinking_result["confidence"] = json_data["confidence"]
                        
                    logger.info(f"✅ Extracted decisions and actions for {agent_name}: {len(decisions)} decisions, {len(next_actions)} actions")
                    
                except Exception as e:
                    logger.error(f"❌ Error extracting decisions/actions for {agent_name}: {e}")
                    pass  # Keep original values if parsing fails
            
            await manager.broadcast({
                "type": "agent_update",
                "agent": agent_name,
                "status": "complete",
                "message": f"✅ {agent_display} complete",
                "risk_assessment": thinking_result.get("risk_assessment", "unknown"),
                "confidence": thinking_result.get("confidence", 0.0),
                "thinking_preview": thinking_preview,
                "full_thinking": thinking_text,
                "decisions": decisions,
                "next_actions": next_actions
            })
        
        return {
            "epa_data": epa_data,
            "violations": violations,
            "agent_intelligence": agent_results,
            "summary": create_summary(epa_data, violations, agent_results)
        }
        
    except Exception as e:
        logger.error(f"Analysis with updates failed: {e}")
        await manager.broadcast({
            "type": "error",
            "message": f"Analysis failed: {str(e)}"
        })
        raise

def create_specialized_prompt(question: str, intent: IntentResponse, agent_name: str, epa_data: Dict, violations: List[Dict]) -> str:
    """Create specialized prompts based on user question and agent role"""
    
    system_name = epa_data.get('pws_name', 'Unknown System')
    violation_count = len(violations)
    
    base_context = f"User asked: '{question}'. System: {system_name}, {violation_count} violations found."
    
    if agent_name == "data-validator":
        return f"{base_context} Focus on data quality, EPA API validation, and system operational status."
    elif agent_name == "violation-analyst":
        return f"{base_context} Focus on EPA regulatory violations, MCL exceedances, and compliance analysis."
    elif agent_name == "notification-specialist":
        return f"{base_context} Focus on public notification requirements, Tier classifications, and health communications."
    elif agent_name == "remediation-specialist":
        guidance_context = ""
        if "latest_epa_guidance" in violations and len(violations) > 0:
            guidance_count = len(violations[0].get("latest_epa_guidance", {}).get("epa_guidance", []))
            if guidance_count > 0:
                guidance_context = f" I have access to {guidance_count} current EPA guidance documents from 2024 searches."
        return f"{base_context} Focus on technical solutions, treatment technologies, corrective actions, and implementation timelines for addressing violations.{guidance_context}"
    
    return base_context

def create_summary(epa_data: Dict, violations: List[Dict], agent_results: Dict) -> Dict[str, Any]:
    """Create direct EPA Compliance Intelligence Briefing from ACTUAL agent outputs"""
    
    # Parse actual agent results (these come from the real thinking JSON)
    agents = {
        'data_validator': agent_results.get('data_validator', {}),
        'violation_analyst': agent_results.get('violation_analyst', {}),
        'notification_specialist': agent_results.get('notification_specialist', {}),
        'remediation_specialist': agent_results.get('remediation_specialist', {})
    }
    
    def extract_from_json_thinking(agent_data, field_name):
        """Extract specific field from agent's actual thinking JSON"""
        thinking = agent_data.get('thinking_process', '')
        
        # Try to extract from JSON in thinking
        if '```json' in thinking:
            try:
                import json
                import re
                json_match = re.search(r'```json\s*(\{.*\})\s*```', thinking, re.DOTALL)
                if json_match:
                    json_data = json.loads(json_match.group(1))
                    return json_data.get(field_name, None)
            except Exception as e:
                logger.warning(f"Failed to parse JSON thinking for {field_name}: {e}")
                pass
        
        # Fallback to direct field
        return agent_data.get(field_name, None)
    
    # Extract REAL decisions and actions from agent JSON thinking
    all_key_findings = []
    all_immediate_actions = []
    agent_assessments = []
    epa_resources = []
    
    agent_names = {
        'data_validator': '🔍 Data Validator',
        'violation_analyst': '🚨 Violation Analyst',
        'notification_specialist': '📢 Notification Specialist', 
        'remediation_specialist': '🔧 Remediation Specialist'
    }
    
    # Extract real data from each agent
    for agent_key, display_name in agent_names.items():
        if agent_key in agents and agents[agent_key]:
            agent_data = agents[agent_key]
            
            # Extract risk and confidence from actual JSON
            risk = extract_from_json_thinking(agent_data, 'risk_assessment') or 'unknown'
            confidence = extract_from_json_thinking(agent_data, 'confidence') or 0
            
            # Extract real decisions from JSON
            decisions = extract_from_json_thinking(agent_data, 'decisions') or []
            actions = extract_from_json_thinking(agent_data, 'next_actions') or []
            
            # Store agent assessment
            agent_assessments.append({
                "agent": display_name,
                "risk": risk.upper() if isinstance(risk, str) else 'UNKNOWN',
                "confidence": f"{round(confidence * 100)}%" if confidence else "0%",
                "decisions": decisions,
                "actions": actions
            })
            
            # Add to aggregated findings
            for decision in decisions[:2]:  # Top 2 decisions per agent
                all_key_findings.append(f"{display_name}: {decision}")
            
            for action in actions[:2]:  # Top 2 actions per agent
                all_immediate_actions.append(action)
            
            # Check for EPA resources (from SerpAPI)
            if agent_key == 'remediation_specialist':
                # Look for EPA references in actions
                for action in actions:
                    if 'Reference:' in action and 'epa.gov' in action:
                        epa_resources.append(action.replace('Reference: ', ''))
    
    # Calculate overall risk (highest priority)
    risk_priority = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
    risks = [a['risk'].lower() for a in agent_assessments if a['risk'].lower() != 'unknown']
    overall_risk = max(risks, key=lambda x: risk_priority.get(x, 0), default='unknown') if risks else 'unknown'
    
    # Calculate average confidence
    confidences = [float(a['confidence'].replace('%', '')) for a in agent_assessments if a['confidence'] != '0%']
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    # Analyze violations
    tier_1_violations = len([v for v in violations if v.get('tier') == 'Tier 1'])
    critical_violations = len([v for v in violations if v.get('severity') == 'CRITICAL'])
    population = epa_data.get('population_served_count', 0)
    
    # Detect SerpAPI usage properly
    serpapi_used = len(epa_resources) > 0
    
    return {
        "briefing_type": "EPA Compliance Intelligence Report",
        "executive_summary": {
            "overall_risk": overall_risk.upper(),
            "population_affected": f"{population:,} people",
            "confidence_level": f"{round(avg_confidence)}%",
            "immediate_action_required": tier_1_violations > 0 or overall_risk == 'critical',
            "violations_summary": f"{len(violations)} total violations ({tier_1_violations} Tier 1, {critical_violations} Critical)"
        },
        
        "system_information": {
            "name": epa_data.get('pws_name', 'Unknown System'),
            "pwsid": epa_data.get('pwsid', 'Unknown'),
            "location": f"{epa_data.get('city_name', 'Unknown')}, {epa_data.get('state_code', 'Unknown')}",
            "epa_region": epa_data.get('epa_region', 'Unknown'),
            "water_source": epa_data.get('gw_sw_code', 'Unknown'),
            "system_type": epa_data.get('pws_type_code', 'Unknown'),
            "service_connections": epa_data.get('service_connections_count', 'Unknown')
        },
        
        "key_findings": all_key_findings[:10],  # Top 10 findings from actual agent analysis
        
        "immediate_actions": all_immediate_actions[:10],  # Top 10 actions from actual agents
        
        "agent_assessments": agent_assessments,  # Individual agent risk assessments
        
        "epa_resources": {
            "serpapi_enhanced": serpapi_used,
            "guidance_documents": epa_resources,
            "total_resources": len(epa_resources)
        },
        
        "violation_details": {
            "by_tier": {
                "tier_1": len([v for v in violations if v.get('tier') == 'Tier 1']),
                "tier_2": len([v for v in violations if v.get('tier') == 'Tier 2'])
            },
            "by_severity": {
                "critical": critical_violations,
                "high": len([v for v in violations if v.get('severity') == 'HIGH'])
            },
            "parameters_affected": list(set(v.get('parameter') for v in violations if v.get('parameter')))
        },
        
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "agents_analyzed": len(agent_assessments),
            "real_time_enhanced": serpapi_used,
            "data_sources": ["EPA SDWIS API", "EPA ECHO Database"] + (["SerpAPI Google Search"] if serpapi_used else [])
        }
    }

def generate_natural_response(results: Dict[str, Any], question: str, intent: IntentResponse) -> str:
    """Generate natural language response based on analysis results"""
    
    summary = results.get('summary', {})
    
    # Handle new summary structure
    if 'executive_summary' in summary:
        # New structure
        system_name = summary.get('system_information', {}).get('name', 'Unknown System')
        overall_risk = summary.get('executive_summary', {}).get('overall_risk', 'UNKNOWN')
        population_str = summary.get('executive_summary', {}).get('population_affected', '0 people')
        population = int(population_str.replace(',', '').replace(' people', '')) if population_str != '0 people' else 0
        violations_summary = summary.get('executive_summary', {}).get('violations_summary', '0 violations')
        immediate_action = summary.get('executive_summary', {}).get('immediate_action_required', False)
        
        # Extract violation counts from violations_summary string
        import re
        total_match = re.search(r'(\d+) total violations', violations_summary)
        tier1_match = re.search(r'(\d+) Tier 1', violations_summary)
        critical_match = re.search(r'(\d+) Critical', violations_summary)
        
        total_violations = int(total_match.group(1)) if total_match else 0
        tier1_violations = int(tier1_match.group(1)) if tier1_match else 0
        critical_violations = int(critical_match.group(1)) if critical_match else 0
        
        # Get parameters from violation_details
        parameters = summary.get('violation_details', {}).get('parameters_affected', [])
        
    else:
        # Legacy structure fallback
        water_system = summary.get('water_system', {})
        violations = summary.get('violations', {})
        
        system_name = water_system.get('name', 'Unknown System')
        total_violations = violations.get('total', 0)
        critical_violations = violations.get('critical', 0)
        population = water_system.get('population', 0)
        tier1_violations = 0
        overall_risk = 'UNKNOWN'
        immediate_action = False
        parameters = violations.get('parameters', [])
    
    # Generate response based on actual data
    if intent.intent == "violation_analysis":
        if total_violations == 0:
            return f"Good news! {system_name} shows no EPA violations in our analysis."
        else:
            # Build response based on severity
            if overall_risk == 'CRITICAL' or immediate_action:
                response = f"🚨 CRITICAL ALERT: {system_name} has {total_violations} EPA violations affecting {population:,} people, requiring immediate action"
            elif overall_risk == 'HIGH':
                response = f"⚠️ HIGH PRIORITY: {system_name} has {total_violations} EPA violations affecting {population:,} people"
            else:
                response = f"{system_name} has {total_violations} EPA violations affecting {population:,} people"
            
            # Add severity details
            severity_details = []
            if tier1_violations > 0:
                severity_details.append(f"{tier1_violations} Tier 1 emergency violation{'s' if tier1_violations > 1 else ''}")
            if critical_violations > 0:
                severity_details.append(f"{critical_violations} critical violation{'s' if critical_violations > 1 else ''}")
            
            if severity_details:
                response += f", including {' and '.join(severity_details)}"
            
            # Add parameters if available
            if parameters:
                response += f". Contaminated parameters: {', '.join(parameters[:3])}"  # Show top 3
                if len(parameters) > 3:
                    response += f" and {len(parameters) - 3} others"
            
            response += "."
            return response
    
    elif intent.intent == "system_lookup":
        pwsid = summary.get('system_information', {}).get('pwsid') if 'executive_summary' in summary else water_system.get('pwsid', 'Unknown')
        location = summary.get('system_information', {}).get('location') if 'executive_summary' in summary else water_system.get('location', 'Unknown')
        return f"{system_name} (PWSID: {pwsid}) serves {population:,} people in {location}."
    
    elif intent.intent == "compliance_status":
        if total_violations == 0:
            return f"{system_name} appears to be in EPA compliance with no violations detected."
        else:
            if immediate_action:
                return f"🚨 {system_name} has {total_violations} compliance violations requiring immediate regulatory action and public notification."
            else:
                return f"{system_name} has {total_violations} compliance issues that require attention, including regulatory violations that may need public notification."
    
    else:
        # General response
        if total_violations == 0:
            return f"Analysis complete for {system_name}. No EPA violations detected."
        else:
            risk_indicator = "🚨" if overall_risk == 'CRITICAL' else "⚠️" if overall_risk == 'HIGH' else "📊"
            return f"{risk_indicator} Analysis complete for {system_name}. Found {total_violations} violations affecting {population:,} people. Risk level: {overall_risk}. Our AI agents have provided detailed regulatory analysis and recommendations."

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)