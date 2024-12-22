from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from typing import Dict, Any, List, Tuple
from enum import Enum
import openai
import numpy as np

class IntentCategory(Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUERY_WEATHER = "query_weather"
    QUERY_TIME = "query_time"
    HELP_REQUEST = "help_request"
    OTHER = "other"
    UNKNOWN = "unknown"
    
    @classmethod
    def get_prompt_categories(cls) -> str:
        """Get formatted categories for prompt template, excluding UNKNOWN"""
        return "\n".join([f"- {intent.value}" for intent in cls 
                         if intent != cls.UNKNOWN])

    @classmethod
    def is_valid(cls, intent: str) -> bool:
        """Check if the given intent is a valid category"""
        return intent in [e.value for e in cls]

class IntentDetector:
    def __init__(self, num_samples: int = 3):
        self.num_samples = num_samples  # Number of samples for prediction
        self.prompt_template = """Analyze the user input and classify it into one of the following categories:
                {categories}

                Return only one classification word, without any additional content.

                <input>
                {text}
                </input>

                Classification:"""
        
        self.chain = (
            PromptTemplate.from_template(self.prompt_template)
            | ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
            | StrOutputParser()
        )

    def _get_multiple_predictions(self, text: str, categories: str) -> List[str]:
        """
        Get multiple predictions with different temperatures
        
        Args:
            text: Input text to classify
            categories: Available categories for classification
            
        Returns:
            List of predicted intents
        """
        predictions = []
        for _ in range(self.num_samples):
            try:
                intent = self.chain.invoke({
                    "text": text,
                    "categories": categories
                })
                predictions.append(intent.lower())
            except Exception:
                continue
        return predictions

    def _calculate_confidence(self, predictions: List[str]) -> Tuple[str, float]:
        """
        Calculate confidence based on prediction consistency and input characteristics
        
        Args:
            predictions: List of predicted intents
            
        Returns:
            Tuple of (most common intent, confidence score)
        """
        if not predictions:
            return IntentCategory.UNKNOWN.value, 0.1

        # Calculate frequency of each intent
        intent_counts = {}
        total_predictions = len(predictions)
        for intent in predictions:
            if IntentCategory.is_valid(intent):
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
            else:
                intent_counts[IntentCategory.OTHER.value] = \
                    intent_counts.get(IntentCategory.OTHER.value, 0) + 1

        # Find the most common intent
        max_intent = max(intent_counts.items(), key=lambda x: x[1])
        most_common_intent = max_intent[0]
        
        # Calculate confidence components
        # 1. Consistency confidence: proportion of the most common intent
        consistency_confidence = max_intent[1] / total_predictions
        
        # 2. Sample completeness: ratio of successful predictions
        sample_confidence = total_predictions / self.num_samples
        
        # 3. Distribution confidence: how dominant is the top prediction
        unique_intents = len(intent_counts)
        distribution_confidence = 1.0 / unique_intents if unique_intents > 0 else 0.1
        
        # Weight factors
        weights = {
            'consistency': 0.5,    # How consistent are the predictions
            'sample': 0.3,         # How many samples succeeded
            'distribution': 0.2    # How clear is the winner
        }
        
        # Calculate weighted confidence
        confidence = (
            consistency_confidence * weights['consistency'] +
            sample_confidence * weights['sample'] +
            distribution_confidence * weights['distribution']
        )
        
        # Apply scaling factor for very short inputs
        if len(predictions) == 1:
            confidence *= 0.8  # Reduce confidence for single prediction
            
        # Cap confidence at 0.95
        confidence = min(0.95, confidence)
        
        return most_common_intent, float(confidence)

    def detect(self, text: str, workspace_id: str = None, block_id: str = None, connections: list = None) -> Dict[str, Any]:
        """
        Detect the intent of input text with confidence calculation
        
        Args:
            text: Input text to classify
            workspace_id: ID of the workspace
            block_id: ID of the block
            connections: List of connections
            
        Returns:
            Dictionary containing intent classification results and metadata
        """
        try:
            # Get multiple predictions
            predictions = self._get_multiple_predictions(
                text, 
                IntentCategory.get_prompt_categories()
            )
            
            # Calculate final intent and confidence
            intent, confidence = self._calculate_confidence(predictions)
            
            return {
                'intent': intent,
                'confidence': confidence,
                'workspace_id': workspace_id,
                'block_id': block_id,
                'connections': connections
            }
            
        except Exception as e:
            return {
                'intent': IntentCategory.UNKNOWN.value,
                'confidence': 0.1,
                'error': str(e),
                'workspace_id': workspace_id,
                'block_id': block_id,
                'connections': connections
            } 