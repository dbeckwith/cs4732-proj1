#version 330 core

in vec3 position;

out vec4 fragColor;

void main() {
    fragColor = vec4((position + 1.0) / 2.0, 1.0);
}
