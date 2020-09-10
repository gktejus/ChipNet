import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision
import torchvision.transforms as transforms
import os
import random
import pandas as pd

def imshow(img):
    img = img_denorm(img)
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()
    
    
def img_denorm(img):
    #for ImageNet the mean and std are:
    mean = np.asarray([ 0.485, 0.456, 0.406 ])
    std = np.asarray([ 0.229, 0.224, 0.225 ])

    denormalize = transforms.Normalize((-1 * mean / std), (1.0 / std))

    res = img.squeeze(0)
    res = denormalize(res)
    res = torch.clamp(res, 0, 1)    
    return(res)

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    
def adjust_learning_rate(optimizer, epoch):
    """Sets the learning rate to the initial LR decayed by 2 every 30 epochs"""
    lr = 0.05 * (0.5 ** (epoch // 30))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
        
def plot_learning_curves(logger_name):
    train_loss = []
    val_loss = []
    val_acc = []
    df = pd.read_csv('logs/'+logger_name)

    train_loss = df.iloc[1:,1]
    val_loss = df.iloc[1:,2]
    val_acc = df.iloc[1:,3]*100
    
    plt.style.use('seaborn')
    plt.plot(np.arange(len(train_loss)), train_loss, label = 'Training error')
    plt.plot(np.arange(len(train_loss)), val_loss, label = 'Validation error')
    plt.ylabel('Loss', fontsize = 14)
    plt.xlabel('Epochs', fontsize = 14)
    plt.title('Loss Curve', fontsize = 18, y = 1.03)
    plt.legend()
    plt.ylim(0,4)
    plt.show()
    print()
    
    plt.style.use('seaborn')
    plt.plot(np.arange(len(train_loss)), val_acc, label = 'Validation Accuracy')
    plt.ylabel('Accuracy', fontsize = 14)
    plt.xlabel('Epochs', fontsize = 14)
    plt.title('Accuracy curve', fontsize = 18, y = 1.03)
    plt.legend()
    plt.ylim(0,100)
    plt.show()
    print()

def visualize_model_architecture(model, budget):
    pruned_model = [3,]
    full_model = [3,]
    model.prepare_for_finetuning(budget)
    for l_block in model.modules():
        if hasattr(l_block, 'zeta'):
            gates = l_block.pruned_zeta().cpu().detach().numpy().tolist()
            full_model.append(len(gates))
            pruned_model.append(np.sum(gates))
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    full_model = np.array(full_model)
    pruned_model = np.array(pruned_model)
    ax.bar(np.arange(len(full_model)), full_model, width = 0.5, color = 'b')
    ax.bar(np.arange(len(pruned_model)), pruned_model, width = 0.5, color = 'r')
    print(full_model)
    print(pruned_model)
    plt.show()
    active_params, total_params = model.get_params_count()
    
    print(f'Total parameter count: {total_params}')
    print(f'Remaining parameter count: {active_params}')
    print(f'Remaining Parameter Fraction: {active_params/total_params}')
    return [full_model, pruned_model]

        