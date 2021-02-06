#version 100
attribute vec3 a_position;
attribute vec2 a_texcoord;
uniform highp mat4  mPVM;
varying vec2 v_texcoord;

precision mediump float;

void main()
{
    v_texcoord = a_texcoord;

    gl_Position = vec4( a_position.xyz, 1 );
}
