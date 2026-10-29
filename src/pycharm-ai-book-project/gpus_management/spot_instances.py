# Spot instance training with checkpointing
import signal

import torch


class SpotTrainingManager:

    def __init__(self, checkpoint_dir: str):
        self.checkpoint_dir = checkpoint_dir
        self.interruption_detected = False
    
    def setup_interruption_handler(self):
        """AWS sends 2-minute warning before termination"""
    
    def handle_interruption(self, sigmun, frame):
            print("Spot interruption detected! Saving checkpoint...")
            self.interruption_detected = True
            self.save_checkpoint()
    
    signal.signal(signal.SIGTERM, handle_interruption)
    
    def train_with_resume(self, model, train_loader, epochs):
        # Check for existing checkpoint
        start_epoch = 0
        if os.path.exists(f"{self.checkpoint_dir}/latest.pt"):
            checkpoint = torch.load(f"{self.checkpoint_dir}/latest.pt")
            model.load_state_dict(checkpoint['model_state'])
            start_epoch = checkpoint['epoch']
            print(f"Resuming from epoch {start_epoch}")
            optimizer = torch.optim.Adam(model.parameters())
            
        for epoch in range(start_epoch, epochs):
            for batch_idx, (data, target) in enumerate(train_loader):
                # Regular training
                optimizer.zero_grad()
                output = model(data)
                loss = F.nll_loss(output, target)
                loss.backward()
                optimizer.step()
                 # Periodic checkpointing
                if batch_idx % 100 == 0:
                    self.save_checkpoint({
                        'epoch': epoch,
                        'batch': batch_idx,
                        'model_state': model.state_dict(),
                        'optimizer_state': optimizer.state_dict()
                    })

                # Check for interruption
                if self.interruption_detected:
                    return