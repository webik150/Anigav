#version 100
attribute mediump vec3 position;
varying mediump vec4 color;
uniform highp mat4  mPVM;   // transformation matrix

vec3 toSphere(vec3 position, float alpha)
{
  vec3 center = vec3(0.0, 0.0, 0.0);
  float radius = 1.4;

  return position;
}

void main()
{
  color = vec4(position,1.0);
  gl_Position = mPVM * vec4(position, 1.0);
}
