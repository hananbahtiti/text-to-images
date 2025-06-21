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
    Generate image with parameters for fal-ai/ideogram/v2.

    Arguments:
      model_name (str)
      prompt (str)
      client_id (str)
      params (dict): parameters like aspect_ratio, expand_prompt, seed, style, negative_prompt
    """
    try:
        logging.info(f"Generating image for client {client_id} with model {model_name}...")

        args = {
            "prompt": prompt,
            "aspect_ratio": params.get("aspect_ratio", "1:1"),  # default 1:1
            "expand_prompt": params.get("expand_prompt", False),
            "style": params.get("style", None),
            "negative_prompt": params.get("negative_prompt", None),
        }

        if "seed" in params and params["seed"] is not None:
            args["seed"] = params["seed"]

        # Clean None values (fal_client may not accept nulls)
        args = {k: v for k, v in args.items() if v is not None}

        logging.info(f"fal_client arguments: {args}")

        handler = fal_client.submit(model_name, arguments=args)
        result = handler.get()

        redis_conn.setex(f"result:{client_id}", RESULT_TTL, json.dumps(result))
        logging.info(f"Image generation completed for client {client_id}")

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        redis_conn.setex(f"result:{client_id}", RESULT_TTL, error_msg)
        logging.error(f"Failed to generate image for {client_id}: {error_msg}")
