# 🧠 QCompress

A quantum-inspired compression framework for neural networks (LLMs/Transformers) using Tensor-Train (TT) decomposition. I built this project to explore how tensor networks can compress large language models while maintaining performance. The framework includes a real-time visualization dashboard, WebSocket streaming, and a modern Next.js interface with REST API.

## 📦 Technologies

- `Python 3.9+`
- `PyTorch`
- `FastAPI`
- `Next.js 15`
- `React 19`
- `TypeScript`
- `Framer Motion` - Professional animations
- `Aceternity UI` - Modern component library
- `Lucide React` - Icon library
- `WebSockets`
- `Recharts`
- `Pydantic`
- `Opt-Einsum`
- `Pytest`

## 🦄 Features

Here's what you can do with QCompress:

- **Tensor-Train Compression**: Compress Linear and Embedding layers using TT decomposition, reducing model size by 5-10x while maintaining performance.

- **Real-time Monitoring**: Watch compression metrics stream live through WebSocket connections. See compression ratios, parameter counts, and model sizes update in real-time as compression progresses.

- **Interactive Dashboard**: Use the Next.js dashboard to visualize compression results, compare original vs compressed models, and monitor multiple compression jobs simultaneously.

- **YAML Recipe System**: Define compression configurations declaratively using YAML files. Specify which layers to compress, TT modes, ranks, and penalty configurations.

- **Modern Web Interface**: Professional Next.js dashboard with i18n support (English/French), real-time updates, and intuitive user experience. Direct API calls also available for programmatic access.

- **Model Support**: Works with Hugging Face models including GPT-2, DistilGPT-2, and DialoGPT. Easy to extend to other transformer architectures.

- **Chat Interface**: Test compressed models interactively. Compare responses from original and compressed models side-by-side with generation time metrics.

- **Model Export**: Export compressed models in multiple formats (PyTorch `.pt`, SafeTensors `.safetensors`, ONNX `.onnx`) for deployment and sharing.

- **Professional UI**: Modern, polished interface with smooth animations, responsive design, and intuitive user experience built with Aceternity UI components.

### 🎯 Key Capabilities:

- **Automatic Dimension Validation**: The system automatically validates and adjusts TT mode configurations to match layer dimensions.
- **Entanglement Penalties**: Control compression using Rényi entropy and Shannon entropy penalties to push ranks down.
- **TT-SVD Initialization**: Initialize TT cores from dense weights using truncated SVD for better starting points.
- **Caching Optimization**: Weight reconstruction is cached during evaluation to improve inference speed.
- **Multi-Format Export**: Export compressed models in PyTorch, SafeTensors, or ONNX formats with metadata for easy deployment.
- **Real-time Progress Tracking**: Live WebSocket updates with animated progress indicators and detailed metrics visualization.

## 👩🏽‍🍳 The Process

I started by implementing the core Tensor-Train layers (`TTLinear` and `TTEmbedding`) in PyTorch. These layers decompose dense weight matrices into a series of smaller tensor cores, dramatically reducing parameter count. The forward pass reconstructs the full weight matrix on-the-fly using efficient einsum contractions.

Next, I built the compression framework (`qtc` module) that can automatically replace dense layers in Hugging Face models with TT layers based on YAML recipe files. This required careful module path resolution, dimension validation, and handling of wildcards for transformer blocks.

To enable real-time monitoring, I created a FastAPI backend with WebSocket support. The backend runs compression jobs asynchronously and streams metrics to connected clients. This allows users to watch compression progress live without polling.

For the frontend, I built a Next.js dashboard with React components for visualization. Using Recharts, I created real-time graphs showing compression ratios and parameter counts. The WebSocket client automatically reconnects and handles connection errors gracefully.

I also implemented an entanglement penalty system inspired by quantum information theory. By penalizing high-rank unfoldings using Rényi entropy, the system encourages lower-rank decompositions during training.

Finally, I added comprehensive error handling, dimension auto-adjustment for embeddings, and caching optimizations to make the system robust and performant. The entire architecture supports both programmatic API usage and interactive web interfaces.

## 📚 What I Learned

During this project, I've gained deep insights into tensor networks, neural network compression, and building real-time systems.

### 🧠 Tensor-Train Decomposition:

- **Mathematical Understanding**: I learned how TT decomposition factorizes high-dimensional tensors into a chain of lower-dimensional cores. Understanding the rank constraints (r₀ = rₑ = 1) and how modes are factored was crucial.

- **Einsum Mastery**: Working with `opt-einsum` to contract TT cores efficiently taught me about tensor algebra and how to optimize contraction paths. Building the einsum equation strings dynamically for different mode configurations was a great learning experience.

### 📏 Dimension Management:

- **Flexible Architecture**: I learned to handle dimension mismatches gracefully, especially for embeddings where vocab sizes don't always factor nicely. Implementing auto-padding and trimming taught me about robust system design.

