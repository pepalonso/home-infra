import * as THREE from 'three';
import { createRoot } from 'react-dom/client';
import React, { useState, useEffect } from 'react';
import { Canvas, ThreeElements, useThree } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

function CameraController() {
  const { camera } = useThree();

  useEffect(() => {
    const handleScroll = (event: WheelEvent) => {
      const zoomSpeed = 0.1;
      const delta = event.deltaY * zoomSpeed;
      camera.position.z += delta;
      // Limit zoom range
      camera.position.z = Math.max(2, Math.min(20, camera.position.z));
    };

    window.addEventListener('wheel', handleScroll);
    return () => window.removeEventListener('wheel', handleScroll);
  }, [camera]);

  return null;
}

function Box(props: ThreeElements['mesh']) {
  const [model, setModel] = useState<THREE.Group | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const loader = new GLTFLoader();

    const loadModel = async () => {
      try {
        setLoading(true);
        const gltf = await loader.loadAsync('/spacecraft.glb');
        if (isMounted) {
          setModel(gltf.scene);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to load model');
          setLoading(false);
        }
      }
    };

    loadModel();

    return () => {
      isMounted = false;
    };
  }, []);

  if (error) {
    console.error('Model loading error:', error);
    return null;
  }

  if (loading) {
    return null;
  }

  return (
    <mesh {...props} scale={1}>
      {model && <primitive object={model} />}
    </mesh>
  );
}

createRoot(document.getElementById('root') as HTMLElement).render(
  <Canvas camera={{ position: [0, 0, 10], fov: 75 }}>
    <CameraController />
    <ambientLight intensity={Math.PI / 2} />
    <spotLight
      position={[10, 10, 10]}
      angle={0.15}
      penumbra={1}
      decay={0}
      intensity={Math.PI}
    />
    <Box position={[0, 0, 0]} />
  </Canvas>,
);
