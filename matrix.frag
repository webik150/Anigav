#version 100
//https://www.khronos.org/opengles/sdk/docs/reference_cards/OpenGL-ES-2_0-Reference-card.pdf
uniform highp mat4  mPVM;   // transformation matrix
uniform lowp  float bpm;
uniform highp  float time;
uniform lowp  int mode;
uniform lowp  float val1;
uniform lowp  float val2;
uniform lowp  float val3;
varying mediump vec4 color;

lowp float minute = 60.0;

void main()
{

    mediump float strength = pow(gl_FragCoord.w*3.0,5.0);
    if(strength<=val2){
        discard;
    }else{
        if(mod(time, minute*2.0/bpm)>=minute/1.0/bpm){
            //discard;
        }else{
                gl_FragColor = vec4(0.0,1.0,0.0, 1.0);
        }
    }
}
