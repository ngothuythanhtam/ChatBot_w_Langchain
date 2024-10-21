import torch
import os

# Check if GPU is available
print("Is CUDA available? ", torch.cuda.is_available())

# Run nvidia-smi command from Python and print the output
os.system("nvidia-smi")
