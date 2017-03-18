#version 330 core

in vec3 vertexPosition;
in vec3 vertexNormal;
in vec2 vertexTexCoord;
in vec4 vertexTangent;

out vec3 position;

uniform mat4 modelView;
uniform mat3 modelViewNormal;
uniform mat4 mvp;

void main() {
    position = vertexPosition;

    gl_Position = mvp * vec4(vertexPosition, 1.0);
}
