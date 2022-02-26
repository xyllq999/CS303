 # Project—Handwritten Digit Recognition Model Compression

[TOC]

## Introduction

Machine learning, especially deep neural networks (DNNs), has become the most dazzling domain witnessing successful applications in a wide spectrum of artificial intelligence (AI) tasks. The incomparable accuracy of DNNs is achieved by paying the cost of hungry memory consumption and high computational complexity, which greatly impedes their deployment in embedded systems. Therefore, the DNN compression concept was naturally proposed and widely used for memory saving and compute acceleration. In the past few years, a tremendous number of compression techniques have sprung up to pursue a satisfactory tradeoff between processing efficiency and application accuracy.  

In this project, we want to use a simple demo (Handwritten Digit Recognition) to learn how to compress an existing model.  Your task is to use one or more compression methods to compress our given reference model (LeNet-5) and exceed our reference model in such indicators as accuracy, Infer Time, Params and MACs. In addition, if you only do some tuning work or use more advanced training methods and the model size does not change, we will accept that and give you points accordingly.  

## Prerequisites

- Linux or Windows
- Python 3.9.7
- CPU or NVIDIA GPU + CUDA CuDNN

## Installation

- Install dependencies

    ```powershell
    pip install -r requirements.txt
    ```

- By default, `pip` uses a foreign mirror, which is very slow when downloading. You can use the `-i` parameter to specify the domestic mirror address, for example

    ```
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

- If `thop` is still not installed successfully through the above methods, you can try the following commands

    ```
    pip install --upgrade git+https://github.com/Lyken17/pytorch-OpCounter.git
    ```

## Quick Start

Download the project file `Project3.zip` and unzip it, then open the terminal in the project directory.

#### Folder Structure

```
.
├── checkpoints
│   └── LeNet5
│       ├── epoch-0.pth
│       ├── epoch-1.pth
│       └── ...
├── data
│   └── MNIST
├── eval
│   └── metrics.py
├── models
│   ├── footer.html
│   └── header.html
├── README.md
├── requirements.txt
├── result.txt
├── test_lenet5.py
├── test_yournet.py
├── train_lenet5.py
└── train_yournet.py
```

#### Reference Model  (LeNet-5)

- Train LeNet-5

  Run `train_lenet5.py` to train the reference model (LeNet-5). In this project, the reference model is already trained and the weight is in the directory "./checkpoints/LeNet5/".

  ```
  python train_lenet5.py \
    --checkpoint-dir <Path to directory used to store checkpoints> \
    --last-checkpoint <Path to last checkpoint> \
    --device <Get cpu or gpu device for training, default:'cpu'> \
    --batch-size <The size of samples per batch to load, default:64> \
    --epoch-start <The epoch to start training, default:0> \
    --epoch-end <The epoch to end training> 
  ```

  For example,

    ```
    python train_lenet5.py \
      --checkpoint-dir ./checkpoints/LeNet5/ \
      --epoch-end 5
    ```

- Test LeNet-5

  Run `test_lenet5.py` to calculate the accuracy, Infer Time, Params and MACs of the reference model (LeNet-5). The checkpoint of our reference model (LeNet-5) is "./checkpoints/LeNet5/epoch-6.pth". 

  ```
  python test_lenet5.py \
    --best-checkpoint <Path to the best checkpoint of LeNet-5> \
    --device <Get cpu or gpu device for training, default:'cpu'> \
    --batch-size <The size of samples per batch to load, default:64> 
  ```

  For example,
  
    ```
    python test_lenet5.py \
      --best-checkpoint ./checkpoints/LeNet5/epoch-6.pth 
    ```
  
  The performance of the reference model (LeNet-5) is as follows. You are excepted to optimize our reference model (LeNet-5).
  
    ```
    ----------------------------------------------------------------
    | Model Name | Accuracy | Infer Time(ms) | Params(M) | MACs(M) |
    ----------------------------------------------------------------
    |    LeNet-5 |    0.980 |          0.055 |     0.206 |   0.060 |
    ----------------------------------------------------------------
    ```

#### Compression Model  (YourNet)

This part is very important and requires you to complete it independently.

- First of all, you should build your neural network in "./models/YourNet.py". You can copy our reference model (LeNet5) from "./models/LeNet5.py", or refer to "./models/LeNet5.py" to build a new network by yourself. Fill in your code in begin-end.

    ```
    class YourNet(nn.Module):
        ###################### Begin #########################
        # You can build your own network here or copy our reference model (LeNet5)

        def __init__(self):
            super(YourNet, self).__init__()

        def forward(self, x):
        
        ######################  End  #########################
    ```

- Then, write your training code at “./train_yournet.py”, and train your network (YourNet) or compress the reference model (LeNet5); Fill in your code in begin-end.

    ```
    def train():
        ###################### Begin #########################
        # You can write your training code here to compress the reference model (LeNet5)
        
        
        ######################  End  #########################
        
    if __name__ == '__main__':
        ###################### Begin #########################
        # You can run your train() here
    
        train()
    
        ######################  End  #########################    
    ```

- Finally, run “./test_yournet.py” to get the accuracy, infer time, MACs and params of your model (YourNet);

    ```
    python test_yournet.py \
      --best-checkpoint <Path to the best checkpoint of YourNet> \
      --device <Get cpu or gpu device for training, default:'cpu'> \
      --batch-size <The size of samples per batch to load, default:64> 
    ```

## Model Compression Technique

Regarding model compression, we give the following methods and references, but not limited to the following methods. You can choose to use one or more of them. 

- Compact model

- Network pruning

  Network pruning refers to the process of eliminating part of the network structure, such as connections, channels, layers, etc., to make the network model more streamlined without significantly reducing the accuracy of the model.

- Knowledge distillation

  Knowledge distillation is an effective method of model compression and knowledge transfer. Its purpose is to train a smaller network to imitate a more complex teacher network.

- Data quantization

  Data quantization refers to reducing the bit width of the data flowing through the neural network model, so the model size can be reduced to save memory and simplify calculations, thereby achieving acceleration of network inference.

- References

  [1] Deng L, Li G, Han S, et al. Model compression and hardware acceleration for neural networks: A comprehensive survey[J]. Proceedings of the IEEE, 2020, 108(4): 485-532.

  [2] Sandler M, Howard A, Zhu M, et al. Mobilenetv2: Inverted residuals and linear bottlenecks[C]//Proceedings of the IEEE conference on computer vision and pattern recognition. 2018: 4510-4520.

  [3] Hinton G, Vinyals O, Dean J. Distilling the knowledge in a neural network[J]. arXiv preprint arXiv:1503.02531, 2015.

  [4] He K, Zhang X, Ren S, et al. Deep residual learning for image recognition[C]//Proceedings of the IEEE conference on computer vision and pattern recognition. 2016: 770-778.

  [5] Liu Z, Li J, Shen Z, et al. Learning efficient convolutional networks through network slimming[C]//Proceedings of the IEEE international conference on computer vision. 2017: 2736-2744.


## Evaluation

- If we can successfully run your "./test_yournet.py" and get the test results not worse than the reference model (each item), then you will be given a basic score of 60. 

- Then we will calculate the score of each item of your model (YourNet) according to the following formula

    |                | Reference Model (LeNet-5) | Compression Model (YourNet) | Your Score  |
    | :------------: | :-----------------------: | :-------------------------: | :---------: |
    |    Accuracy    |          a=0.980          |             a‘              | (a'-a)*2000 |
    | Infer Time(ms) |          i=0.055          |             i’              | (i-i')/i*50 |
    |   Params(M)    |          p=0.206          |             p‘              | (p-p')/p'*2 |
    |    MACs(M)     |          m=0.060          |             m’              | (m-m')/m'*2 |

- The sum of the above two is your final score, the full score is 100. If any indicator is worse than the reference model, zero point will be given. For example, the performance of a model (YourNet) is as follows. Then, the score of this model is 89.5.

    ```
    ----------------------------------------------------------------
    | Model Name | Accuracy | Infer Time(ms) | Params(M) | MACs(M) |
    ----------------------------------------------------------------
    |    YourNet |    0.986 |          0.049 |     0.061 |   0.013 |
    ----------------------------------------------------------------
    ```

- Don't worry about the inconsistency of infer time obtained on different machines. We will eventually test your model on the same machine to ensure fairness.

- In addition, we will randomly check the "./train_yournet.py" of 30% of the students. If it does not match the test result, we will give zero points.

## Submission

- Fill in the relevant information in "./result.txt“

  ```
  # Installation
  
  # The accuracy, infer time, MACs and params of reference model (LeNet-5)
  
  # The accuracy, infer time, MACs and params of your model (YourNet)
  
  # The command to run “./train_yournet.py”
  
  # The command to run “./test_yournet.py”
  
  # Others
  
  ```

- Submit the `Project3.zip`

