<template>
  <div class="w-full h-[443px] relative overflow-hidden">
    <canvas ref="canvasRef" class="block w-full h-full"></canvas>

    <!-- Loading and Error Overlays -->
    <div v-if="isLoading" class="absolute top-0 left-0 w-full h-full bg-black/70 text-white flex justify-center items-center text-2xl z-10">
      Loading 3D Model...
    </div>
    <div v-if="error" class="absolute top-0 left-0 w-full h-full bg-red-800/70 text-white flex justify-center items-center text-2xl z-10">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, reactive, watch } from 'vue';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { gsap } from 'gsap';

const props = defineProps({
  modelPath: {
    type: String,
    default: '/3D/model.glb'
  },
  cameraInitialPosition: {
    type: Object,
    default: () => ({ x: 0, y: 2, z: 5 })
  },
  hdriPath: {
    type: String,
    default: '/textures/venice_sunrise_1k.hdr'
  },
  enableHDRI: {
    type: Boolean,
    default: true
  },
  lightIntensityMultiplier: {
    type: Number,
    default: 10
  },
  environmentExposure: {
    type: Number,
    default: 0.5
  },
  isOrthographic: {
    type: Boolean,
    default: true
  },
  orthoZoom: {
    type: Number,
    default: 10
  },
  windTurbineFlow: {
    type: Number,
    default: 1
  },
  solarPanelFlow: {
    type: Number,
    default: 1
  },
  batteryFlow: {
    type: Number,
    default: 1
  },
  consumptionFlow: {
    type: Number,
    default: 1
  },
  sphereSize: {
    type: Number,
    default: 0.05
  },
  sphereGlowIntensity: {
    type: Number,
    default: 2.0
  },
  propellerSpeed: {
    type: Number,
    default: 2.0 // Speed in radians per second
  }
});

const canvasRef = ref(null);
const isLoading = ref(true);
const error = ref(null);

let scene, renderer, activeCamera, controls, animationFrameId, clock;
let gltfSceneModel = null;
let propellerModel = null;
let actualPropeller = null; // Reference to the actual propeller mesh
let animatedSpheres = [];
let gsapTimelinesMap = new Map();

const paths = [
  {
    name: "Wind Turbine Path",
    flowPropName: 'windTurbineFlow',
    pointsBlender: {
      A: { x: -1.6837, y: 2.0619, z: 0 },
      B: { x: -0.19793, y: 2.0025, z: 0 },
      C: { x: -0.13797, y: 0.1481, z: 0 }
    }
  },
  {
    name: "Solar Panel Path",
    flowPropName: 'solarPanelFlow',
    pointsBlender: {
      A: { x: -1.6837, y: -2.0619, z: 0 },
      B: { x: -0.19793, y: -2.0025, z: 0 },
      C: { x: -0.13797, y: -0.1481, z: 0 }
    }
  },
  {
    name: "Battery Path",
    flowPropName: 'batteryFlow',
    pointsBlender: {
      A: { x: 1.6836, y: -2.0619, z: 0 },
      B: { x: 0.19793, y: -2.0025, z: 0 },
      C: { x: 0.13797, y: -0.1481, z: 0 }
    }
  },
  {
    name: "Consumption Path (Factory)",
    flowPropName: 'consumptionFlow',
    pointsBlender: {
      A: { x: 1.6836, y: 2.0619, z: 0 },
      B: { x: 0.19793, y: 2.0025, z: 0 },
      C: { x: 0.13797, y: 0.1481, z: 0 }
    }
  }
];

const convertBlenderToThree = (blenderCoords) => {
  return new THREE.Vector3(blenderCoords.x, blenderCoords.z, -blenderCoords.y);
};

const getCanvasDimensions = () => {
  if (canvasRef.value) {
    return {
      width: canvasRef.value.clientWidth,
      height: canvasRef.value.clientHeight,
    };
  }
  return { width: window.innerWidth, height: window.innerHeight };
};

const controlTimeline = (timelineName, flowValue) => {
  const timeline = gsapTimelinesMap.get(timelineName);
  if (!timeline) return;

  const { sphere, pointA, pointC } = timeline.vars.data;

  timeline.vars.onRepeat = () => {
    if (timeline.reversed()) {
      sphere.position.copy(pointC);
    } else {
      sphere.position.copy(pointA);
    }
  };

  if (flowValue === 0) {
    timeline.pause();
    sphere.visible = false;
  } else if (flowValue === 1) {
    sphere.visible = true;
    if (timeline.reversed() || timeline.progress() === 0 || timeline.progress() === 1) {
      timeline.reversed(false);
      timeline.play(0);
    } else {
      timeline.play();
    }
  } else if (flowValue === -1) {
    sphere.visible = true;
    if (!timeline.reversed() || timeline.progress() === 1 || timeline.progress() === 0) {
      timeline.reversed(true);
      timeline.reverse(0);
    } else {
      timeline.reverse();
    }
  }
};

