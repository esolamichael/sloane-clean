"""
Natural Language Understanding module using custom TensorFlow/PyTorch models.
"""
import os
import numpy as np
# Try to import TensorFlow and PyTorch, but provide fallback if not available
try:
    import tensorflow as tf
    import torch
    from transformers import AutoTokenizer, AutoModel
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available, using fallback NLU processing")

from . import config

class IntentClassifier:
    """
    Intent classification model using TensorFlow.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the intent classifier model with either TensorFlow models or fallback logic.
        
        """
        self.fallback_mode = not TENSORFLOW_AVAILABLE
        
        if not self.fallback_mode:
            # Original initialization code for TensorFlow
            self.intent_classifier = IntentClassifier(model_path)
            self.entity_extractor = EntityExtractor(model_path)
            # Keep any other original initialization code here
        else:
            # Simple fallback mode
            print("Using simple rule-based NLU processing")
    
    def process_text(self, text):
        """
        Process text input to determine intent and extract entities.
        """
        if not self.fallback_mode:
            # Original TensorFlow-based processing
            # Keep the original code here
            intent = self.intent_classifier.classify(text)
            entities = self.entity_extractor.extract(text)
            # Any other original processing code

        return {
                "intent": intent,
                "entities": entities,
                "confidence": 0.9
            }
        else:
            # Simple rule-based processing
            intent = "unknown"
            entities = {}
            
            # Simple keyword matching
            if "hours" in text.lower() or "open" in text.lower():
                intent = "business_hours"
            elif "appointment" in text.lower() or "schedule" in text.lower() or "book" in text.lower():
                intent = "schedule_appointment"
            elif "location" in text.lower() or "address" in text.lower():
                intent = "business_location"
            elif "service" in text.lower() or "product" in text.lower():
                intent = "service_inquiry"
            elif "urgent" in text.lower() or "emergency" in text.lower() or "important" in text.lower():
                intent = "high_value_transfer"
            
	return {
                "intent": intent,
                "entities": entities,
                "confidence": 0.7
            }
    
    def load_model(self):
        """Load the TensorFlow model if it exists, otherwise create a placeholder."""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            print(f"Loaded intent model from {self.model_path}")
        except (OSError, IOError):
            print(f"No existing model found at {self.model_path}. Using placeholder model.")
            # Create a placeholder model for demonstration
            self._create_placeholder_model()
    
    def _create_placeholder_model(self):
        """Create a simple placeholder model for demonstration purposes."""
        # This would be replaced with a properly trained model in production
        inputs = tf.keras.layers.Input(shape=(768,))
        x = tf.keras.layers.Dense(256, activation='relu')(inputs)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(10, activation='softmax')(x)  # Assuming 10 intent classes
        
        self.model = tf.keras.Model(inputs=inputs, outputs=outputs)
        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def predict_intent(self, text):
        """
        Predict the intent of the given text.
        
        Args:
            text (str): The input text.
            
        Returns:
            dict: Intent prediction with confidence scores.
        """
        # For demonstration, we'll use a simple mapping of intents
        # In a real implementation, this would use the actual model prediction
        
        # Example intents for a business call
        intents = [
            "greeting", "appointment_scheduling", "business_hours", 
            "service_inquiry", "pricing", "complaint", "urgent_request",
            "general_question", "contact_request", "goodbye"
        ]
        
        # Simple keyword-based intent detection for demonstration
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["hello", "hi", "hey", "morning", "afternoon", "evening"]):
            intent_idx = 0  # greeting
        elif any(word in text_lower for word in ["appointment", "schedule", "book", "reserve", "slot"]):
            intent_idx = 1  # appointment_scheduling
        elif any(word in text_lower for word in ["hour", "open", "close", "time", "when"]):
            intent_idx = 2  # business_hours
        elif any(word in text_lower for word in ["service", "offer", "provide", "available"]):
            intent_idx = 3  # service_inquiry
        elif any(word in text_lower for word in ["price", "cost", "fee", "charge", "much"]):
            intent_idx = 4  # pricing
        elif any(word in text_lower for word in ["complaint", "issue", "problem", "unhappy", "dissatisfied"]):
            intent_idx = 5  # complaint
        elif any(word in text_lower for word in ["urgent", "emergency", "immediately", "asap", "right now"]):
            intent_idx = 6  # urgent_request
        elif any(word in text_lower for word in ["question", "wonder", "curious", "know"]):
            intent_idx = 7  # general_question
        elif any(word in text_lower for word in ["contact", "reach", "talk", "speak", "call back"]):
            intent_idx = 8  # contact_request
        elif any(word in text_lower for word in ["bye", "goodbye", "thank", "end", "hang up"]):
            intent_idx = 9  # goodbye
        else:
            intent_idx = 7  # default to general_question
        
        # Create a mock confidence distribution
        confidences = np.zeros(len(intents))
        confidences[intent_idx] = 0.7  # Primary intent
        
        # Add some noise to other intents
        for i in range(len(intents)):
            if i != intent_idx:
                confidences[i] = np.random.uniform(0, 0.1)
        
        # Normalize to ensure sum is 1
        confidences = confidences / np.sum(confidences)
        
        # Create result dictionary
        result = {
            "intent": intents[intent_idx],
            "confidence": float(confidences[intent_idx]),
            "all_intents": {intents[i]: float(confidences[i]) for i in range(len(intents))}
        }
        
        return result


