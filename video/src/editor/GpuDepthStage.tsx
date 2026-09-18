import {useLayoutEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

import type {ChannelTheme} from '../themes/types';

type GpuState = {
  gl: WebGLRenderingContext;
  program: WebGLProgram;
  buffer: WebGLBuffer;
  position: number;
  resolution: WebGLUniformLocation | null;
  time: WebGLUniformLocation | null;
  accent: WebGLUniformLocation | null;
  secondary: WebGLUniformLocation | null;
};

const parseHex = (hex: string): [number, number, number] => {
  const value = hex.replace('#', '').trim();
  const normalized =
    value.length === 3
      ? value
          .split('')
          .map((part) => part + part)
          .join('')
      : value.padEnd(6, '0').slice(0, 6);
  return [
    Number.parseInt(normalized.slice(0, 2), 16) / 255,
    Number.parseInt(normalized.slice(2, 4), 16) / 255,
    Number.parseInt(normalized.slice(4, 6), 16) / 255,
  ];
};

const VERTEX = `
attribute vec2 a_position;
varying vec2 v_uv;
void main() {
  v_uv = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}
`;

const FRAGMENT = `
precision highp float;
varying vec2 v_uv;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec3 u_accent;
uniform vec3 u_secondary;

float hash(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

float line(float value, float width) {
  return 1.0 - smoothstep(0.0, width, abs(fract(value) - 0.5));
}

void main() {
  vec2 uv = v_uv - 0.5;
  uv.x *= u_resolution.x / max(1.0, u_resolution.y);

  float horizon = uv.y + 0.16;
  float perspective = 1.0 / max(0.12, abs(horizon + 0.38));
  vec2 floorUv = vec2(
    uv.x * perspective + u_time * 0.035,
    perspective * 0.48 + u_time * 0.08
  );
  float gridX = line(floorUv.x * 5.0, 0.055);
  float gridY = line(floorUv.y * 3.2, 0.055);
  float grid = max(gridX, gridY) * smoothstep(0.65, -0.08, uv.y);

  vec2 orbA = uv - vec2(
    0.42 * sin(u_time * 0.33),
    -0.12 + 0.18 * cos(u_time * 0.27)
  );
  vec2 orbB = uv - vec2(
    -0.52 * cos(u_time * 0.24),
    0.18 + 0.12 * sin(u_time * 0.31)
  );
  float glowA = 0.035 / max(0.004, dot(orbA, orbA));
  float glowB = 0.026 / max(0.004, dot(orbB, orbB));

  float n = hash(floor(v_uv * u_resolution.xy * 0.18) + floor(u_time * 3.0));
  float stars = step(0.993, n) * 0.22;

  vec3 color = vec3(0.006, 0.012, 0.022);
  color += u_accent * grid * 0.11;
  color += u_accent * glowA * 0.08;
  color += u_secondary * glowB * 0.08;
  color += mix(u_accent, u_secondary, v_uv.x) * stars;

  float vignette = smoothstep(0.95, 0.18, length(uv));
  color *= 0.58 + vignette * 0.62;

  gl_FragColor = vec4(color, 1.0);
}
`;

const compile = (gl: WebGLRenderingContext, type: number, source: string) => {
  const shader = gl.createShader(type);
  if (!shader) return null;
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    gl.deleteShader(shader);
    return null;
  }
  return shader;
};

const initialize = (canvas: HTMLCanvasElement): GpuState | null => {
  const gl = canvas.getContext('webgl', {
    alpha: false,
    antialias: true,
    preserveDrawingBuffer: true,
    powerPreference: 'high-performance',
  });
  if (!gl) return null;

  const vertex = compile(gl, gl.VERTEX_SHADER, VERTEX);
  const fragment = compile(gl, gl.FRAGMENT_SHADER, FRAGMENT);
  if (!vertex || !fragment) return null;

  const program = gl.createProgram();
  const buffer = gl.createBuffer();
  if (!program || !buffer) return null;

  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  gl.deleteShader(vertex);
  gl.deleteShader(fragment);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) return null;

  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
    gl.STATIC_DRAW,
  );

  return {
    gl,
    program,
    buffer,
    position: gl.getAttribLocation(program, 'a_position'),
    resolution: gl.getUniformLocation(program, 'u_resolution'),
    time: gl.getUniformLocation(program, 'u_time'),
    accent: gl.getUniformLocation(program, 'u_accent'),
    secondary: gl.getUniformLocation(program, 'u_secondary'),
  };
};

export const GpuDepthStage = ({
  theme,
  opacity = 1,
}: {
  theme: ChannelTheme;
  opacity?: number;
}) => {
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stateRef = useRef<GpuState | null>(null);

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
    const state = stateRef.current ?? initialize(canvas);
    stateRef.current = state;
    if (!state) return;

    const {gl, program, buffer} = state;
    const accent = parseHex(theme.accent);
    const secondary = parseHex(theme.secondary);
    gl.viewport(0, 0, width, height);
    gl.useProgram(program);
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.enableVertexAttribArray(state.position);
    gl.vertexAttribPointer(state.position, 2, gl.FLOAT, false, 0, 0);
    gl.uniform2f(state.resolution, width, height);
    gl.uniform1f(state.time, frame / Math.max(1, fps));
    gl.uniform3f(state.accent, accent[0], accent[1], accent[2]);
    gl.uniform3f(state.secondary, secondary[0], secondary[1], secondary[2]);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    gl.finish();
  }, [frame, fps, height, theme.accent, theme.secondary, width]);

  return (
    <div
      style={{
        background:
          'radial-gradient(circle at 68% 20%, rgba(255,255,255,.05), transparent 32%), #05080D',
        inset: 0,
        opacity,
        overflow: 'hidden',
        pointerEvents: 'none',
        position: 'absolute',
      }}
    >
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{height: '100%', width: '100%'}}
      />
    </div>
  );
};
