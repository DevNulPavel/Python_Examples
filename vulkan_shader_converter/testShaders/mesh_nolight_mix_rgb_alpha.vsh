attribute vec4 a_position;
attribute vec3 a_normal;
attribute vec2 a_texcoord;
//attribute vec4 a_color;

varying vec4 v_color;
varying vec2 v_texcoord;

#if defined BUILD_IOS
uniform highp mat4 u_transform;
#elif defined BUILD_ANDROID
uniform highp mat4 u_transform;
#else
uniform mat4 u_transform;
#endif
uniform float u_flipx;


void main(void)
{
    gl_Position = u_transform * vec4(a_position.x * u_flipx, a_position.yzw);
	v_texcoord = a_texcoord;
}
