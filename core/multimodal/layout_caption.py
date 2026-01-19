"""
Multimodal layout captioning for page images.
Generates captions describing page layout and content.
"""
from typing import List, Dict, Any, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False


class LayoutCaptioner:
    """
    Generates layout-aware captions for page images.
    Captions describe structure, tables, figures, etc.
    """
    
    def __init__(self):
        """Initialize captioner (can use vision models in future)."""
        self.available = MULTIMODAL_AVAILABLE
    
    def caption_page(self, image_path: str, page_number: int, text_preview: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate layout caption for a page image.
        
        Args:
            image_path: Path to page image
            page_number: Page number
            text_preview: Optional text preview for context
        
        Returns:
            Dict with caption, layout_info, and metadata
        """
        if not self.available or not PIL_AVAILABLE:
            return self._fallback_caption(page_number, text_preview)
        
        try:
            # Load image
            from PIL import Image
            image = Image.open(image_path)
            width, height = image.size
            
            # Analyze layout (simplified - in production use layout models)
            layout_info = self._analyze_layout(image, text_preview)
            
            # Generate caption
            caption = self._generate_caption(page_number, layout_info, text_preview)
            
            return {
                "page_number": page_number,
                "caption": caption,
                "layout_info": layout_info,
                "image_dimensions": {"width": width, "height": height},
                "has_text": bool(text_preview and len(text_preview.strip()) > 0),
                "has_tables": layout_info.get("table_count", 0) > 0,
                "has_figures": layout_info.get("figure_count", 0) > 0
            }
        except Exception as e:
            return {
                "page_number": page_number,
                "caption": f"Page {page_number} - [Caption generation error: {str(e)}]",
                "layout_info": {},
                "error": str(e)
            }
    
    def _analyze_layout(self, image: Image.Image, text_preview: Optional[str]) -> Dict[str, Any]:
        """Analyze page layout (simplified heuristic-based approach)."""
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1.0
        
        layout_info = {
            "aspect_ratio": aspect_ratio,
            "orientation": "landscape" if aspect_ratio > 1.2 else "portrait",
            "table_count": 0,
            "figure_count": 0,
            "text_density": "unknown"
        }
        
        # Simple heuristics based on text preview
        if text_preview:
            # Count potential table indicators
            lines = text_preview.split("\n")
            table_indicators = sum(1 for line in lines if "|" in line or "\t" in line)
            layout_info["table_count"] = min(table_indicators // 3, 5)  # Rough estimate
            
            # Estimate text density
            char_count = len(text_preview)
            if char_count > 2000:
                layout_info["text_density"] = "high"
            elif char_count > 500:
                layout_info["text_density"] = "medium"
            else:
                layout_info["text_density"] = "low"
        
        return layout_info
    
    def _generate_caption(self, page_number: int, layout_info: Dict[str, Any], text_preview: Optional[str]) -> str:
        """Generate natural language caption."""
        parts = [f"Page {page_number}"]
        
        # Add layout description
        orientation = layout_info.get("orientation", "unknown")
        parts.append(f"({orientation} orientation)")
        
        # Add content description
        if layout_info.get("table_count", 0) > 0:
            parts.append(f"contains {layout_info['table_count']} table(s)")
        
        if layout_info.get("text_density") != "unknown":
            parts.append(f"with {layout_info['text_density']} text density")
        
        # Add text preview snippet if available
        if text_preview:
            preview = text_preview[:100].replace("\n", " ")
            parts.append(f"- Content preview: {preview}...")
        
        return " ".join(parts)
    
    def _fallback_caption(self, page_number: int, text_preview: Optional[str]) -> Dict[str, Any]:
        """Fallback caption when multimodal models unavailable."""
        caption = f"Page {page_number}"
        if text_preview:
            preview = text_preview[:100].replace("\n", " ")
            caption += f" - Text content: {preview}..."
        
        return {
            "page_number": page_number,
            "caption": caption,
            "layout_info": {"note": "Multimodal models not available"},
            "has_text": bool(text_preview),
            "has_tables": False,
            "has_figures": False
        }
    
    def embed_caption(self, caption: str) -> List[float]:
        """
        Embed caption text for hybrid retrieval.
        Uses same embedder as text chunks for consistency.
        """
        # In production, could use multimodal embedder
        # For now, use text embedder (same as chunks)
        from core.embeddings.local_embedder import LocalEmbedder
        embedder = LocalEmbedder()
        return embedder.embed_query(caption).tolist()
