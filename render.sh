# Output dir
outDir="Images/"
calibDir=${outDir}"Calibration/"

# Input Dir
dataDir="./data/"
obj="shape0000_sor2_water15101"
template=${dataDir}"template.pov"
setting=${dataDir}"setting.pov"

# Render setting
D="Declare="
common="+H512 +W512 -GR -GS -GW +GFerror +GP +FJ +A -D" # Common POV-RAY render setting
# Please refer to template.pov for definition of the following parameters 
cam_obj_bg_setting="${D}cl_x=-0.05 ${D}cl_y=-0.12 ${D}cl_z=-3.74 ${D}lk_x=0.02 ${D}lk_y=-0.31 ${D}lk_z=0.00 ${D}cs_x=0.00 ${D}cam_a=1.00 ${D}cam_z=1.77 ${D}bg_sc=3.06 ${D}bg_pz=3.02 ${D}bg_rx=0.00 ${D}bg_ry=0.00 ${D}bg_rz=0.00 ${D}Dim=0.89 ${D}Trans=0.99 ${D}SC=0.85 ${D}IOR=1.48 ${D}RotZ=-31.61 ${D}RotY=-3.24 ${D}TX=0.00 ${D}TY=-1.10 ${D}FadeD=1.63 ${D}FadeP=1001.00" 
echo $cam_obj_bg_setting

# Render images, object mask and attenuation mask
mkdir -p $outDir
sed -e  's#\${ImageName}#"data/COCO_train2014_000000000009.jpg"#' ${template} > ${setting}
povray -I$setting $common +HI${dataDir}${obj}.inc ${cam_obj_bg_setting} -O${outDir}${obj}_ref ${D}Empty=1
povray -I$setting $common +HI${dataDir}${obj}.inc ${cam_obj_bg_setting} -O${outDir}${obj}
povray -I$setting $common +HI${dataDir}${obj}.inc ${cam_obj_bg_setting} -O${outDir}${obj}_mask +FN ${D}mask=1
povray -I$setting $common +HI${dataDir}${obj}.inc ${cam_obj_bg_setting} -O${outDir}${obj}_rho +FN ${D}rho=1
python processMask.py --img_dir $outDir # Process Mask

# Use graycode pattern to obtain the ground truth refractive flow field
mkdir -p ${calibDir}${obj}
sed -e  's#\${ImageName}#"./data/graycode_512_512/graycode_"#' ${template} > ${setting}
povray -I$setting $common +HI${dataDir}${obj}.inc ${cam_obj_bg_setting} +FN ${D}Calib=1 +KFI1 +KFF20 +KI1 +KF20 -O${calibDir}${obj}/graycode_
python findCorrespondence.py --in_root ${calibDir} --in_dir ${obj} --out_dir ${outDir} 
