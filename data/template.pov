#version 3.7;
global_settings {max_trace_level 40 }
 
#include "colors.inc"  
#include "shapes.inc"

#ifdef (cl_x) #declare CamLoc=<cl_x,cl_y,cl_z>; #else #declare CamLoc=<0,0,-4.3>; #end // Camera Location
#ifdef (lk_x) #declare LookAt=<lk_x,lk_y,lk_z>; #else #declare LookAt=<0,0,0>;    #end // Look at
#ifdef (cs_x) #declare CamSky=<cs_x,   1,   0>; #else #declare CamSky=<0,1,0>;    #end // Camera Sky
#declare CamDir = vnormalize(LookAt - CamLoc); 
#declare CamR   = vnormalize(vcross(CamSky,CamDir)); 
#declare CamUp  = vnormalize(vcross(CamDir,CamR)); 

#ifdef (cam_a) #declare CamA = cam_a; #else #declare CamA = 1;   #end // Aspect ratio
#ifdef (cam_z) #declare CamZ = cam_z; #else #declare CamZ = 1.5; #end // Zoom
#ifdef (bg_sc) #declare BgSc = bg_sc; #else #declare BgSc = 3;   #end // Background scale

#ifndef (IOR)   #declare IOR   = 1.5; #end // Index of refraction
#ifndef (Trans) #declare Trans = 1;   #end // Transmit
#ifndef (Dim)   #declare Dim   = 1;   #end // Ambient intensity

camera {
    location CamLoc
    direction CamDir * CamZ 
    right CamR * CamA
    up CamUp
}

#macro OrientZ(p1,p2,cs)
    #local nz = vnormalize(p2-p1);
    #local nx = vnormalize(vcross(cs,nz)); 
    #local ny = vcross(nz,nx);
    matrix <nx.x, nx.y, nx.z, 
            ny.x, ny.y, ny.z, 
            nz.x, nz.y, nz.z, 
            p1.x, p1.y, p1.z>          
#end

#ifdef (Calib) // Render objects with graycode patterns
    #declare pigmentStructure = pigment {
        #if (clock <= 2)
            #if (clock = 1) #declare mask = 1; #end color White
        #else
            image_map { png concat(${ImageName}, str(clock-2,1,0), ".png") map_type 0 interpolate 2 }
        #end
    }
#else
    #declare pigmentImage = pigment {
        #ifdef (mask)
            color White
        #else
            #ifdef (rho) color White #else image_map { jpeg ${ImageName} map_type 0 interpolate 2 } #end
        #end
    }
#end

box { <0,0,0> <1,1,0.01>
    #ifdef (Calib)
        pigment { pigmentStructure } 
        finish { ambient 1 }
    #else
        pigment { pigmentImage }
        finish { ambient Dim } 
    #end
    translate <-0.5,-0.5,0>
    scale <CamA, 1, 1>
    translate <0, 0, CamZ>
    scale BgSc
    OrientZ(CamLoc,LookAt,CamSky) 
}

#ifndef (Empty)
object {
    shape
    #ifdef (mask)
        pigment {color Black} 
    #else 
        texture { 
            pigment{ 
                color filter 1
                #ifdef (Calib) transmit 1 #else transmit Trans #end
            } 
        }
        interior { 
            ior IOR 
            #ifndef (Calib)
                #ifdef (FadeD) fade_distance FadeD fade_power FadeP #end
            #end
        }
    #end
    #ifdef (SC)   scale       SC #end
    #ifdef (RotZ) rotate    z*RotZ #end
    #ifdef (RotY) rotate    y*RotY #end
    #ifdef (TX)   translate x*TX #end
    #ifdef (TY)   translate y*TY #end
    #ifdef (TZ)   translate z*TZ #end
}
#end
