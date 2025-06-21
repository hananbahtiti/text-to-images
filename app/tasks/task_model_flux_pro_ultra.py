import fal_client
from redis import Redis
import logging
import os
import json
from dotenv import load_dotenv

load_dotenv()

os.environ["FAL_KEY"] = "671b3239-6a7c-4449-a85e-caa161fe3351:631d5730d85692de182d398b1b072496"

redis_conn = Redis(host="redis", port=6379)
logging.basicConfig(level=logging.INFO)

RESULT_TTL = 3600

def generate_image(model_name, prompt, client_id, params):
    """
    Generate an image using fal-client with full control over model parameters.
    
    Parameters:
      model_name (str): The model to use, e.g., 'fal-ai/flux-pro/v1.1-ultra'
      prompt (str): The text prompt for image generation.
      client_id (str): Unique client ID for result storage.
      params (dict): Dynamic parameters for the model.
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        # Build argument dictionary for fal-client
        args = {
            "prompt": prompt,
            "num_images": params.get("num_images", 1),
            "enable_safety_checker": params.get("enable_safety_checker", True),
            "safety_tolerance": params.get("safety_tolerance", "2"),
            "output_format": params.get("output_format", "jpeg"),
            "aspect_ratio": params.get("aspect_ratio", "landscape_4_3"),
            "raw": params.get("raw", False)
        }

        # Optional parameters
        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        if "sync_mode" in params and params["sync_mode"] is not None:
            args["sync_mode"] = params["sync_mode"]

        # Submit request to fal-client
        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        # Save result to Redis
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Image generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate image for {client_id}: {error_msg}")
