uniform vec2 mouse_pos;
uniform vec2 window_size;

varying vec4 color;

void main(){
    vec4 v_pos = gl_ModelViewMatrix * gl_Vertex;

    float ratio = .1;

    vec2 xy = abs(mouse_pos - v_pos.xy);

    float angle = atan(xy.y, xy.x);

    vec2 bound = window_size * ratio;

    if (length(xy) < (cos(angle)*bound.x + sin(angle)*bound.y)){
    //if (xy.x < bound.x && xy.y < bound.y){
        color = vec4(1,0,0,1);
    }
    else{
        color = vec4(0,1,0,1);
    }

    gl_Position = gl_ProjectionMatrix * v_pos;
}