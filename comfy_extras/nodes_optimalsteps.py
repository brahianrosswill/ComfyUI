# from https://github.com/bebebe666/OptimalSteps

import numpy as np
import torch


def loglinear_interp(t_steps, num_steps):
    """
    Performs log-linear interpolation of a given array of decreasing numbers.
    """
    xs = np.linspace(0, 1, len(t_steps))
    ys = np.log(t_steps[::-1])

    new_xs = np.linspace(0, 1, num_steps)
    new_ys = np.interp(new_xs, xs, ys)

    interped_ys = np.exp(new_ys)[::-1].copy()
    return interped_ys


NOISE_LEVELS = {"FLUX": [0.9968, 0.9886, 0.9819, 0.975, 0.966, 0.9471, 0.9158, 0.8287, 0.5512, 0.2808, 0.001],
"Wan": [1.0, 0.997, 0.995, 0.993, 0.991, 0.989, 0.987, 0.985, 0.98, 0.975, 0.973, 0.968, 0.96, 0.946, 0.927, 0.902, 0.864, 0.776, 0.539, 0.208, 0.001], "SDXL": [12.1769, 9.9182, 7.0887, 4.5944, 2.2473, 0.9020, 0.2872, 0.0738, 0.0197, 0.0020, 0.001],
"Chroma": [0.992, 0.99, 0.988, 0.985, 0.982, 0.978, 0.973, 0.968, 0.961, 0.953, 0.943, 0.931, 0.917, 0.9, 0.881, 0.858, 0.832, 0.802, 0.769, 0.731, 0.69, 0.646, 0.599, 0.55, 0.501, 0.451, 0.402, 0.355, 0.311, 0.27, 0.232, 0.199, 0.169, 0.143, 0.12, 0.101, 0.084, 0.07, 0.058, 0.048, 0.001]}


class OptimalStepsScheduler:
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_type": (["FLUX", "Wan", "SDXL", "Chroma"], ),
                "steps": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 1000
                }),
                "denoise": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01
                }),
            },
            "optional": {
                "custom_sigmas": ("STRING", {
                    "default": "",
                    "placeholder": "Comma-separated sigma values"
                }),
            }
        }

    RETURN_TYPES = ("SIGMAS", )
    CATEGORY = "sampling/custom_sampling/schedulers"

    FUNCTION = "get_sigmas"

    def get_sigmas(self, model_type, steps, denoise, custom_sigmas=""):
        total_steps = steps
        if denoise < 1.0:
            if denoise <= 0.0:
                return (torch.FloatTensor([]), )
            total_steps = round(steps * denoise)

        if custom_sigmas:
            # Parse the custom_sigmas string into a list of floats
            try:
                sigmas = [float(s.strip()) for s in custom_sigmas.split(",") if s.strip()]
            except ValueError:
                raise ValueError("Invalid custom_sigmas format. Ensure it is a comma-separated list of numbers.")
        else:
            # Use the predefined NOISE_LEVELS
            sigmas = NOISE_LEVELS[model_type][:]
        if (steps + 1) != len(sigmas):
            sigmas = loglinear_interp(sigmas, steps + 1)

        sigmas = sigmas[-(total_steps + 1):]
        sigmas[-1] = 0
        return (torch.FloatTensor(sigmas), )


NODE_CLASS_MAPPINGS = {
    "OptimalStepsScheduler": OptimalStepsScheduler,
}
