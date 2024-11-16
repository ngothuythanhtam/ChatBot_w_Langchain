import torch
import os
print("Is CUDA available? ", torch.cuda.is_available())
os.system("nvidia-smi")
