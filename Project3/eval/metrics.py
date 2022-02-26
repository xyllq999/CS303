import time
import torch
from thop import profile

def get_accuracy(model, test_loader, device):
    size = len(test_loader.dataset)
    model.eval()
    correct = 0
    with torch.no_grad():
        for X, y in test_loader:
            X, y = X.to(device), y.to(device)
            pred_y = model(X)
            correct += (pred_y.argmax(1) == y).type(torch.float).sum().item()
    accuracy = correct / size
    return accuracy

def get_infer_time(model, test_loader, device):
    size = len(test_loader.dataset)
    model.eval()
    with torch.no_grad():
        start = time.time()
        for X, y in test_loader:
            X, y = X.to(device), y.to(device)
            pred_y = model(X)
        end = time.time()
    infer_time = (end - start)/size
    return infer_time


def get_macs_and_params(model, device):
    input = torch.randn(1, 1, 28, 28).to(device=device)
    MACs, params = profile(model, inputs=(input,),verbose=True)
    return MACs,params