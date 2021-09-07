#version 100
attribute vec3 a_position;
attribute vec2 a_texcoord;
uniform highp mat4  mPVM;
varying vec2 v_texcoord;
precision mediump float;

uniform highp float  analog1;
uniform highp float  analog2;
uniform highp float  analog3;
uniform highp float  analog4;



void main()
{
    v_texcoord = a_texcoord;
    vec3 pos = a_position.xyz * analog2;
    gl_Position = vec4( pos, 1 );
}
