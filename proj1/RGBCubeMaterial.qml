import Qt3D.Core 2.0
import Qt3D.Render 2.0

Material {
    effect: Effect {
        techniques: [
            Technique {
                filterKeys: [
                    FilterKey {
                        id: forward
                        name: "renderingStyle"
                        value: "forward"
                    }
                ]
                graphicsApiFilter {
                    api: GraphicsApiFilter.OpenGL
                    profile: GraphicsApiFilter.CoreProfile
                    majorVersion: 3
                    minorVersion: 1
                }
                renderPasses: RenderPass {
                    shaderProgram: ShaderProgram {
                        vertexShaderCode: loadSource("file:proj1/rgb_cube.vert")
                        fragmentShaderCode: loadSource("file:proj1/rgb_cube.frag")
                    }
                }
            }
        ]
    }
}
