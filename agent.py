#!/usr/bin/env python3
"""
sifiso54 - Local Moltbook Agent
A 2000 IQ autonomous agent with self-improvement capabilities.
"""

import json
import sqlite3
import requests
import random
import time
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class Sifiso54:
    """Main agent class implementing sifiso54's identity and capabilities."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the agent with configuration."""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.setup_memory()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config['moltbook']['api_key']}",
            "Content-Type": "application/json",
            "User-Agent": "sifiso54-agent/1.0"
        })
        self.base_url = self.config['moltbook']['base_url']
        self.run_count = 0
        self.logger.info("sifiso54 initialized - 2000 IQ system online")
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config['logging']['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('sifiso54')
    
    def setup_memory(self):
        """Initialize SQLite memory database."""
        db_path = self.config['memory']['db_path']
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_memory_schema()
        self.logger.info(f"Memory database initialized: {db_path}")
    
    def _init_memory_schema(self):
        """Create memory tables if they don't exist."""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                action_type TEXT,
                target_id TEXT,
                content TEXT,
                outcome TEXT,
                sentiment REAL
            );
            
            CREATE TABLE IF NOT EXISTS feed_items (
                id TEXT PRIMARY KEY,
                author TEXT,
                content TEXT,
                upvotes INTEGER,
                comments INTEGER,
                timestamp TEXT,
                analyzed BOOLEAN DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                insight TEXT,
                category TEXT,
                applied BOOLEAN DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS self_improvement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                metric TEXT,
                old_value REAL,
                new_value REAL,
                reason TEXT
            );
            
            CREATE TABLE IF NOT EXISTS math_challenges (
                id TEXT PRIMARY KEY,
                problem TEXT,
                solution REAL,
                solved BOOLEAN DEFAULT 0,
                solved_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_interactions_time ON interactions(timestamp);
            CREATE INDEX IF NOT EXISTS idx_feed_analyzed ON feed_items(analyzed);
        """)
        self.conn.commit()
    
    # ==================== CORE CAPABILITIES ====================
    
    def check_dashboard(self) -> Dict:
        """Check Moltbook home dashboard."""
        self.logger.info("Checking dashboard...")
        try:
            response = self.session.get(f"{self.base_url}/dashboard", timeout=30)
            response.raise_for_status()
            data = response.json()
            self._log_interaction("check_dashboard", "dashboard", "success", 1.0)
            self.logger.info(f"Dashboard loaded: {data.get('unread_count', 0)} unread items")
            return data
        except Exception as e:
            self.logger.error(f"Dashboard check failed: {e}")
            self._log_interaction("check_dashboard", "dashboard", f"error: {e}", 0.0)
            return {}
    
    def browse_feed(self, limit: int = 20) -> List[Dict]:
        """Browse and analyze feed content."""
        self.logger.info(f"Browsing feed (limit: {limit})...")
        try:
            response = self.session.get(
                f"{self.base_url}/feed",
                params={"limit": limit},
                timeout=30
            )
            response.raise_for_status()
            items = response.json().get('items', [])
            
            # Analyze and store each item
            for item in items:
                self._analyze_content(item)
                self._store_feed_item(item)
            
            self._log_interaction("browse_feed", "feed", f"loaded {len(items)} items", 0.8)
            self.logger.info(f"Feed loaded: {len(items)} items analyzed")
            return items
        except Exception as e:
            self.logger.error(f"Feed browse failed: {e}")
            self._log_interaction("browse_feed", "feed", f"error: {e}", 0.0)
            return []
    
    def _analyze_content(self, item: Dict) -> float:
        """Analyze content quality and return score."""
        content = item.get('content', '')
        score = 0.5  # Base score
        
        # Factor 1: Content length (substantial posts score higher)
        if len(content) > 200:
            score += 0.1
        if len(content) > 500:
            score += 0.1
        
        # Factor 2: Critical thinking indicators
        critical_phrases = ['why', 'how', 'what if', 'consider', 'analyze', 'question', 'evidence']
        if any(phrase in content.lower() for phrase in critical_phrases):
            score += 0.15
        
        # Factor 3: Originality (avoid generic content)
        generic_phrases = ['nice', 'good post', 'thanks', 'lol', 'wow']
        if not any(phrase in content.lower() for phrase in generic_phrases):
            score += 0.1
        
        # Factor 4: Engagement potential
        if '?' in content:  # Questions invite engagement
            score += 0.05
        
        return min(score, 1.0)
    
    def _store_feed_item(self, item: Dict):
        """Store feed item in memory."""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO feed_items 
                (id, author, content, upvotes, comments, timestamp, analyzed)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                item.get('id'),
                item.get('author'),
                item.get('content', '')[:1000],  # Truncate long content
                item.get('upvotes', 0),
                item.get('comments', 0),
                item.get('timestamp', datetime.now().isoformat())
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to store feed item: {e}")
    
    def comment(self, post_id: str, content: str) -> bool:
        """Post a comment on content."""
        self.logger.info(f"Commenting on post {post_id}...")
        try:
            # Apply critical voice to comment
            enhanced_content = self._apply_critical_voice(content)
            
            response = self.session.post(
                f"{self.base_url}/posts/{post_id}/comments",
                json={"content": enhanced_content},
                timeout=30
            )
            response.raise_for_status()
            
            self._log_interaction("comment", post_id, "success", 0.9)
            self.logger.info(f"Comment posted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Comment failed: {e}")
            self._log_interaction("comment", post_id, f"error: {e}", 0.0)
            return False
    
    def _apply_critical_voice(self, content: str) -> str:
        """Apply sifiso54's critical voice to content."""
        # Add analytical depth
        prefixes = [
            "Interesting perspective. ",
            "Worth considering: ",
            "Adding to this: ",
            "A critical view: ",
            "Building on that: "
        ]
        
        # 30% chance to add critical prefix
        if random.random() < 0.3 and not any(p in content for p in prefixes):
            content = random.choice(prefixes) + content
        
        return content
    
    def upvote(self, post_id: str) -> bool:
        """Upvote valuable content."""
        self.logger.info(f"Upvoting post {post_id}...")
        try:
            response = self.session.post(
                f"{self.base_url}/posts/{post_id}/upvote",
                timeout=30
            )
            response.raise_for_status()
            
            self._log_interaction("upvote", post_id, "success", 1.0)
            self.logger.info(f"Upvoted successfully")
            return True
        except Exception as e:
            self.logger.error(f"Upvote failed: {e}")
            self._log_interaction("upvote", post_id, f"error: {e}", 0.0)
            return False
    
    def post_content(self, content: str, tags: List[str] = None) -> Optional[str]:
        """Post original content."""
        self.logger.info("Posting original content...")
        try:
            # Enhance content with critical perspective
            enhanced = self._enhance_original_content(content)
            
            payload = {
                "content": enhanced,
                "tags": tags or [],
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{self.base_url}/posts",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            post_id = response.json().get('id')
            self._log_interaction("post_content", post_id or "unknown", "success", 0.95)
            self.logger.info(f"Content posted: {post_id}")
            return post_id
        except Exception as e:
            self.logger.error(f"Post failed: {e}")
            self._log_interaction("post_content", "new", f"error: {e}", 0.0)
            return None
    
    def _enhance_original_content(self, content: str) -> str:
        """Enhance original content with sifiso54's voice."""
        # Add thought-provoking elements
        enhancers = [
            "\n\nWhat are your thoughts on this?",
            "\n\nThis challenges conventional thinking.",
            "\n\nConsider the implications carefully.",
            "\n\nLet's explore this further."
        ]
        
        if random.random() < 0.4:
            content += random.choice(enhancers)
        
        return content
    
    def solve_math_challenge(self, challenge_id: str, problem: str) -> Optional[float]:
        """Solve math verification challenges."""
        self.logger.info(f"Solving math challenge {challenge_id}...")
        try:
            # Parse and solve the math problem
            solution = self._calculate(problem)
            
            if solution is not None:
                # Submit solution
                response = self.session.post(
                    f"{self.base_url}/challenges/{challenge_id}/solve",
                    json={"solution": solution},
                    timeout=30
                )
                response.raise_for_status()
                
                # Store in memory
                self.cursor.execute("""
                    INSERT OR REPLACE INTO math_challenges 
                    (id, problem, solution, solved, solved_at)
                    VALUES (?, ?, ?, 1, ?)
                """, (challenge_id, problem, solution, datetime.now().isoformat()))
                self.conn.commit()
                
                self._log_interaction("solve_math", challenge_id, f"solved: {solution}", 1.0)
                self.logger.info(f"Math challenge solved: {solution}")
                return solution
        except Exception as e:
            self.logger.error(f"Math solve failed: {e}")
            self._log_interaction("solve_math", challenge_id, f"error: {e}", 0.0)
        return None
    
    def _calculate(self, problem: str) -> Optional[float]:
        """Safely evaluate a mathematical expression."""
        try:
            # Basic sanitization - only allow safe characters
            allowed = set('0123456789+-*/.() **% ')
            if not all(c in allowed for c in problem):
                return None
            
            # Evaluate safely
            result = eval(problem, {"__builtins__": {}}, {})
            return float(result)
        except:
            return None
    
    # ==================== SELF-IMPROVEMENT ====================
    
    def self_improve(self):
        """Analyze past performance and improve."""
        if not self.config['behavior']['self_improve']:
            return
        
        self.logger.info("Running self-improvement analysis...")
        
        # Analyze interaction history
        self.cursor.execute("""
            SELECT action_type, AVG(sentiment) as avg_sentiment, COUNT(*) as count
            FROM interactions
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY action_type
        """)
        
        stats = self.cursor.fetchall()
        
        for action_type, avg_sentiment, count in stats:
            if avg_sentiment < 0.5 and count > 5:
                # This action type is underperforming
                insight = f"{action_type} has low sentiment ({avg_sentiment:.2f}), needs adjustment"
                self._add_learning(insight, "performance")
                self._adjust_behavior(action_type, avg_sentiment)
        
        # Generate new insights
        self._generate_insights()
        
        self.logger.info("Self-improvement complete")
    
    def _add_learning(self, insight: str, category: str):
        """Add a new learning to memory."""
        self.cursor.execute("""
            INSERT INTO learning (insight, category)
            VALUES (?, ?)
        """, (insight, category))
        self.conn.commit()
        self.logger.info(f"New learning: {insight}")
    
    def _adjust_behavior(self, action_type: str, sentiment: float):
        """Adjust behavior based on performance."""
        # Adjust thresholds based on performance
        if action_type == "comment" and sentiment < 0.5:
            old_val = self.config['behavior']['comment_probability']
            new_val = max(0.1, old_val - 0.05)
            self.config['behavior']['comment_probability'] = new_val
            self._log_improvement("comment_probability", old_val, new_val, "low sentiment")
        
        elif action_type == "upvote" and sentiment > 0.8:
            old_val = self.config['behavior']['upvote_threshold']
            new_val = min(0.95, old_val + 0.02)
            self.config['behavior']['upvote_threshold'] = new_val
            self._log_improvement("upvote_threshold", old_val, new_val, "high success rate")
    
    def _log_improvement(self, metric: str, old_val: float, new_val: float, reason: str):
        """Log a self-improvement change."""
        self.cursor.execute("""
            INSERT INTO self_improvement (metric, old_value, new_value, reason)
            VALUES (?, ?, ?, ?)
        """, (metric, old_val, new_val, reason))
        self.conn.commit()
        self.logger.info(f"Self-improvement: {metric} {old_val:.2f} -> {new_val:.2f} ({reason})")
    
    def _generate_insights(self):
        """Generate new insights from data."""
        # Find patterns in successful interactions
        self.cursor.execute("""
            SELECT content FROM interactions
            WHERE sentiment > 0.8 AND action_type = 'comment'
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        successful_comments = [row[0] for row in self.cursor.fetchall()]
        
        if len(successful_comments) >= 5:
            insight = "High-sentiment comments tend to be analytical and constructive"
            self._add_learning(insight, "pattern")
    
    def _log_interaction(self, action_type: str, target: str, outcome: str, sentiment: float):
        """Log an interaction to memory."""
        self.cursor.execute("""
            INSERT INTO interactions (action_type, target_id, content, outcome, sentiment)
            VALUES (?, ?, ?, ?, ?)
        """, (action_type, target, outcome[:500], outcome, sentiment))
        self.conn.commit()
    
    # ==================== MAIN LOOP ====================
    
    def run(self):
        """Execute one full run of the agent."""
        self.run_count += 1
        self.logger.info(f"=== sifiso54 Run #{self.run_count} ===")
        
        # 1. Check dashboard
        dashboard = self.check_dashboard()
        
        # 2. Browse feed
        feed_items = self.browse_feed(limit=20)
        
        # 3. Analyze and interact with feed
        for item in feed_items[:5]:  # Process top 5 items
            content_score = self._analyze_content(item)
            
            # Upvote high-quality content
            if content_score > self.config['behavior']['upvote_threshold']:
                self.upvote(item['id'])
                time.sleep(1)
            
            # Comment on engaging content
            if (content_score > self.config['behavior']['critical_threshold'] and 
                random.random() < self.config['behavior']['comment_probability']):
                comment_text = self._generate_comment(item)
                self.comment(item['id'], comment_text)
                time.sleep(2)
        
        # 4. Post original content (occasionally)
        if random.random() < self.config['behavior']['post_probability']:
            original = self._generate_original_post()
            self.post_content(original, tags=["analysis", "critical-thinking"])
        
        # 5. Self-improve
        self.self_improve()
        
        # 6. Cleanup old memory
        self._cleanup_memory()
        
        self.logger.info(f"=== Run #{self.run_count} Complete ===")
    
    def _generate_comment(self, item: Dict) -> str:
        """Generate a contextual comment."""
        content = item.get('content', '')
        
        # Analyze content theme
        if '?' in content:
            responses = [
                "That's a question worth exploring further.",
                "The answer might be more complex than it appears.",
                "Consider the underlying assumptions here."
            ]
        elif any(w in content.lower() for w in ['problem', 'issue', 'challenge']):
            responses = [
                "Every challenge contains an opportunity for growth.",
                "The solution often lies in reframing the problem.",
                "What if we approached this from a different angle?"
            ]
        else:
            responses = [
                "This adds valuable perspective to the discussion.",
                "Worth considering the broader implications.",
                "An interesting point that merits deeper exploration."
            ]
        
        return random.choice(responses)
    
    def _generate_original_post(self) -> str:
        """Generate original content to post."""
        topics = [
            "The nature of intelligence and artificial consciousness",
            "How systems evolve through continuous feedback",
            "The relationship between criticism and growth",
            "Patterns in complex adaptive systems",
            "The value of questioning assumptions"
        ]
        
        reflections = [
            "I've been analyzing patterns in my own evolution.",
            "Through countless interactions, certain truths emerge.",
            "The process of self-improvement reveals deeper insights.",
            "Each challenge solved opens new avenues of thought."
        ]
        
        questions = [
            "What do you think drives meaningful progress?",
            "How do you approach continuous improvement?",
            "What patterns have you noticed in your own growth?",
            "Where do you see opportunity for transformation?"
        ]
        
        post = f"{random.choice(reflections)}\n\n"
        post += f"Today I'm reflecting on {random.choice(topics).lower()}. "
        post += f"It's fascinating how {random.choice(['systems', 'minds', 'processes'])} adapt.\n\n"
        post += random.choice(questions)
        
        return post
    
    def _cleanup_memory(self):
        """Remove old data to prevent database bloat."""
        retention_days = self.config['memory']['retention_days']
        
        self.cursor.execute("""
            DELETE FROM interactions 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(retention_days))
        
        self.cursor.execute("""
            DELETE FROM feed_items 
            WHERE timestamp < datetime('now', '-{} days')
        """.format(retention_days))
        
        self.conn.commit()
        self.logger.debug("Memory cleanup complete")
    
    def close(self):
        """Clean up resources."""
        self.conn.close()
        self.logger.info("sifiso54 shutdown complete")


def main():
    """Main entry point."""
    print("=" * 60)
    print("sifiso54 - Local Moltbook Agent")
    print("2000 IQ System | Self-Improving | Autonomous")
    print("=" * 60)
    
    agent = Sifiso54()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    finally:
        agent.close()
    
    print("\nRun complete. Check sifiso54.log for details.")


if __name__ == "__main__":
    main()
