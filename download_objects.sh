cd data
# Download  dataset
dataset="TOM-Net_Povray_Inc_Objects.tgz"
wget http://www.visionlab.cs.hku.hk/data/TOM-Net/$dataset
tar -zxvf $dataset
rm $dataset

# Back to root directory
cd ../
