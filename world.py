import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class WorldState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.calendar = {
            "user_001": {
                today: [
                    {"time": "09:00-10:30", "event": "Advanced AI Lecture (Room A301)", "type": "lecture"},
                    {"time": "10:45-12:15", "event": "Machine Learning Seminar (Room B205)", "type": "lecture"},
                    {"time": "14:00-15:00", "event": "Research Group Meeting", "type": "meeting"},
                ]
            }
        }
        
        self.contacts = {
            "Sarah": {
                "availability": "Free after 16:00",
                "location": "University Town, Shenzhen",
                "preferred_venues": ["quiet", "wifi"],
                "contact_method": "wechat"
            },
            "Mark": {
                "availability": "Free 14:00-18:00",
                "location": "Nanshan District, Shenzhen",
                "preferred_venues": ["casual", "coffee"],
                "contact_method": "wechat"
            },
            "Professor Chen": {
                "availability": "By appointment only",
                "location": "SIGS Campus",
                "preferred_venues": ["formal", "quiet"],
                "contact_method": "wechat"
            }
        }
        
        self.venues = [
            {
                "name": "The Lab Coffee",
                "location": "University Town",
                "type": "cafe",
                "wifi": True,
                "avg_cost": 12,
                "quiet": True,
                "hours": "08:00-22:00"
            },
            {
                "name": "Starbucks",
                "location": "Uniwalk Mall",
                "type": "cafe",
                "wifi": True,
                "avg_cost": 25,
                "quiet": False,
                "hours": "07:00-23:00"
            },
            {
                "name": "Campus Library Study Room",
                "location": "SIGS Campus",
                "type": "study",
                "wifi": True,
                "avg_cost": 0,
                "quiet": True,
                "hours": "08:00-22:00"
            },
            {
                "name": "Meet You Tea House",
                "location": "University Town",
                "type": "cafe",
                "wifi": True,
                "avg_cost": 18,
                "quiet": True,
                "hours": "10:00-23:00"
            },
            {
                "name": "Pacific Coffee",
                "location": "Coco Park",
                "type": "cafe",
                "wifi": True,
                "avg_cost": 30,
                "quiet": False,
                "hours": "07:30-22:00"
            },
            {
                "name": "SIGS Canteen",
                "location": "SIGS Campus",
                "type": "restaurant",
                "wifi": False,
                "avg_cost": 15,
                "quiet": False,
                "hours": "11:00-14:00, 17:00-19:00"
            }
        ]
        
        self.budget = {
            "user_001": {
                "weekly_discretionary": 200,
                "remaining": 85
            }
        }
        
        self.notification_queue = []
        
        self.weather_data = {
            today: {
                9: {"rain_prob": 20, "temp": 22},
                10: {"rain_prob": 15, "temp": 24},
                11: {"rain_prob": 10, "temp": 26},
                12: {"rain_prob": 5, "temp": 27},
                13: {"rain_prob": 10, "temp": 28},
                14: {"rain_prob": 30, "temp": 27},
                15: {"rain_prob": 60, "temp": 26},
                16: {"rain_prob": 90, "temp": 25},
                17: {"rain_prob": 100, "temp": 24},
                18: {"rain_prob": 80, "temp": 23},
                19: {"rain_prob": 40, "temp": 22},
                20: {"rain_prob": 20, "temp": 21}
            }
        }
        
        self.locations = {
            "SIGS Campus": {"coords": (22.5955, 113.9765)},
            "University Town": {"coords": (22.5980, 113.9790)},
            "Uniwalk Mall": {"coords": (22.6020, 113.9850)},
            "Coco Park": {"coords": (22.5450, 114.0550)},
            "Nanshan District": {"coords": (22.5400, 113.9300)}
        }
    
    def get_calendar(self, user_id: str, date: str = None) -> Dict:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if user_id not in self.calendar:
            return {"status": "error", "message": "User not found"}
        
        if date not in self.calendar[user_id]:
            return {"status": "success", "date": date, "events": []}
        
        return {
            "status": "success",
            "date": date,
            "events": self.calendar[user_id][date]
        }
    
    def fetch_contact_info(self, name: str) -> Dict:
        if name not in self.contacts:
            return {"status": "error", "message": "Contact not found"}
        
        return {
            "status": "success",
            "name": name,
            **self.contacts[name]
        }
    
    def search_venues(self, location: str, venue_type: str, max_price: Optional[float] = None) -> Dict:
        results = []
        for venue in self.venues:
            if venue["location"] != location and location != "any":
                continue
            if venue["type"] != venue_type and venue_type != "any":
                continue
            if max_price is not None and venue["avg_cost"] > max_price:
                continue
            results.append(venue)
        
        return {
            "status": "success",
            "count": len(results),
            "venues": results
        }
    
    def get_weather(self, hour: int, date: str = None) -> Dict:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        if date not in self.weather_data:
            return {"status": "error", "message": "Weather data not available for this date"}
        
        if hour not in self.weather_data[date]:
            return {"status": "error", "message": "Weather data not available for this hour"}
        
        return {
            "status": "success",
            "date": date,
            "hour": hour,
            **self.weather_data[date][hour]
        }
    
    def calculate_travel_time(self, start: str, end: str, mode: str = "walking") -> Dict:
        if start not in self.locations or end not in self.locations:
            return {"status": "error", "message": "Location not found"}
        
        start_coords = self.locations[start]["coords"]
        end_coords = self.locations[end]["coords"]
        
        lat_diff = abs(start_coords[0] - end_coords[0])
        lon_diff = abs(start_coords[1] - end_coords[1])
        distance_km = ((lat_diff * 111) ** 2 + (lon_diff * 100) ** 2) ** 0.5
        
        time_map = {
            "walking": distance_km * 12,
            "cycling": distance_km * 4,
            "taxi": distance_km * 3 + 5,
            "metro": distance_km * 2.5 + 10
        }
        
        minutes = int(round(time_map.get(mode, distance_km * 12)))
        
        return {
            "status": "success",
            "start": start,
            "end": end,
            "mode": mode,
            "distance_km": round(distance_km, 2),
            "minutes": minutes
        }
    
    def check_finances(self, user_id: str = "user_001") -> Dict:
        if user_id not in self.budget:
            return {"status": "error", "message": "User not found"}
        
        return {
            "status": "success",
            "user_id": user_id,
            "weekly_discretionary": self.budget[user_id]["weekly_discretionary"],
            "remaining": self.budget[user_id]["remaining"]
        }
    
    def update_schedule(self, user_id: str, date: str, event_details: Dict) -> Dict:
        if user_id not in self.calendar:
            return {"status": "error", "message": "User not found"}
        
        required_fields = ["time", "event", "type"]
        for field in required_fields:
            if field not in event_details:
                return {"status": "error", "message": f"Missing required field: {field}"}
        
        if date not in self.calendar[user_id]:
            self.calendar[user_id][date] = []
        
        new_event = {
            "time": event_details["time"],
            "event": event_details["event"],
            "type": event_details["type"]
        }
        
        if "cost" in event_details:
            new_event["cost"] = event_details["cost"]
        
        # De-duplication check: if an event with same time and name exists, don't add
        is_duplicate = any(e["time"] == new_event["time"] and e["event"] == new_event["event"] 
                          for e in self.calendar[user_id][date])
        
        if is_duplicate:
            return {
                "status": "success",
                "message": "Event already exists",
                "event": new_event,
                "remaining_budget": self.budget[user_id]["remaining"]
            }

        if "cost" in event_details:
            self.budget[user_id]["remaining"] -= event_details["cost"]
        
        self.calendar[user_id][date].append(new_event)
        
        return {
            "status": "success",
            "message": "Event added successfully",
            "event": new_event,
            "remaining_budget": self.budget[user_id]["remaining"]
        }
    
    def notify_contact(self, name: str, message: str) -> Dict:
        if name not in self.contacts:
            return {"status": "error", "message": "Contact not found"}
        
        notification = {
            "timestamp": datetime.now().isoformat(),
            "to": name,
            "via": self.contacts[name]["contact_method"],
            "message": message,
            "status": "queued"
        }
        
        self.notification_queue.append(notification)
        
        return {
            "status": "success",
            "notification_id": len(self.notification_queue),
            "to": name,
            "via": self.contacts[name]["contact_method"],
            "status": "Message Queued"
        }
    
    def get_state_summary(self) -> Dict:
        return {
            "calendar": self.calendar,
            "budget": self.budget,
            "contacts": list(self.contacts.keys()),
            "venues_count": len(self.venues),
            "notifications_queued": len(self.notification_queue)
        }


world = WorldState()
