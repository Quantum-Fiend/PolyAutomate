"""
NLP Processor
Handles natural language processing tasks
"""
import logging
from typing import Dict, Any, Optional
from transformers import pipeline
import time

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Handles NLP tasks using transformers"""
    
    def __init__(self):
        """Initialize NLP models"""
        self.summarizer = None
        self.sentiment_analyzer = None
        logger.info("NLP Processor initialized (models loaded on-demand)")
    
    def _load_summarizer(self):
        """Lazy load summarization model"""
        if self.summarizer is None:
            logger.info("Loading summarization model...")
            self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            logger.info("Summarization model loaded")
    
    def _load_sentiment_analyzer(self):
        """Lazy load sentiment analysis model"""
        if self.sentiment_analyzer is None:
            logger.info("Loading sentiment analysis model...")
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            logger.info("Sentiment analysis model loaded")
    
    def summarize_text(self, text: str, max_length: int = 150, 
                      min_length: int = 50) -> Dict[str, Any]:
        """
        Summarize text using BART model
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of summary
            min_length: Minimum length of summary
            
        Returns:
            Dict containing summary and metadata
        """
        start_time = time.time()
        
        try:
            self._load_summarizer()
            
            # Truncate input if too long (BART has max 1024 tokens)
            if len(text.split()) > 1000:
                text = ' '.join(text.split()[:1000])
            
            # Generate summary
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'summary': result[0]['summary_text'],
                'original_length': len(text),
                'summary_length': len(result[0]['summary_text']),
                'processing_time_ms': processing_time_ms,
                'model': 'facebook/bart-large-cnn'
            }
            
        except Exception as e:
            logger.error(f"Error in text summarization: {e}")
            return {
                'error': str(e),
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict containing sentiment label and score
        """
        start_time = time.time()
        
        try:
            self._load_sentiment_analyzer()
            
            # Truncate if too long
            if len(text.split()) > 500:
                text = ' '.join(text.split()[:500])
            
            result = self.sentiment_analyzer(text)[0]
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                'sentiment': result['label'],
                'confidence': result['score'],
                'processing_time_ms': processing_time_ms,
                'model': 'distilbert-base-uncased-finetuned-sst-2-english'
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'error': str(e),
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text
        (Placeholder for future implementation)
        """
        return {
            'entities': [],
            'note': 'Entity extraction not yet implemented'
        }
