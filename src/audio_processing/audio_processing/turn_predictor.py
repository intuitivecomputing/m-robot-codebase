"""Turn completion prediction using smart-turn model."""
import os
import numpy as np
import onnxruntime as ort
from transformers import WhisperFeatureExtractor


class TurnPredictor:
    """Predict whether a speech turn is complete or incomplete."""

    def __init__(self, model_path: str):
        """Initialize the turn predictor.
        
        Args:
            model_path: Path to the smart-turn ONNX model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        so = ort.SessionOptions()
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.inter_op_num_threads = 1
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options=so)
        
        self.feature_extractor = WhisperFeatureExtractor(chunk_length=8)
        self.sample_rate = 16000
        self.max_duration = 8  # seconds

    def _prepare_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Truncate to last 8 seconds or pad with zeros."""
        max_samples = self.max_duration * self.sample_rate
        if len(audio_array) > max_samples:
            return audio_array[-max_samples:]
        elif len(audio_array) < max_samples:
            padding = max_samples - len(audio_array)
            return np.pad(audio_array, (padding, 0), mode='constant', constant_values=0)
        return audio_array

    def predict(self, audio_array: np.ndarray) -> dict:
        """Predict turn completion.
        
        Args:
            audio_array: Audio samples at 16kHz (float32)
            
        Returns:
            dict with 'prediction' (1=complete, 0=incomplete) and 'probability'
        """
        audio_array = self._prepare_audio(audio_array)
        
        inputs = self.feature_extractor(
            audio_array,
            sampling_rate=self.sample_rate,
            return_tensors="np",
            padding="max_length",
            max_length=self.max_duration * self.sample_rate,
            truncation=True,
            do_normalize=True,
        )
        
        input_features = inputs.input_features.squeeze(0).astype(np.float32)
        input_features = np.expand_dims(input_features, axis=0)
        
        outputs = self.session.run(None, {"input_features": input_features})
        probability = outputs[0][0].item()
        prediction = 1 if probability > 0.5 else 0
        
        return {
            "prediction": prediction,
            "probability": probability,
        }
