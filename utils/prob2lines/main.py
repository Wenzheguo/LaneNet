import os
import numpy as np
import cv2

def getLane(score):
    thr = 0.3
    coordinate = np.zeros((1, 18))
    for i in range(18):
        lineId = int(288-1-i*20/590*288)
        line = score[lineId, :]
        id = np.argmax(line)
        value = line[id]
        if np.double(value)/255 > thr:
            coordinate[0, i] = id
    if (coordinate>0).sum()<2:
        coordinate[:] = 0
    return coordinate


# Experiment name
exp = 'vgg_SCNN_DULR_w9'
exp = 'driver_37_30frame_crop_center'
# Data root
data = '../../data/CULane'
# Directory where prob imgs generated by CNN are saved.
probRoot = os.path.join('../../experiments/predicts/', exp)
# Directory to save fitted lanes.
output = os.path.join('./output/', exp)

testList = os.path.join(data, 'list/test.txt')
testList = os.path.join(data, 'list/driver_37_30frame_crop_center.txt')
show = False # set to true to visualize

file_list = [l.strip() for l in open(testList)]
num = len(file_list)
pts = 18

for i in range(len(file_list)):
    if i%100 == 0:
        print('Processing the {} th image...\n'.format(i))
    imname = file_list[i]
    imname = imname[1:] if imname[0]=='/' else imname
    existPath = os.path.join(probRoot, imname[:-3]+'exist.txt')
    exist = [l.strip() for l in open(existPath)]
    exist = exist[0].split(" ")[:4]
    coordinates = np.zeros((4, pts))
    for j in range(4):
        if exist[j]=='1':
            scorePath = os.path.join(probRoot, imname[:-4] + '_' + str(j+1) + '_avg.png')
            scoreMap = cv2.imread(scorePath)[:, :, 0]
            coordinate = getLane(scoreMap)
            coordinates[j,:] = coordinate
    
    if show:
        print(os.path.join(data, imname))
        img = cv2.imread(os.path.join(data, imname))
        H, W = img.shape[:2]
        probMaps = np.zeros((288,800,3), dtype=np.uint8)
        for j in range(4):
            color = [(0,255,0), (255,0,0), (0,0,255), (0,0,255)]
            if exist[j] =='1':
                for m in range(pts):
                    if coordinates[j, m]>0:
                        cv2.circle(img, (int(coordinates[j ,m]/800*W), int(H-1-m*20)), 2, color[j])
        cv2.imshow(imname, img)
        if cv2.waitKey(0)==ord('1'):
            cv2.destroyAllWindows()
            import sys
            sys.exit(0)
        cv2.destroyAllWindows()
    else:
        save_name = os.path.join(output, imname[:-3]+'lines.txt')
        position = save_name.rfind('/')
        prefix = ''
        if position>=0:
            prefix = save_name[0:position];
        if prefix!='' and not os.path.exists(prefix):
            os.makedirs(prefix, exist_ok=True)

        with open(save_name, 'w') as f:
            for j in range(4):
                if exist[j]=='1' and (coordinates[j]>0).sum()>1:
                    for m in range(pts):
                        if coordinates[j, m]>0:
                            print("{} {} ".format(int(coordinates[j,m]*1640/800-1), int(590-m*20)-1), end='', file=f)
                    print(file=f)