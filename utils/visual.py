from .dataset_info import *

import cv2
import numpy as np
import torch.nn.functional as F
import matplotlib.pyplot as plt


def watch_dataload_heatmap(gt_heatmap):
    heatmap_sum = gt_heatmap[0]
    for index in range(boundary_num - 1):
        heatmap_sum += gt_heatmap[index + 1]
    cv2.imshow('heatmap_sum', heatmap_sum)
    cv2.moveWindow('heatmap_sum', 0, 0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def watch_pic_kp(dataset, pic, kp):
    for kp_index in range(dataset_kp_num[dataset]):
        cv2.circle(pic,
                   (int(kp[2*kp_index]), int(kp[2*kp_index+1])),
                   1,
                   (0, 0, 255))
    cv2.imshow('pic', pic)
    cv2.moveWindow('pic', 0, 0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def watch_pic_kp_xy(dataset, pic, coord_x, coord_y):
    for kp_index in range(dataset_kp_num[dataset]):
        cv2.circle(pic,
                   (int(coord_x[kp_index]), int(coord_y[kp_index])),
                   1,
                   (0, 0, 255))
    cv2.imshow('pic', pic)
    cv2.moveWindow('pic', 0, 0)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def eval_heatmap(arg, heatmaps, img_name, bbox, save_only=False):
    heatmaps = F.interpolate(heatmaps, scale_factor=4, mode='bilinear', align_corners=True)
    heatmaps = heatmaps.squeeze(0)
    heatmaps = heatmaps.detach().cpu().numpy()
    heatmaps_sum = heatmaps[0]
    for heatmaps_index in range(12):
        heatmaps_sum += heatmaps[heatmaps_index+1]
    plt.axis('off')
    plt.imshow(heatmaps_sum, interpolation='nearest', vmax=1.)
    if save_only:
        import os
        if not os.path.exists('./imgs'):
            os.mkdir('./imgs')
        fig = plt.gcf()
        fig.set_size_inches(2.56 / 3, 2.56 / 3)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        plt.margins(0, 0)
        name = (img_name[0]).split('/')[-1]
        fig.savefig('./imgs/'+name.split('.')[0]+'_hm.png', format='png', transparent=True, dpi=300, pad_inches=0)

        assert arg.dataset in ['300W']
        bbox = bbox.squeeze().numpy()
        pic = cv2.imread(dataset_route[arg.dataset] + img_name[0])
        position_before = np.float32([
            [int(bbox[0]), int(bbox[1])],
            [int(bbox[0]), int(bbox[3])],
            [int(bbox[2]), int(bbox[3])]
        ])
        position_after = np.float32([
            [0, 0],
            [0, arg.crop_size - 1],
            [arg.crop_size - 1, arg.crop_size - 1]
        ])
        crop_matrix = cv2.getAffineTransform(position_before, position_after)
        pic = cv2.warpAffine(pic, crop_matrix, (arg.crop_size, arg.crop_size))
        cv2.imwrite('./imgs/' + name.split('.')[0] + '_init.png', pic)
        hm = cv2.imread('./imgs/'+name.split('.')[0]+'_hm.png')
        syn = cv2.addWeighted(pic, 0.4, hm, 0.6, 0)
        cv2.imwrite('./imgs/'+name.split('.')[0]+'_syn.png', syn)
        return
    plt.show()


def eval_points(arg, pred_coords, img_name, bbox, save_only=False):
    assert arg.dataset in ['300W']
    pred_coords = pred_coords.squeeze().numpy()
    bbox = bbox.squeeze().numpy()
    pic = cv2.imread(dataset_route[arg.dataset] + img_name[0])
    position_before = np.float32([
        [int(bbox[0]), int(bbox[1])],
        [int(bbox[0]), int(bbox[3])],
        [int(bbox[2]), int(bbox[3])]
    ])
    position_after = np.float32([
        [0, 0],
        [0, arg.crop_size - 1],
        [arg.crop_size - 1, arg.crop_size - 1]
    ])
    crop_matrix = cv2.getAffineTransform(position_before, position_after)
    pic = cv2.warpAffine(pic, crop_matrix, (arg.crop_size, arg.crop_size))

    for coord_index in range(dataset_kp_num[arg.dataset]):
        cv2.circle(pic, (int(pred_coords[2 * coord_index]), int(pred_coords[2 * coord_index + 1])), 2, (0, 0, 255))
    if save_only:
        import os
        if not os.path.exists('./imgs'):
            os.mkdir('./imgs')
        name = (img_name[0]).split('/')[-1]
        cv2.imwrite('./imgs/'+name.split('.')[0]+'_lmk.png', pic)
    else:
        cv2.imshow('pic', pic)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
