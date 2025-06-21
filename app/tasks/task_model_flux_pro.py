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

async def generate_image(model_name, prompt, client_id, params):
    """
    Generate an image based on the given prompt and parameters using fal-client.

    Parameters:
      model_name (str): Model identifier.
      prompt (str): Prompt for image generation.
      client_id (str): Client ID for Redis result storage.
      params (dict): Additional model parameters (dynamic).
    """
    try:
        logging.info(f"Generating image for client {client_id} using model {model_name}...")

        # Build the argument dictionary
        args = {
            "prompt": prompt,
            "num_images": params.get("num_images", 1),
            "enable_safety_checker": params.get("enable_safety_checker", True),
            "safety_tolerance": params.get("safety_tolerance", "2"),
            "output_format": params.get("output_format", "jpeg")
        }

        # Check for image size or custom width/height
        if params.get("width") and params.get("height"):
            args["image_size"] = {"width": params["width"], "height": params["height"]}
        else:
            args["image_size"] = params.get("image_size", "landscape_4_3")

        # Optional parameters
        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        if "sync_mode" in params and params["sync_mode"] is not None:
            args["sync_mode"] = params["sync_mode"]

        # Submit the request to fal-client
        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        # Store result in Redis
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Image generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate image for {client_id}: {error_msg}")
