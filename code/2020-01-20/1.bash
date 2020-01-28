#!/bin/bash
#将所有png图片拷贝到新目录下，以防误删除，因为图片过滤500张大概需要3个小时
cp /root/samples_training_convert_image/* /root/samples_training_after_filter/
cd /root/samples_training_after_filter
#去除掉中转图片
shopt -s extglob
rm -rf !(*strip*)
#将图片以结果名称重命名 如:e2d66_strip_noise.png---->e2d66.png
for i in `ls`
do
rename "_strip_noise" "" *
done
#将png格式图片转化为tif
for i in `ls`
do
k=${i%.*}
convertformat $i $k.tif
done
#将png图片删除
rm -rf *.png
