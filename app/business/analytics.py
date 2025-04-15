# ~/Desktop/clean-code/app/business/analytics.py

import logging
from datetime import datetime, timedelta
import json
import pandas as pd
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallAnalytics:
    """
    Class for analyzing call data and generating reports
    """
    
    def __init__(self, db_session=None, mongo_db=None):
        """
        Initialize the analytics module
        
        Args:
            db_session: SQL database session for structured data
            mongo_db: MongoDB database for unstructured data
        """
        # Import here to avoid circular imports
        from ..database.sql_db import get_db_session
        from ..database.mongo_db import get_mongo_db
        
        self.db_session = db_session or get_db_session()
        self.mongo_db = mongo_db or get_mongo_db()
    
    async def get_call_volume_by_day(self, business_id, days=30):
        """
        Get call volume by day for a business
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            
        Returns:
            dict: Call volume data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # SQL query for call volume
            query = """
            SELECT 
                DATE(start_time) as call_date,
                COUNT(*) as call_count
            FROM 
                calls
            WHERE 
                business_id = :business_id
                AND start_time >= :start_date
                AND start_time <= :end_date
            GROUP BY 
                DATE(start_time)
            ORDER BY 
                call_date
            """
            
            # Execute query
            from sqlalchemy import text
            result = self.db_session.execute(
                text(query),
                {"business_id": business_id, "start_date": start_date, "end_date": end_date}
            )
            
            # Process results
            dates = []
            counts = []
            
            for row in result:
                dates.append(row[0].strftime("%Y-%m-%d"))
                counts.append(row[1])
                
            # Fill in missing dates with zero counts
            all_dates = pd.date_range(start=start_date, end=end_date).strftime("%Y-%m-%d").tolist()
            complete_data = []
            
            for date in all_dates:
                if date in dates:
                    idx = dates.index(date)
                    complete_data.append({"date": date, "count": counts[idx]})
                else:
                    complete_data.append({"date": date, "count": 0})
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "data": complete_data
            }
            
        except Exception as e:
            logger.error(f"Error getting call volume: {str(e)}")
            return {"error": str(e)}
    
    async def get_call_duration_stats(self, business_id, days=30):
        """
        Get call duration statistics
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            
        Returns:
            dict: Call duration statistics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # SQL query for call durations
            query = """
            SELECT 
                duration
            FROM 
                calls
            WHERE 
                business_id = :business_id
                AND start_time >= :start_date
                AND start_time <= :end_date
                AND status = 'completed'
            """
            
            # Execute query
            from sqlalchemy import text
            result = self.db_session.execute(
                text(query),
                {"business_id": business_id, "start_date": start_date, "end_date": end_date}
            )
            
            # Process results
            durations = [row[0] for row in result]
            
            if not durations:
                return {
                    "business_id": business_id,
                    "period": f"{days} days",
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "avg_duration": 0,
                    "min_duration": 0,
                    "max_duration": 0,
                    "total_calls": 0,
                    "total_duration": 0,
                    "distribution": []
                }
            
            # Calculate statistics
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            total_calls = len(durations)
            total_duration = sum(durations)
            
            # Create duration distribution bins
            bins = [0, 60, 120, 180, 240, 300, 600, 900, 1800, float('inf')]
            bin_labels = [
                "0-1 min", 
                "1-2 min", 
                "2-3 min", 
                "3-4 min", 
                "4-5 min", 
                "5-10 min", 
                "10-15 min", 
                "15-30 min", 
                "30+ min"
            ]
            
            distribution = [0] * len(bin_labels)
            
            for duration in durations:
                for i, upper in enumerate(bins[1:], 0):
                    if duration <= upper:
                        distribution[i] += 1
                        break
            
            # Format distribution for output
            distribution_data = [
                {"range": bin_labels[i], "count": count, "percentage": round(count / total_calls * 100, 1)}
                for i, count in enumerate(distribution)
            ]
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "avg_duration": round(avg_duration, 1),
                "min_duration": min_duration,
                "max_duration": max_duration,
                "total_calls": total_calls,
                "total_duration": total_duration,
                "distribution": distribution_data
            }
            
        except Exception as e:
            logger.error(f"Error getting call duration stats: {str(e)}")
            return {"error": str(e)}
    
    async def get_top_intents(self, business_id, days=30, limit=10):
        """
        Get top detected intents from calls
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            limit: Maximum number of top intents to return
            
        Returns:
            dict: Top intents data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # MongoDB aggregation for intent analysis
            pipeline = [
                # Match calls for the business within time period
                {
                    "$match": {
                        "business_id": business_id,
                        "created_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                # Unwind detected intents array
                {
                    "$unwind": {
                        "path": "$detected_intents",
                        "preserveNullAndEmptyArrays": False
                    }
                },
                # Group by intent name
                {
                    "$group": {
                        "_id": "$detected_intents.name",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$detected_intents.confidence"}
                    }
                },
                # Sort by count descending
                {
                    "$sort": {
                        "count": -1
                    }
                },
                # Limit to top N
                {
                    "$limit": limit
                }
            ]
            
            # Execute aggregation
            cursor = self.mongo_db.call_transcripts.aggregate(pipeline)
            
            # Convert to list
            intents = await cursor.to_list(length=limit)
            
            # Format results
            intent_data = [
                {
                    "intent": item["_id"],
                    "count": item["count"],
                    "avg_confidence": round(item["avg_confidence"], 2)
                }
                for item in intents
            ]
            
            # Get total call count for percentage calculation
            total_calls_query = [
                {
                    "$match": {
                        "business_id": business_id,
                        "created_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                {
                    "$count": "total"
                }
            ]
            
            total_result = await self.mongo_db.call_transcripts.aggregate(total_calls_query).to_list(length=1)
            total_calls = total_result[0]["total"] if total_result else 0
            
            # Add percentage to each intent
            if total_calls > 0:
                for item in intent_data:
                    item["percentage"] = round(item["count"] / total_calls * 100, 1)
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_calls": total_calls,
                "intents": intent_data
            }
            
        except Exception as e:
            logger.error(f"Error getting top intents: {str(e)}")
            return {"error": str(e)}
    
    async def get_common_entities(self, business_id, days=30):
        """
        Get commonly extracted entities from calls
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            
        Returns:
            dict: Common entities data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # MongoDB query to get extracted entities
            query = {
                "business_id": business_id,
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            projection = {
                "extracted_entities": 1
            }
            
            # Execute query
            cursor = self.mongo_db.call_transcripts.find(query, projection)
            results = await cursor.to_list(length=1000)
            
            # Process results
            entity_types = {}
            
            for doc in results:
                entities = doc.get("extracted_entities", {})
                
                for entity_type, values in entities.items():
                    if entity_type not in entity_types:
                        entity_types[entity_type] = []
                        
                    # Handle both list and string values
                    if isinstance(values, list):
                        entity_types[entity_type].extend(values)
                    else:
                        entity_types[entity_type].append(values)
            
            # Count entity occurrences
            entity_counts = {}
            
            for entity_type, values in entity_types.items():
                # Count occurrences of each value
                value_counts = {}
                
                for value in values:
                    if isinstance(value, str):
                        value_lower = value.lower()
                        value_counts[value_lower] = value_counts.get(value_lower, 0) + 1
                
                # Sort by count descending
                sorted_values = sorted(
                    value_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                # Take top 10 values
                top_values = sorted_values[:10]
                
                # Format for output
                entity_counts[entity_type] = [
                    {"value": value, "count": count}
                    for value, count in top_values
                ]
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "entities": entity_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting common entities: {str(e)}")
            return {"error": str(e)}
    
    async def get_call_action_metrics(self, business_id, days=30):
        """
        Get metrics on calls requiring action
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            
        Returns:
            dict: Call action metrics
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # SQL query for action metrics
            query = """
            SELECT 
                COUNT(*) as total_calls,
                SUM(CASE WHEN action_required = TRUE THEN 1 ELSE 0 END) as action_required_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_calls
            FROM 
                calls
            WHERE 
                business_id = :business_id
                AND start_time >= :start_date
                AND start_time <= :end_date
            """
            
            # Execute query
            from sqlalchemy import text
            result = self.db_session.execute(
                text(query),
                {"business_id": business_id, "start_date": start_date, "end_date": end_date}
            ).fetchone()
            
            total_calls = result[0] if result else 0
            action_required_count = result[1] if result else 0
            completed_calls = result[2] if result else 0
            
            # Calculate percentages
            action_percentage = round((action_required_count / total_calls * 100), 1) if total_calls > 0 else 0
            completion_percentage = round((completed_calls / total_calls * 100), 1) if total_calls > 0 else 0
            
            # MongoDB query for action types
            pipeline = [
                # Match calls for the business within time period
                {
                    "$match": {
                        "business_id": business_id,
                        "created_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        },
                        "action_required": True
                    }
                },
                # Unwind action items
                {
                    "$unwind": {
                        "path": "$action_items",
                        "preserveNullAndEmptyArrays": False
                    }
                },
                # Group by action and priority
                {
                    "$group": {
                        "_id": {
                            "action": "$action_items.action",
                            "priority": "$action_items.priority"
                        },
                        "count": {"$sum": 1}
                    }
                },
                # Sort by count
                {
                    "$sort": {
                        "count": -1
                    }
                },
                # Limit to top 10
                {
                    "$limit": 10
                }
            ]
            
            # Execute aggregation
            cursor = self.mongo_db.call_transcripts.aggregate(pipeline)
            action_types = await cursor.to_list(length=10)
            
            # Format action types
            formatted_actions = [
                {
                    "action": item["_id"]["action"],
                    "priority": item["_id"]["priority"],
                    "count": item["count"]
                }
                for item in action_types
            ]
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_calls": total_calls,
                "action_required_count": action_required_count,
                "action_percentage": action_percentage,
                "completed_calls": completed_calls,
                "completion_percentage": completion_percentage,
                "top_actions": formatted_actions
            }
            
        except Exception as e:
            logger.error(f"Error getting call action metrics: {str(e)}")
            return {"error": str(e)}
    
    async def get_keyword_frequency(self, business_id, days=30, top_n=20):
        """
        Analyze call transcripts for keyword frequency
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            top_n: Number of top keywords to return
            
        Returns:
            dict: Keyword frequency data
        """
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # MongoDB aggregation for text analysis
            pipeline = [
                # Match calls for the business within time period
                {
                    "$match": {
                        "business_id": business_id,
                        "created_at": {
                            "$gte": start_date,
                            "$lte": end_date
                        }
                    }
                },
                # Unwind transcript entries
                {
                    "$unwind": {
                        "path": "$transcript",
                        "preserveNullAndEmptyArrays": False
                    }
                },
                # Filter to only user messages
                {
                    "$match": {
                        "transcript.speaker": "user"
                    }
                },
                # Project text content
                {
                    "$project": {
                        "text": "$transcript.text"
                    }
                }
            ]
            
            # Execute aggregation
            cursor = self.mongo_db.call_transcripts.aggregate(pipeline)
            messages = await cursor.to_list(length=10000)
            
            # Process text for keyword analysis
            all_text = " ".join([msg["text"] for msg in messages])
            
            # Simple keyword extraction (in a real app, use more advanced NLP)
            import re
            from collections import Counter
            
            # Convert to lowercase and remove punctuation
            cleaned_text = re.sub(r'[^\w\s]', '', all_text.lower())
            
            # Split into words
            words = cleaned_text.split()
            
            # Remove stop words (simplified list)
            stop_words = set([
                "a", "an", "the", "and", "or", "but", "of", "to", "in", "is", "it", "for",
                "with", "on", "at", "by", "this", "that", "i", "you", "he", "she", "we", "they",
                "my", "your", "his", "her", "our", "their", "me", "him", "us", "them", "what",
                "which", "who", "when", "where", "why", "how", "do", "does", "did", "am", "is",
                "are", "was", "were", "be", "been", "have", "has", "had", "can", "could", "will",
                "would", "shall", "should", "may", "might", "must", "just", "very", "so", "from"
            ])
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Count word frequencies
            word_counts = Counter(filtered_words)
            
            # Get top N keywords
            top_keywords = word_counts.most_common(top_n)
            
            # Format for output
            keywords_data = [
                {"keyword": keyword, "count": count}
                for keyword, count in top_keywords
            ]
            
            return {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "total_messages": len(messages),
                "keywords": keywords_data
            }
            
        except Exception as e:
            logger.error(f"Error getting keyword frequency: {str(e)}")
            return {"error": str(e)}
    
    async def get_business_dashboard(self, business_id, days=30):
        """
        Get comprehensive dashboard data for a business
        
        Args:
            business_id: The business ID
            days: Number of days to analyze
            
        Returns:
            dict: Dashboard data
        """
        try:
            # Get all metrics in parallel
            call_volume = await self.get_call_volume_by_day(business_id, days)
            duration_stats = await self.get_call_duration_stats(business_id, days)
            top_intents = await self.get_top_intents(business_id, days)
            action_metrics = await self.get_call_action_metrics(business_id, days)
            keyword_data = await self.get_keyword_frequency(business_id, days)
            
            # Combine into dashboard data
            dashboard = {
                "business_id": business_id,
                "period": f"{days} days",
                "start_date": datetime.utcnow() - timedelta(days=days),
                "end_date": datetime.utcnow(),
                "call_volume": call_volume.get("data", []),
                "call_stats": {
                    "total_calls": duration_stats.get("total_calls", 0),
                    "avg_duration": duration_stats.get("avg_duration", 0),
                    "action_required_percentage": action_metrics.get("action_percentage", 0),
                    "completion_rate": action_metrics.get("completion_percentage", 0)
                },
                "duration_distribution": duration_stats.get("distribution", []),
                "top_intents": top_intents.get("intents", []),
                "top_actions": action_metrics.get("top_actions", []),
                "top_keywords": keyword_data.get("keywords", [])
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting business dashboard: {str(e)}")
            return {"error": str(e)}
