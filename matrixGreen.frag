#version 100
//https://www.khronos.org/opengles/sdk/docs/reference_cards/OpenGL-ES-2_0-Reference-card.pdf
uniform highp mat4  mPVM;   // transformation matrix
uniform lowp  float bpm;   // transformation matrix
uniform lowp  float time;   // transformation matrix
uniform lowp  float analog0;   // transformation matrix
uniform lowp  float val2;   // transformation matrix
uniform lowp  float val3;   // transformation matrix
varying mediump vec4 color;

void main()
{
    mediump float strength = pow(gl_FragCoord.w*3.0, 5.0);
    mediump vec3 col = vec3((analog0+1.0)/2.0, 0, (analog0+1.0)/2.0);
    if (strength>val2){
        discard;
    }
    gl_FragColor = vec4(mix(col, vec3(0.3, 0, 1.0), strength), 1.0);
}
