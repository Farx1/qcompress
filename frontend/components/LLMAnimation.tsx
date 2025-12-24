"use client"

import { useRef, useMemo } from "react"
import { Canvas, useFrame } from "@react-three/fiber"
import { OrbitControls } from "@react-three/drei"
import * as THREE from "three"

interface CubeNode {
  position: [number, number, number]
  index: number
  layer: number
}

const layerConfigs = [
  // Embedding + Premiers blocs Attention (gros heads/context)
  { x: 15, y: 10, type: "Embedding+Attn0", params: "1.2B", desc: "Token embeddings + premier self-attention" },
  { x: 14, y: 9, type: "Attention1", params: "1.1B", desc: "Multi-head attention (32 heads)" },
  { x: 13, y: 8, type: "Attention2", params: "950M", desc: "RMSNorm + attention pré-entraînée" },
  { x: 12, y: 8, type: "FFN3", params: "1B", desc: "FeedForward premier plateau" },

  // Blocs Attention intermédiaires (tapering)
  { x: 11, y: 7, type: "Attention4", params: "850M", desc: "Milieu architecture" },
  { x: 11, y: 6, type: "FFN5", params: "750M", desc: "FFN expansion (4x dim)" },
  { x: 10, y: 6, type: "Attention6", params: "700M", desc: "Rotary embeddings" },
  { x: 9, y: 6, type: "Attention7", params: "650M", desc: "Gated attention" },

  // Zone FFN dominante (plateaux)
  { x: 9, y: 5, type: "FFN8", params: "600M", desc: "Swiglu activation" },
  { x: 8, y: 5, type: "Attention9", params: "550M", desc: "Pré-alignement" },
  { x: 8, y: 5, type: "FFN10", params: "550M", desc: "Plateau capacité" },
  { x: 7, y: 5, type: "Attention11", params: "500M", desc: "Context compression" },

  // Fin blocs + spécialisation
  { x: 7, y: 4, type: "FFN12", params: "450M", desc: "Fine-tuning zone" },
  { x: 6, y: 4, type: "Attention13", params: "400M", desc: "MoE-like gating" },
  { x: 6, y: 4, type: "FFN14", params: "400M", desc: "Plateau intermédiaire" },
  { x: 5, y: 4, type: "Attention15", params: "350M", desc: "Reduced heads" },

  // Derniers blocs + Output (tapering final)
  { x: 5, y: 3, type: "FFN16", params: "300M", desc: "Final capacity" },
  { x: 5, y: 3, type: "Attention17", params: "300M", desc: "Last attention" },
  { x: 4, y: 3, type: "FFN18", params: "250M", desc: "Pre-output" },
  { x: 4, y: 3, type: "FFN19", params: "250M", desc: "Normalization" },
  { x: 4, y: 3, type: "FFN20", params: "250M", desc: "Final plateau" },

  // Output + Post-processing (LoRA/Quantization)
  { x: 3, y: 3, type: "LMHead", params: "200M", desc: "Vocab projection 128k" },
  { x: 3, y: 2, type: "LoRA1", params: "50M", desc: "Adapter 1" },
  { x: 3, y: 2, type: "LoRA2", params: "50M", desc: "Adapter 2" },
  { x: 3, y: 2, type: "Quant4bit", params: "8B→4B", desc: "Quantization layer" },

  // Padding final (1x1 pour viz cohérente)
  { x: 2, y: 2, type: "PostProc1", params: "Cache", desc: "KV cache compression" },
  { x: 2, y: 2, type: "PostProc2", params: "Cache", desc: "Attention mask" },
  { x: 2, y: 2, type: "PostProc3", params: "Cache", desc: "Speculative decoding" },
  { x: 2, y: 2, type: "PostProc4", params: "Cache", desc: "FlashAttention2" },
  { x: 2, y: 1, type: "Output", params: "Final", desc: "Token logits" },
  { x: 2, y: 1, type: "Sampler", params: "Final", desc: "Top-k/p sampling" },

  // 1x1 final (total: 8B paramètres)
  ...Array(6).fill({ x: 1, y: 1, type: "1x1", params: "Distillé", desc: "Architecture compressée" }),
]

