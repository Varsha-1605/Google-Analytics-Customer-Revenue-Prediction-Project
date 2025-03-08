"""Latency tracking utility for model responses."""
import time
from functools import wraps
from statistics import mean, median
import streamlit as st
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LatencyTracker:
    def __init__(self):
        self.response_times = []
        self.batch_times = []
        
    def record_latency(self, latency):
        """Record a single latency measurement."""
        self.response_times.append(latency)
        
    def record_batch_latency(self, latency):
        """Record batch prediction latency."""
        self.batch_times.append(latency)
    
    def get_statistics(self):
        """Calculate latency statistics."""
        if not self.response_times:
            return None
            
        stats = {
            'avg_response_time': mean(self.response_times) * 1000,  # Convert to ms
            'median_response_time': median(self.response_times) * 1000,
            'min_response_time': min(self.response_times) * 1000,
            'max_response_time': max(self.response_times) * 1000,
            'total_predictions': len(self.response_times)
        }
        
        if self.batch_times:
            stats.update({
                'avg_batch_time': mean(self.batch_times) * 1000,
                'total_batches': len(self.batch_times)
            })
            
        return stats

# Initialize global tracker
latency_tracker = LatencyTracker()

def measure_latency(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        latency_tracker.record_latency(execution_time)
        logger.info(f"Function {func.__name__} execution time: {execution_time*1000:.2f}ms")
        
        return result
    return wrapper

def measure_batch_latency(func):
    """Decorator to measure batch prediction time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        latency_tracker.record_batch_latency(execution_time)
        logger.info(f"Batch prediction time: {execution_time*1000:.2f}ms")
        
        return result
    return wrapper