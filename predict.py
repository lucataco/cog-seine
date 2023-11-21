# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path
import os
import sys
import yaml
import torch
sys.path.extend(['/SEINE'])
import subprocess

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")

    @torch.inference_mode()
    def predict(
        self,
        image: Path = Input(description="Input image"),
        width: int = Input(
            description="Width",
            default=560,
        ),
        height: int = Input(
            description="Height",
            default=240,
        ),
        num_frames: int = Input(
            description="Number of frames",
            default=16,
        ),
        cfg_scale: float = Input(
            description="Scale for classifier-free guidance", ge=1, le=50, default=8.0
        ),
        run_time: int = Input(
            description="Run time",
            default=13,
        ),
        num_sampling_steps: int = Input(
            description="Number of sampling steps",
            default=250,
        ),
        seed: int = Input(
            description="Random seed. Leave blank to randomize the seed",
            default=None,
        )
    ) -> Path:
        """Run a single prediction on the model"""
        if seed is None:
            seed = int.from_bytes(os.urandom(2), "big")
        print(f"Using seed: {seed}")
        
        # Clean up past runs (just in case)
        os.system("rm -rf /src/results/")
        os.system("mkdir -p /src/results/")

        # Create config file
        config_data = {
            'ckpt': "/src/pretrained/seine.pt",
            'pretrained_model_path': "/src/pretrained/stable-diffusion-v1-4/",
            'input_path': str(image),
            'save_path': "/src/results/",
            'model': 'UNet',
            'num_frames': num_frames,
            'image_size': [height, width],
            'use_fp16': True,
            'enable_xformers_memory_efficient_attention': True,
            'seed': str(seed),
            'run_time': str(run_time),
            'cfg_scale': cfg_scale,
            'sample_method': 'ddpm',
            'num_sampling_steps': str(num_sampling_steps),
            'text_prompt': [],
            'additional_prompt': ', slow motion.',
            'negative_prompt': '',
            'do_classifier_free_guidance': True,
            'mask_type': 'first1',
            'use_mask': True
        }

        # Write the data to a YAML file
        with open('config.yaml', 'w') as file:
            yaml.dump(config_data, file, default_flow_style=False)

        command = [
            "python", "/SEINE/sample_scripts/with_mask_sample.py",
            "--config", "/src/config.yaml"
        ]
        subprocess.run(command)
        
        output_dir = "/src/results/"
        output_path = None
        # Find an mp4 file in the "output" directory
        for file in os.listdir(output_dir):
            if file.endswith(".mp4"):
                output_path = str(output_dir + file)
                print(output_path)
                break

        return Path(output_path)