function GridScan() {
  const cubeRefs = useRef<THREE.Mesh[]>([])
  const scanProgress = useRef(0)

  const cubeData = useMemo(() => {
    const layers = layerConfigs.length
    const cubeSize = 2 // Large cubes
    const layerSpacing = 2 // Space between layers
    const cubesArray: CubeNode[] = []

    for (let layer = 0; layer < layers; layer++) {
      const layerX = (layer - (layers - 1) / 2) * layerSpacing
      const config = layerConfigs[layer]

      for (let x = 0; x < config.x; x++) {
        for (let y = 0; y < config.y; y++) {
          const xPos = layerX
          const yPos = (y - (config.y - 1) / 2) * cubeSize
          const zPos = (x - (config.x - 1) / 2) * cubeSize

          cubesArray.push({
            position: [xPos, yPos, zPos],
            index: cubesArray.length,
            layer,
          })
        }
      }
    }

    return { cubes: cubesArray, layers, cubeSize, layerSpacing }
  }, [])

  useFrame((state, delta) => {
    scanProgress.current += delta * 0.16
    if (scanProgress.current > 1) {
      scanProgress.current = 0
    }

    const totalWidth = (cubeData.layers - 1) * cubeData.layerSpacing
    const scanX = (scanProgress.current - 0.5) * totalWidth

    cubeData.cubes.forEach((cube, i) => {
      const mesh = cubeRefs.current[i]
      if (!mesh) return

      const material = mesh.material as THREE.MeshStandardMaterial
      const distanceToScan = Math.abs(cube.position[0] - scanX)
      const threshold = 3 // Distance at which cubes light up

      if (distanceToScan < threshold) {
        // Cube is near scan plane - light it up bright white
        const intensity = Math.pow(1 - distanceToScan / threshold, 2)
        material.emissive.setHex(0xffffff)
        material.emissiveIntensity = intensity * 5
        material.color.setHex(0xffffff)
      } else {
        // Cube is far from scan - keep it dark black
        material.emissiveIntensity = 0
        material.color.setHex(0x0a0a0a)
      }
    })
  })

  return (
    <group>
      {/* Grid of cubes organized in layers */}
      {cubeData.cubes.map((cube, i) => (
        <group key={`cube-${i}`}>
          <mesh
            ref={(el) => {
              if (el) cubeRefs.current[i] = el
            }}
            position={cube.position}
          >
            <boxGeometry args={[1.9, 1.9, 1.9]} />
            <meshStandardMaterial
              color="#0a0a0a"
              emissive="#ffffff"
              emissiveIntensity={0}
              metalness={0.2}
              roughness={0.7}
            />
          </mesh>
          {/* White edges around each cube */}
          <lineSegments position={cube.position}>
            <edgesGeometry args={[new THREE.BoxGeometry(1.9, 1.9, 1.9)]} />
            <lineBasicMaterial color="#ffffff" linewidth={2} opacity={0.6} transparent />
          </lineSegments>
        </group>
      ))}
    </group>
  )
}

function Scene() {
  return (
    <>
      <color attach="background" args={["#0a0a0a"]} />
      <ambientLight intensity={0.3} />
      <pointLight position={[20, 15, 15]} intensity={1} color="#ffffff" />
      <pointLight position={[-20, -10, -10]} intensity={0.6} color="#ffffff" />

      <GridScan />

      <OrbitControls
        enableZoom={true}
        enablePan={true}
        autoRotate={false}
        maxDistance={200}
        minDistance={30}
        target={[0, 0, 0]}
      />
    </>
  )
}

export function LLMAnimation() {
  return (
    <div className="w-full h-full">
      <Canvas camera={{ position: [74.25, 5, 7], fov: 7 }} gl={{ antialias: true, alpha: true }}>
        <Scene />
      </Canvas>
    </div>
  )
}