- **Validation Logic**: Creating the recipe validator required understanding model architectures deeply. Checking that mode products match layer dimensions and that ranks are valid required careful mathematical reasoning.

### 🎨 Real-time Systems:

- **WebSocket Architecture**: Building the WebSocket manager taught me about connection lifecycle management, broadcasting to multiple clients, and handling disconnections gracefully. The reconnection logic with exponential backoff was particularly interesting.

- **Async Python**: Using FastAPI's async capabilities and running compression in thread pools helped me understand when to use async vs sync code, especially for CPU-bound operations like model loading.

### ✏️ React and Next.js:

- **Modern React Patterns**: Working with Next.js 15 App Router, React Query for data fetching, and Zustand for state management taught me about modern React best practices. The component architecture with separation of concerns was valuable.

- **TypeScript Integration**: Creating comprehensive type definitions for the API and WebSocket messages improved code safety and developer experience. Learning to type async operations and WebSocket events was particularly useful.

### 🎣 Performance Optimization:

- **Caching Strategies**: Implementing weight caching in TT layers (only in eval mode) taught me about memory vs computation tradeoffs. Understanding when to cache and when to recompute is crucial for performance.

- **Model Loading**: Learning to cache loaded models in the backend service to avoid reloading for multiple compression jobs was important for efficiency.

### 📈 Overall Growth:

This project helped me understand the intersection of quantum-inspired algorithms, deep learning, and modern web development. It was more than just implementing compression—it was about building a complete system from mathematical foundations to user interfaces, with real-time capabilities and robust error handling.

## 💭 How can it be improved?

- **Efficient Contractions**: Replace full weight reconstruction with direct TT contractions to avoid materializing the full matrix, significantly improving speed for large models.

- **MPO Support**: Add Matrix Product Operator (MPO) decomposition for attention layers, not just Linear and Embedding layers.

- **Automatic Rank Search**: Implement Optuna-based hyperparameter search to automatically find optimal TT ranks and modes under memory/latency constraints.

- **More Model Architectures**: Extend support to BERT, T5, and other transformer variants beyond GPT-2 family.

- **Quantization Integration**: Combine TT compression with quantization techniques for even greater compression ratios.

- **Training Integration**: Add fine-tuning capabilities to recover performance after compression using the entanglement penalties.

- **Visual Recipe Builder**: Create a GUI for building compression recipes instead of manually writing YAML files.

- **Batch Compression**: Support compressing multiple models or layers in parallel for faster experimentation.

- **Performance Profiling**: Add detailed profiling to compare dense vs TT layer performance across different hardware.

- **Export Formats**: Support exporting compressed models to ONNX or other formats for deployment.

## 🚦 Running the Project

To run the project in your local environment, follow these steps:

1. **Clone the repository** to your local machine.

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

3. **Install frontend dependencies:**
```bash
cd frontend
npm install
cd ..
```

4. **Start everything with one command:**

**On Windows (PowerShell):**
```powershell
.\start.ps1
```

**On Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Or manually start each service:**

Start the FastAPI backend (in one terminal):
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Start the Next.js frontend (in another terminal):
```bash
cd frontend
npm run dev
```

5. **Access the application:**
   - Frontend Dashboard: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Exporting Models

After completing a compression job, you can export the compressed model in multiple formats:

1. **Via UI**: Click the "Export Model" button in the Compression Monitor after a job completes
2. **Via API**: Use the export endpoints:
   ```bash
   # PyTorch format
   curl http://localhost:8000/api/jobs/{job_id}/export/pytorch -o model.pt
   
   # SafeTensors format
   curl http://localhost:8000/api/jobs/{job_id}/export/safetensors -o model.safetensors
   
   # ONNX format
   curl http://localhost:8000/api/jobs/{job_id}/export/onnx -o model.onnx
   ```

**Note**: SafeTensors and ONNX exports require additional packages:
```bash
pip install safetensors  # For SafeTensors export
pip install onnx        # For ONNX export
```

### Quick Test

Test the compression with a simple API call:

```bash
curl -X POST http://localhost:8000/api/compress \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "distilgpt2",
    "compression_configs": {
      "lm_head": {
        "in_modes": [768],
        "out_modes": [50257],
        "ranks": [1, 1]
      }
    }
  }'
```

## 📖 Example Recipe

Create a YAML file (e.g., `examples/gpt2_tt.yaml`) to define compression:

```yaml
model: gpt2
seed: 42
budget: 10x

targets:
  - path: transformer.wte
    decomp: TT
    in_modes: [17, 17, 17, 10]
    out_modes: [16, 16, 3]
    ranks: [1, 16, 16, 1]
    init: random
    penalty:
      type: renyi
      alpha: 2.0
      lambda: 1.0e-4
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/
```

## 📄 License

MIT License

## 🙏 Acknowledgments

- Tensor-Train decomposition research (Oseledets, 2011)
- Hugging Face Transformers library
- FastAPI and Next.js communities
- Quantum-inspired compression research
