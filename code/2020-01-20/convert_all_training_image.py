from PIL import Image,ImageFilter
import os
path="/root/samples_training" #设置sample图片路径
'''PIX函数作用是对图片进行降噪处理
通过getpixel获取每个像素所对应的二值的数值，然后根据规则进行降噪处理
降噪规则有很多种，包括4格，8格，大于5格等等，根据实际的情况进行选择'''
def pIx(data,iteration=1):
    w,h=data.size
    for x in range(1,w-1):
        if x > 1 and x != w-2:
            left = x - 1
            leftleft= x - 2
            right = x + 1
            rightright = x + 2
        for y in range(1,h-1):
            up = y - 1
            upup = y - 2
            down = y + 1
            downdown = y + 2
            if x <= 2 or x >= (w - 2):
                data.putpixel((x,y),1)
            elif y <= 2 or y >= (h - 2):
                data.putpixel((x,y),1)
            elif data.getpixel((x,y)) == 0:
                if y > 1 and y != h-1:
                    up_color = data.getpixel((x,up))
                    down_color = data.getpixel((x,down))
                    downdown_color = data.getpixel((x,downdown))
                    left_color = data.getpixel((left,y))
                    left_down_color = data.getpixel((left,down))
                    right_color = data.getpixel((right,y))
                    right_up_color = data.getpixel((right,up))
                    right_down_color = data.getpixel((right,down))
                    if (down_color == 0 and downdown_color == 1) or (left_color == 1 and right_color == 1 and up_color == 1 and down_color == 1) or (up_color == 1 and down_color == 1):
                        data.putpixel((x,y),1)
            else:
                pass
            data.save(itcp+filename_prefix+'_strip_noise.png')
    if iteration > 1:
        iteration=iteration-1
        pIx(data,iteration=iteration)
for  filename in os.listdir(path):
    image_training_path=path
    image_training_convert_path='/root/samples_training_convert_image/'
    itp=image_training_path#简化一下变量名
    itcp=image_training_convert_path
    img=Image.open(itp+filename)
    Img=img.convert('L') #转换成灰度图
    filename_prefix=filename.split(".")[0]
    Img.save(itcp+filename_prefix+'_gray.png')
######下面是二值化图片过程###########################
    threshold=143     #阈值设置成143，根据图片的情况进行设置
    table=[]
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    photo=Img.point(table,'1')
    photo.save(itcp+filename_prefix+'_blackwhite.png')
    pIx(photo,iteration=2)      #因为图片上的横线大概是两像素宽度，所以这里迭代2次
