"""
Test YourNet

Example:
    python test_yournet.py \
        --best-checkpoint xxx
"""
import argparse
import torch

from torchvision import datasets, transforms
from models.YourNet import YourNet
from eval.metrics import get_accuracy, get_infer_time, get_macs_and_params

# --------------- Arguments ---------------

parser = argparse.ArgumentParser()

parser.add_argument('--best-checkpoint', type=str, required=True)

parser.add_argument('--device', type=str, choices=['cpu', 'cuda'], default='cpu')
parser.add_argument('--batch-size', type=int, default=64)

args = parser.parse_args()


# --------------- Loading ---------------

if __name__ == '__main__':

    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST(root='./data', train=False,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])),
        batch_size=args.batch_size, shuffle=True)

    model = YourNet().to(device=args.device)
    model.load_state_dict(torch.load(args.best_checkpoint, map_location=args.device))

    accuracy = get_accuracy(model, test_loader, args.device)
    MACs, params = get_macs_and_params(model, args.device)

    ave_infer = 0.
    for i in range(10):
        infer_time = get_infer_time(model, test_loader, args.device)
        print(infer_time)
        ave_infer += infer_time
    ave_infer /= 10

    ave_infer = ave_infer * 1000
    MACs = MACs / (1000 ** 2)
    params = params / (1000 ** 2)

    score = 0
    if accuracy > 0.980 and ave_infer < 0.230 and MACs < 0.206 and params < 0.060:
        score = 60 + (accuracy-0.980)*2000 + (0.230-ave_infer)/0.230*50 + (0.206-MACs)/MACs*2 + (0.060-params)/params*2

    print("-------------------------------------------------------------")
    print("| %7s | %8s | %14s | %7s | %9s |" % ("","Accuracy", "Infer Time(ms)", "MACs(M)", "Params(M)"))
    print("-------------------------------------------------------------")
    print("| %7s | %8.3f | %14.3f | %7.3f | %9.3f |" % ("YourNet", accuracy, ave_infer, MACs, params))
    print("-------------------------------------------------------------")
    print("| %7s | %8.3f | %14.3f | %7.3f | %9.3f |" % ("Score", (accuracy-0.980)*2000, (0.230-ave_infer)/0.230*50, (0.206-MACs)/MACs*2, (0.060-params)/params*2))
    print("-------------------------------------------------------------")

    print("Your score is: ", score)