const initThree = () => {
  if (!canvasRef.value) return;

  // Initialize the clock for delta time
  clock = new THREE.Clock();

  const { width, height } = getCanvasDimensions();
  const aspect = width / height;

  scene = new THREE.Scene();
  scene.background = null;

  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: true
  });

  renderer.setSize(width, height);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = props.environmentExposure;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x000000, 0);

  if (props.isOrthographic) {
    const frustumSize = 10;
    activeCamera = new THREE.OrthographicCamera(
      frustumSize * aspect / -2,
      frustumSize * aspect / 2,
      frustumSize / 2,
      frustumSize / -2,
      0.1,
      1000
    );
    activeCamera.zoom = props.orthoZoom;
    activeCamera.updateProjectionMatrix();
  } else {
    activeCamera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000);
  }

  activeCamera.position.set(
    props.cameraInitialPosition.x,
    props.cameraInitialPosition.y,
    props.cameraInitialPosition.z
  );

  controls = new OrbitControls(activeCamera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.screenSpacePanning = false;
  controls.minDistance = 0.1;
  controls.maxDistance = 100;

  if (props.isOrthographic) {
    controls.minZoom = 0.1;
    controls.maxZoom = 100;
  }

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.05);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(5, 10, 7.5);
  directionalLight.castShadow = true;
  directionalLight.shadow.mapSize.width = 2048;
  directionalLight.shadow.mapSize.height = 2048;
  scene.add(directionalLight);

  if (props.hdriPath && props.enableHDRI) {
    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    pmremGenerator.compileEquirectangularShader();

    new RGBELoader()
      .setPath('/')
      .load(props.hdriPath, (texture) => {
        const envMap = pmremGenerator.fromEquirectangular(texture).texture;
        scene.environment = envMap;
        texture.dispose();
        pmremGenerator.dispose();
      }, undefined, (err) => {});
  }

  // Load main model
  const mainModelLoader = new GLTFLoader();
  mainModelLoader.load(
    props.modelPath,
    (gltf) => {
      gltfSceneModel = gltf.scene;
      scene.add(gltfSceneModel);
      isLoading.value = false;

      gltfSceneModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
        if (child.isLight) {
          child.intensity *= props.lightIntensityMultiplier;
          child.castShadow = true;
        }
      });

      if (gltf.cameras && gltf.cameras.length > 0) {
        const glbOrthoCamera = gltf.cameras.find(cam => cam.isOrthographicCamera);
        if (glbOrthoCamera && props.isOrthographic) {
          activeCamera = glbOrthoCamera;
        } else {
          activeCamera = gltf.cameras[0] || activeCamera;
        }
      }

      const { width, height } = getCanvasDimensions();
      const newAspect = width / height;

      if (activeCamera.isPerspectiveCamera) {
        activeCamera.aspect = newAspect;
      } else if (activeCamera.isOrthographicCamera) {
        const frustumSize = 10;
        activeCamera.left = frustumSize * newAspect / -2;
        activeCamera.right = frustumSize * newAspect / 2;
        activeCamera.top = frustumSize / 2;
        activeCamera.bottom = frustumSize / -2;
        activeCamera.zoom = props.orthoZoom;
      }
      activeCamera.updateProjectionMatrix();

      controls.object = activeCamera;
      controls.update();

      // Create animated spheres
      const sphereRadius = props.sphereSize;
      const sphereMaterial = new THREE.MeshStandardMaterial({
        color: 0x00aaff,
        metalness: 0.8,
        roughness: 0.2,
        emissive: 0x0000ff,
        emissiveIntensity: props.sphereGlowIntensity
      });

      paths.forEach((pathConfig) => {
        const sphereGeometry = new THREE.SphereGeometry(sphereRadius, 32, 32);
        const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial.clone());
        sphere.castShadow = true;
        sphere.receiveShadow = true;
        scene.add(sphere);
        animatedSpheres.push(sphere);

        const pointA = convertBlenderToThree(pathConfig.pointsBlender.A);
        const pointB = convertBlenderToThree(pathConfig.pointsBlender.B);
        const pointC = convertBlenderToThree(pathConfig.pointsBlender.C);

        sphere.position.copy(pointA);
        sphere.visible = (props[pathConfig.flowPropName] !== 0);

        const timeline = gsap.timeline({
          repeat: -1,
          paused: true,
          data: { sphere, pointA, pointC }
        });

        timeline.to(sphere.position, { x: pointB.x, y: pointB.y, z: pointB.z, duration: 1 });
        timeline.to(sphere.position, { x: pointC.x, y: pointC.y, z: pointC.z, duration: 1 });

        gsapTimelinesMap.set(pathConfig.name, timeline);
        controlTimeline(pathConfig.name, props[pathConfig.flowPropName]);
      });
    },
    undefined,
    (err) => {
      error.value = 'Failed to load 3D model.';
      isLoading.value = false;
    }
  );

  // Load propeller model
  const propellerLoader = new GLTFLoader();
  propellerLoader.load(
    '/3D/proppeler.glb',
    (gltf) => {
      propellerModel = gltf.scene;
      
      // Debug: Log the propeller's structure
      console.log('Propeller model loaded:', propellerModel);
      console.log('Propeller position:', propellerModel.position);
      console.log('Propeller rotation:', propellerModel.rotation);
      
      // Find the actual propeller mesh
      propellerModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
          
          // Store reference to the propeller mesh
          // You might need to adjust this based on your model's naming
          if (child.name.toLowerCase().includes('propeller') || 
              child.name.toLowerCase().includes('blade') ||
              child.name.toLowerCase().includes('rotor') ||
              !actualPropeller) { // If no specific name, use the first mesh
            actualPropeller = child;
            console.log('Found propeller mesh:', child.name);
          }
        }
      });
      
      // If no specific mesh found, use the scene itself
      if (!actualPropeller) {
        actualPropeller = propellerModel;
      }
      
      scene.add(propellerModel);
    },
    undefined,
    (err) => {
      console.error('An error occurred while loading the propeller GLB model: ', err);
    }
  );

  const onWindowResize = () => {
    const { width, height } = getCanvasDimensions();
    const newAspect = width / height;

    if (activeCamera.isPerspectiveCamera) {
      activeCamera.aspect = newAspect;
    } else if (activeCamera.isOrthographicCamera) {
      const frustumSize = 10;
      activeCamera.left = frustumSize * newAspect / -2;
      activeCamera.right = frustumSize * newAspect / 2;
      activeCamera.top = frustumSize / 2;
      activeCamera.bottom = frustumSize / -2;
    }
    activeCamera.updateProjectionMatrix();
    renderer.setSize(width, height);
    controls.update();
  };

  window.addEventListener('resize', onWindowResize);

  const animate = () => {
    animationFrameId = requestAnimationFrame(animate);
    
    // Get delta time for smooth animation
    const deltaTime = clock.getDelta();

    // Animate the propeller - only when wind turbine is active
    if (actualPropeller && props.windTurbineFlow !== 0) {
      // Rotate on Z-axis (the one that worked for you)
      actualPropeller.rotation.z += props.propellerSpeed * deltaTime;
      
      // Optional: You can also make it spin backwards when windTurbineFlow is -1
      // actualPropeller.rotation.z += props.propellerSpeed * props.windTurbineFlow * deltaTime;
    }

    controls.update();
    renderer.render(scene, activeCamera);
  };
  
  animate();

  onBeforeUnmount(() => {
    window.removeEventListener('resize', onWindowResize);
    cancelAnimationFrame(animationFrameId);

    if (renderer) {
      renderer.dispose();
    }

    scene.clear();
    gltfSceneModel = null;
    propellerModel = null;
    actualPropeller = null;

    animatedSpheres.forEach(sphere => {
      if (sphere && sphere.geometry) sphere.geometry.dispose();
      if (sphere && sphere.material) sphere.material.dispose();
      scene.remove(sphere);
    });

    animatedSpheres = [];
    gsapTimelinesMap.forEach(timeline => timeline.kill());
    gsapTimelinesMap.clear();
  });
};

onMounted(() => {
  initThree();

  // Watch for flow changes
  paths.forEach(pathConfig => {
    watch(() => props[pathConfig.flowPropName], (newValue) => {
      controlTimeline(pathConfig.name, newValue);
    });
  });

  // Watch for glow intensity changes
  watch(() => props.sphereGlowIntensity, (newValue) => {
    animatedSpheres.forEach(sphere => {
      if (sphere.material && sphere.material.isMeshStandardMaterial) {
        sphere.material.emissiveIntensity = newValue;
      }
    });
  });
});
</script>