import torch
x = torch.rand(5, 3)
print(x)

print("CUDA availability:")
print(torch.cuda.is_available())