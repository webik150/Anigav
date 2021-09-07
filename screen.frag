#version 100
precision mediump float;
// Downscale Texture/Buffer
uniform sampler2D s_diffuse;
// Scene time
uniform float time;
// Resolution
uniform vec2 screenSize;
// Current mode
uniform lowp  int mode;
varying vec2 v_texcoord;

uniform highp float  analog0;
uniform highp float  analog1;
uniform highp float  analog2;
uniform highp float  analog3;

//Rotates a vector by angle
mat2 rot(float angle) {
	float s = sin(angle);
	float c = cos(angle);
	return mat2(
		c, -s,
		s, c
	);
}

vec3 fractal(vec2 coords)
{
    //3float center_r = -screenSize.x/2.0 + 0.0;
    //float center_i = -screenSize.y/2.0 + 00.0;
    float aspect = screenSize.x/screenSize.y;
    float center_r = 0.5;
    float center_i = 0.5/aspect;
    //float scale = sin(time+3.14)*0.002+0.002;
    float scale = 3.0;
    bool escape = false;
    float c_r = (coords.x/screenSize.x - center_r) * scale + sin(time/5.0)/1.5;
    float c_i = (coords.y/screenSize.x - center_i) * scale + cos(time/5.0)/1.5;
    vec2 c = rot(/*sin(time/5.0)*1.0*/analog1) * vec2(c_r, c_i);
    c_r = c.x;
    c_i = c.y;
    float z_r = 0.;
    float z_i = 0.;
    float z_r_new = 0.;
    float z_i_new = 0.;
    vec3 col = vec3(0);
    for (int i = 0; i < int((sin(time)+2.0)*20.0); i++)
    {
        z_r_new = z_r * z_r - z_i * z_i + c_r;
        z_i_new = (sin(sin(sin(time/5.0)))+2.0) * z_r * z_i + c_i;
        z_r = z_r_new;
        z_i = z_i_new;
        escape = z_r * z_r + z_i * z_i > 8.0;
//        if((c_r >= -0.003 && c_r <= 0.003) || (c_i >= -0.003 && c_i <= 0.003)) {      //Debug show center
//                return vec3(1.0);
//        }
//        if(c_r >= -1.01 && c_r <= -0.999){
//            return vec3(1.0);
//        }
        if(escape){
            col.x = float(i)/(((cos(cos(cos(time*3.0))*2.0)+1.0)*2.0)*20.0);
            return vec3(col.xy, 1.0);
        }
    }
    return vec3(col.xy, 0.0);
}

void main()
{
    if(mode == 0){
        vec4 texColor = texture2D( s_diffuse, v_texcoord.st );
        vec2 fragCoord = gl_FragCoord.xy;
        vec2 uv = (fragCoord - vec2(1920.0,1080.0) * .5) / 1080.0;
        float t = time;
        vec3 col = fractal(gl_FragCoord.xy);
        gl_FragColor = mix(mix(texColor, vec4(0.0), col.z), vec4(col,1.0),texColor.r);
        //gl_FragColor = vec4(col, 1.0);
    }else if(mode == 1){
        vec4 texColor = texture2D( s_diffuse, v_texcoord.st );
        if(texColor.w > 0.0){
                gl_FragColor = texColor;
        }else{
            vec2 fragCoord = gl_FragCoord.xy;
            vec2 uv = (fragCoord - vec2(1920.0,1080.0) * .5) / 1080.0;
            float t = time;
            vec3 col = fractal(gl_FragCoord.xy);
            gl_FragColor = mix(texColor, vec4(col, 1.0), col.z);
        }
    }
}
