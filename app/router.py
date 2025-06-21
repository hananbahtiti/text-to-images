import logging
from tasks import task_model_a, task_model_b  # Add all models here

def run_model_task(**kwargs):
    model_name = kwargs.get("model_name")
    
    if model_name == "fal-ai/flux-pro/v1.1"                                                                   ":
        task_model_flux_pro.generate_image(**kwargs)
    elif model_name == "fal-ai/flux-pro/v1.1-ultra":
        task_model_flux_pro_ultra.generate_image(**kwargs)
    elif model_name == "fal-ai/flux/dev":
        task_model_flux_dev.generate_image(**kwargs)
    elif model_name == "fal-ai/ideogram/v2":
        task_model_ideogram_v2.generate_image(**kwargs)
    elif model_name == "fal-ai/flux/schnell":
        task_model_flux_schnell.generate_image(**kwargs)
  
    else:
        logging.error(f"Unsupported model: {model_name}")
        raise ValueError(f"Unsupported model: {model_name}")
