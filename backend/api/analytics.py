"""
Analytics and Metrics Collection for Healthcare Multi-Agent System
Tracks usage patterns, agent performance, and user engagement
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
import json


@dataclass
class AgentInteraction:
    """Single agent interaction record"""
    session_id: str
    agent_name: str
    timestamp: datetime
    user_message: str
    response_length: int
    duration_ms: Optional[float] = None
    hitl_flagged: bool = False
    user_rating: Optional[int] = None
    

@dataclass
class SessionMetrics:
    """Metrics for a single session"""
    session_id: str
    started_at: datetime
    last_interaction: datetime
    total_interactions: int
    agents_used: Dict[str, int]
    hitl_flags: int
    avg_rating: Optional[float] = None
    completed_actions: List[str] = None
    

class AnalyticsTracker:
    """
    In-memory analytics tracker for the healthcare multi-agent system.
    In production, this would write to a database or analytics service.
    """
    
    def __init__(self):
        self.interactions: List[AgentInteraction] = []
        self.sessions: Dict[str, SessionMetrics] = {}
        self.agent_metrics: Dict[str, Dict] = defaultdict(lambda: {
            "total_calls": 0,
            "total_duration_ms": 0,
            "hitl_flags": 0,
            "avg_rating": 0.0,
            "ratings_count": 0,
        })
    
    def record_interaction(
        self,
        session_id: str,
        agent_name: str,
        user_message: str,
        response_length: int,
        duration_ms: Optional[float] = None,
        hitl_flagged: bool = False,
    ) -> None:
        """Record a single agent interaction"""
        now = datetime.now()
        
        # Create interaction record
        interaction = AgentInteraction(
            session_id=session_id,
            agent_name=agent_name,
            timestamp=now,
            user_message=user_message[:100],  # Truncate for privacy
            response_length=response_length,
            duration_ms=duration_ms,
            hitl_flagged=hitl_flagged,
        )
        self.interactions.append(interaction)
        
        # Update session metrics
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMetrics(
                session_id=session_id,
                started_at=now,
                last_interaction=now,
                total_interactions=0,
                agents_used={},
                hitl_flags=0,
                completed_actions=[],
            )
        
        session = self.sessions[session_id]
        session.last_interaction = now
        session.total_interactions += 1
        session.agents_used[agent_name] = session.agents_used.get(agent_name, 0) + 1
        if hitl_flagged:
            session.hitl_flags += 1
        
        # Update agent metrics
        metrics = self.agent_metrics[agent_name]
        metrics["total_calls"] += 1
        if duration_ms:
            metrics["total_duration_ms"] += duration_ms
        if hitl_flagged:
            metrics["hitl_flags"] += 1
    
    def record_rating(self, session_id: str, agent_name: str, rating: int) -> None:
        """Record user rating for an interaction"""
        if session_id in self.sessions:
            # Update session rating
            session = self.sessions[session_id]
            ratings = [i.user_rating for i in self.interactions 
                      if i.session_id == session_id and i.user_rating is not None]
            ratings.append(rating)
            session.avg_rating = sum(ratings) / len(ratings)
            
            # Update agent rating
            metrics = self.agent_metrics[agent_name]
            total = metrics["avg_rating"] * metrics["ratings_count"] + rating
            metrics["ratings_count"] += 1
            metrics["avg_rating"] = total / metrics["ratings_count"]
    
    def get_dashboard_metrics(self, hours: int = 24) -> Dict:
        """
        Get dashboard metrics for the specified time period.
        
        Args:
            hours: Number of hours to look back (default 24)
            
        Returns:
            Dict with comprehensive metrics
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Filter recent interactions
        recent_interactions = [
            i for i in self.interactions
            if i.timestamp > cutoff
        ]
        
        # Calculate metrics
        total_interactions = len(recent_interactions)
        active_sessions = len(set(i.session_id for i in recent_interactions))
        hitl_flags = sum(1 for i in recent_interactions if i.hitl_flagged)
        
        # Agent usage breakdown
        agent_usage = defaultdict(int)
        for interaction in recent_interactions:
            agent_usage[interaction.agent_name] += 1
        
        # Average response times
        avg_duration = {}
        for agent_name, metrics in self.agent_metrics.items():
            if metrics["total_calls"] > 0:
                avg_duration[agent_name] = (
                    metrics["total_duration_ms"] / metrics["total_calls"]
                )
        
        # Session duration analysis
        session_durations = []
        for session in self.sessions.values():
            if session.started_at > cutoff:
                duration = (session.last_interaction - session.started_at).total_seconds()
                session_durations.append(duration)
        
        avg_session_duration = (
            sum(session_durations) / len(session_durations)
            if session_durations else 0
        )
        
        return {
            "overview": {
                "total_interactions": total_interactions,
                "active_sessions": active_sessions,
                "hitl_flags": hitl_flags,
                "avg_session_duration_seconds": round(avg_session_duration, 2),
                "time_period_hours": hours,
            },
            "agent_usage": dict(agent_usage),
            "agent_performance": {
                agent_name: {
                    "total_calls": metrics["total_calls"],
                    "avg_duration_ms": round(avg_duration.get(agent_name, 0), 2),
                    "hitl_flags": metrics["hitl_flags"],
                    "avg_rating": round(metrics["avg_rating"], 2),
                    "ratings_count": metrics["ratings_count"],
                }
                for agent_name, metrics in self.agent_metrics.items()
            },
            "top_sessions": self._get_top_sessions(5),
            "recent_hitl_flags": self._get_recent_hitl_flags(10),
        }
    
    def get_session_details(self, session_id: str) -> Optional[Dict]:
        """Get detailed metrics for a specific session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        interactions = [
            {
                "agent": i.agent_name,
                "timestamp": i.timestamp.isoformat(),
                "message_preview": i.user_message[:50],
                "response_length": i.response_length,
                "hitl_flagged": i.hitl_flagged,
                "rating": i.user_rating,
            }
            for i in self.interactions
            if i.session_id == session_id
        ]
        
        return {
            "session_id": session.session_id,
            "started_at": session.started_at.isoformat(),
            "last_interaction": session.last_interaction.isoformat(),
            "duration_minutes": round(
                (session.last_interaction - session.started_at).total_seconds() / 60, 2
            ),
            "total_interactions": session.total_interactions,
            "agents_used": session.agents_used,
            "hitl_flags": session.hitl_flags,
            "avg_rating": session.avg_rating,
            "interactions": interactions,
        }
    
    def _get_top_sessions(self, limit: int) -> List[Dict]:
        """Get top sessions by interaction count"""
        sorted_sessions = sorted(
            self.sessions.values(),
            key=lambda s: s.total_interactions,
            reverse=True
        )[:limit]
        
        return [
            {
                "session_id": s.session_id,
                "total_interactions": s.total_interactions,
                "agents_used": len(s.agents_used),
                "duration_minutes": round(
                    (s.last_interaction - s.started_at).total_seconds() / 60, 2
                ),
            }
            for s in sorted_sessions
        ]
    
    def _get_recent_hitl_flags(self, limit: int) -> List[Dict]:
        """Get recent HITL-flagged interactions"""
        hitl_interactions = [
            i for i in self.interactions
            if i.hitl_flagged
        ]
        
        # Sort by timestamp, most recent first
        hitl_interactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "session_id": i.session_id,
                "agent": i.agent_name,
                "timestamp": i.timestamp.isoformat(),
                "message_preview": i.user_message[:100],
            }
            for i in hitl_interactions[:limit]
        ]
    
    def export_metrics(self, filepath: str) -> None:
        """Export all metrics to a JSON file"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_sessions": len(self.sessions),
            "total_interactions": len(self.interactions),
            "metrics": self.get_dashboard_metrics(hours=24 * 7),  # Last 7 days
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


# Global analytics tracker instance
analytics = AnalyticsTracker()