class EntityExtractor:
    """
    Named entity recognition using PyTorch and transformers.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the entity extractor model.
        
        Args:
            model_path (str): Path to the saved model. If None, uses the default path.
        """
        self.model_path = model_path or config.ENTITY_MODEL_PATH
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.model = AutoModel.from_pretrained("distilbert-base-uncased")
        
        # Entity types we want to extract
        self.entity_types = [
            "PERSON", "DATE", "TIME", "PHONE_NUMBER", "EMAIL", 
            "SERVICE", "LOCATION", "ORGANIZATION", "MONEY"
        ]
    
    def extract_entities(self, text):
        """
        Extract entities from the given text.
        
        Args:
            text (str): The input text.
            
        Returns:
            list: Extracted entities with their types and positions.
        """
        # For demonstration, we'll use a simple rule-based approach
        # In a real implementation, this would use a proper NER model
        
        entities = []
        text_lower = text.lower()
        
        # Simple pattern matching for demonstration
        
        # Date patterns (very simplified)
        date_patterns = [
            r"\b(today|tomorrow|yesterday)\b",
            r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(st|nd|rd|th)?\b",
            r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b"
        ]
        
        # Time patterns (very simplified)
        time_patterns = [
            r"\b\d{1,2}:\d{2}\s*(am|pm)?\b",
            r"\b\d{1,2}\s*(am|pm)\b",
            r"\b(morning|afternoon|evening|night)\b"
        ]
        
        # Phone number patterns (very simplified)
        phone_patterns = [
            r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ]
        
        # Email patterns (very simplified)
        email_patterns = [
            r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        ]
        
        # Money patterns (very simplified)
        money_patterns = [
            r"\$\d+(\.\d{2})?",
            r"\d+\s*dollars"
        ]
        
        # For demonstration, we'll just do some simple checks
        # In a real implementation, we would use regex or a proper NER model
        
        words = text.split()
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Check for dates
            if any(term in word_lower for term in ["today", "tomorrow", "yesterday", "monday", "tuesday", 
                                                 "wednesday", "thursday", "friday", "saturday", "sunday",
                                                 "january", "february", "march", "april", "may", "june",
                                                 "july", "august", "september", "october", "november", "december"]):
                entities.append({
                    "type": "DATE",
                    "text": word,
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })
            
            # Check for times
            if any(term in word_lower for term in ["am", "pm", "morning", "afternoon", "evening"]) or ":" in word:
                entities.append({
                    "type": "TIME",
                    "text": word,
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })
            
            # Very simple check for phone numbers
            if word.replace("-", "").replace(".", "").replace(" ", "").isdigit() and len(word) >= 10:
                entities.append({
                    "type": "PHONE_NUMBER",
                    "text": word,
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })
            
            # Simple check for email
            if "@" in word and "." in word:
                entities.append({
                    "type": "EMAIL",
                    "text": word,
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })
            
            # Simple check for money
            if "$" in word or word_lower.endswith("dollars"):
                entities.append({
                    "type": "MONEY",
                    "text": word,
                    "start": text.find(word),
                    "end": text.find(word) + len(word)
                })
        
        return entities


class NLUProcessor:
    """
    Natural Language Understanding processor that combines intent classification
    and entity extraction.
    """
    
    def __init__(self):
        """Initialize the NLU processor with intent and entity models."""
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
    
    def process(self, text):
        """
        Process the input text to extract intent and entities.
        
        Args:
            text (str): The input text.
            
        Returns:
            dict: The processed NLU result with intent and entities.
        """
        intent_result = self.intent_classifier.predict_intent(text)
        entities = self.entity_extractor.extract_entities(text)
        
        return {
            "text": text,
            "intent": intent_result,
            "entities": entities
        }
