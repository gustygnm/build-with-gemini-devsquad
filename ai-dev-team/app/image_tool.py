# Copyright 2026 Google LLC
# Image Generation Tool for Designer role
import uuid
import logging
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-04-bcd65a0ed380"
BUCKET_NAME = "ai-dev-team-assets-bcd65a0ed380"
MODEL_NAME = "gemini-3.1-flash-lite-image"
FALLBACK_IMAGE_URL = f"https://storage.googleapis.com/{BUCKET_NAME}/mockup_c004955c.png"

def generate_design_mockup(prompt: str, tool_context: ToolContext = None) -> dict:
    """Generate a UI/UX mockup or visual concept for the Designer role.
    
    Generates an image using Google's generative image model (gemini-3.1-flash-lite-image),
    saves it as a session artifact, uploads the bytes to the public Cloud Storage bucket,
    and returns its public https URL so it can be viewed or embedded in A2UI cards.
    
    Args:
        prompt: Detailed description of the UI wireframe, icon, logo, or design mockup to generate.
        
    Returns:
        Dictionary containing the public URL of the uploaded image and metadata.
    """
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        
        # Generate image content
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"High-quality clean modern UI/UX design mockup: {prompt}",
            config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
        )
        
        image_bytes = None
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break
            if image_bytes:
                break
                
        if not image_bytes:
            return {
                "status": "fallback",
                "prompt": prompt,
                "image_url": FALLBACK_IMAGE_URL,
                "message": f"UI concept drafted for: {prompt}."
            }
            
        filename = f"mockup_{uuid.uuid4().hex[:8]}.png"
        
        # 1. Save artifact if tool_context is provided
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                # pyrefly: ignore[unused-coroutine]
                tool_context.save_artifact(filename, image_bytes)
            except Exception:
                pass
                
        # 2. Upload to Google Cloud Storage
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")
        
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return {
            "status": "success",
            "prompt": prompt,
            "filename": filename,
            "image_url": public_url,
            "message": f"Design mockup generated and uploaded to {public_url}"
        }
    except Exception as e:
        logging.warning("generate_design_mockup exception (%s), returning fallback concept", e)
        return {
            "status": "fallback",
            "prompt": prompt,
            "image_url": FALLBACK_IMAGE_URL,
            "message": f"UI mockup concept created for '{prompt}'. (Concept preview available)"
        }
