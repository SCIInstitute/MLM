uniform vec2 mouse_pos;
uniform vec2 window_size;

varying vec4 color;

float my_distance(float angle, vec2 bound){
    float x = cos(angle) * bound.x;
    float y = sin(angle) * bound.y;
    return sqrt(pow(x, 2.0) + pow(y, 2.0));
}

void main(){
/*
    vec4 v_pos = gl_ModelViewMatrix * gl_Vertex;

    v_pos.xy = v_pos.xy /v_pos.a;

    vec4 xy = vec4(v_pos.xy - mouse_pos,0,1);

    // Puts vertex back into original plane
    xy = gl_ModelViewMatrixInverse * xy;

    float angle = atan(xy.y, xy.x);

    float ratio = .1;

    // .5 is for the width of the screen cut in half
    vec2 bound = window_size * ratio * .5;

    float distAngle = my_distance(angle, bound);

    float highlightInc = .3;

    color = gl_Color;

    if (length(xy.xy) < distAngle){
        color = color + vec4(highlightInc,highlightInc,highlightInc,0);
    }

    */

    color = gl_Color;

    gl_Position = ftransform();
}