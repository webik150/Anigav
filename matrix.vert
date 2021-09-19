#version 100
attribute mediump vec3 position;
attribute mediump vec3 normal;
attribute mediump vec2 uv;
varying mediump vec4 color;
uniform highp mat4  mPVM;   // transformation matrix
uniform lowp  float bpm;
uniform highp  float time;
uniform lowp  int mode;
uniform lowp  float analog0;
uniform lowp  float analog1;
uniform lowp  float analog2;
uniform lowp  float analog3;

vec3 toSphere(vec3 position, float alpha)
{
  vec3 center = vec3(0.0, 0.0, 0.0);
  float radius = 1.4;

  return position;
}

void main()
{

  color = vec4(position,1.0);
  //gl_Position = mPVM * vec4(position*(analog1/3.0+1.0), 1.0);
  gl_Position = mPVM * vec4(position, 1.0);
}
