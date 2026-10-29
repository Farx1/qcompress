# 🧠 QCompress

[![CI](https://github.com/Farx1/qcompress/actions/workflows/ci.yml/badge.svg)](https://github.com/Farx1/qcompress/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Tensor-Train (TT-SVD) replacement of the linear layers of Hugging Face Transformers, with error bounds, property tests and a reproducible ratio-vs-perplexity benchmark.**

A quantum-inspired compression framework for neural networks (LLMs/Transformers) using Tensor-Train (TT) decomposition. I built this project to explore how tensor networks can compress large language models. The framework includes a real-time visualization dashboard, WebSocket streaming, and a modern Next.js interface with REST API.

## Quickstart

Library and benchmark only (no web app). Requires the benchmark script from #9 (and #2/#3 it builds on).

```bash
git clone https://github.com/Farx1/qcompress && cd qcompress
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python -m scripts.reproduce_compression --skip-real   # drop --skip-real to also run distilgpt2 + WikiText-2 (~350 MB download)
```

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

- **Tensor-Train Compression**: Replace Linear and Embedding layers with TT layers. Size reduction and accuracy depend on the chosen modes and ranks; no ratio has been measured on a trained checkpoint yet (see Status below).

- **Real-time Monitoring**: Watch compression metrics stream live through WebSocket connections. See compression ratios, parameter counts, and model sizes update in real-time as compression progresses.

- **Interactive Dashboard**: Use the Next.js dashboard to visualize compression results, compare original vs compressed models, and monitor multiple compression jobs simultaneously.

- **YAML Recipe System**: Define compression configurations declaratively using YAML files. Specify which layers to compress, TT modes, ranks, and penalty configurations.

- **Modern Web Interface**: Professional Next.js dashboard with i18n support (English/French), real-time updates, and intuitive user experience. Direct API calls also available for programmatic access.

- **Model Support**: Works with Hugging Face models including GPT-2, DistilGPT-2, and DialoGPT. Easy to extend to other transformer architectures.

- **Model Export**: Export compressed models in multiple formats (PyTorch `.pt`, SafeTensors `.safetensors`, ONNX `.onnx`) for deployment and sharing.

- **Professional UI**: Modern, polished interface with smooth animations, responsive design, and intuitive user experience built with Aceternity UI components.

### 🎯 Key Capabilities:

- **Dimension Validation**: Recipes are checked so that mode products match layer dimensions.
- **Entanglement Penalties**: Rényi / Shannon entropy of TT unfoldings, computed by a forward hook. The hook detaches the weights, so the penalty has no gradient and does not currently push ranks down.
- **TT-SVD Initialization**: Initialize TT cores from dense weights using truncated SVD for better starting points.
- **Caching Optimization**: Weight reconstruction is cached during evaluation to improve inference speed.
- **Multi-Format Export**: Export compressed models in PyTorch, SafeTensors, or ONNX formats with metadata for easy deployment.
- **Real-time Progress Tracking**: Live WebSocket updates with animated progress indicators and detailed metrics visualization.

## ⚠️ Status / known limitations

- **Backend does not use `qtc`**: `backend/compression_service.py` builds `TTLinear` / `TTEmbedding` directly with random cores (no recipe, no TT-SVD), and only for `nn.Linear` / `nn.Embedding`. GPT-2's `Conv1D` layers are skipped.
- **Benchmark runs on the original model**: `POST /api/benchmark/{job_id}` reloads the uncompressed model by name and evaluates that.
- **Chat is a stub**: `POST /api/chat` returns a fixed placeholder string.
- **Results page is mock data**: `frontend/app/[locale]/results/page.tsx` shows hard-coded numbers (Llama 2 7B, GLUE, SQuAD), not a job result.
- **SafeTensors export fails on tied weights** (e.g. GPT-2 `wte` / `lm_head`), because `save_file` rejects shared tensors.
- **Recipe engine (`src/qtc`)**: embedding modes must multiply exactly to the vocab size; there is no auto-padding (on `main` a mismatch hangs, fixed in #1). `init: ttsvd` / `copy` and HF `Conv1D` support are being fixed in PRs #2 and #3.
- **Measured so far** (with #3, random-init `GPT2Config(vocab_size=64, n_positions=16, n_embd=16, n_layer=1, n_head=2)`, wte + c_attn + c_fc + c_proj): full TT rank reproduces the logits (rel. err 4.8e-07) but uses 1.9x *more* parameters (7616 vs 3968); rank 8 gives 1.88x fewer parameters at 0.39 logits rel. err. No trained checkpoint has been measured.
- **Theory**: the TT-SVD error bound, the parameter-count formula and why full TT rank always uses more parameters than the dense matrix are in [docs/THEORY.md](docs/THEORY.md).

## 👩🏽‍🍳 The Process

I started by implementing the core Tensor-Train layers (`TTLinear` and `TTEmbedding`) in PyTorch. These layers decompose dense weight matrices into a series of smaller tensor cores, dramatically reducing parameter count. The forward pass reconstructs the full weight matrix on-the-fly using efficient einsum contractions.

Next, I built the compression framework (`qtc` module) that can automatically replace dense layers in Hugging Face models with TT layers based on YAML recipe files. This required careful module path resolution, dimension validation, and handling of wildcards for transformer blocks.

To enable real-time monitoring, I created a FastAPI backend with WebSocket support. The backend runs compression jobs asynchronously and streams metrics to connected clients. This allows users to watch compression progress live without polling.

For the frontend, I built a Next.js dashboard with React components for visualization. Using Recharts, I created real-time graphs showing compression ratios and parameter counts. The WebSocket client automatically reconnects and handles connection errors gracefully.

I also implemented an entanglement penalty system inspired by quantum information theory. It computes the Rényi entropy of high-rank unfoldings; wiring it into the training loss (it currently works on detached weights) is still to do.

Finally, I added error handling, dimension validation, and caching optimizations to make the system robust and performant. The entire architecture supports both programmatic API usage and interactive web interfaces.

## 📚 What I Learned

During this project, I've gained deep insights into tensor networks, neural network compression, and building real-time systems.

### 🧠 Tensor-Train Decomposition:

- **Mathematical Understanding**: I learned how TT decomposition factorizes high-dimensional tensors into a chain of lower-dimensional cores. Understanding the rank constraints (r₀ = rₑ = 1) and how modes are factored was crucial.

- **Einsum Mastery**: Working with `opt-einsum` to contract TT cores efficiently taught me about tensor algebra and how to optimize contraction paths. Building the einsum equation strings dynamically for different mode configurations was a great learning experience.

### 📏 Dimension Management:

- **Flexible Architecture**: I learned to handle dimension mismatches gracefully, especially for embeddings where vocab sizes don't always factor nicely.

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

## 📊 Results

Produced by `python -m scripts.reproduce_compression` (CPU, Python 3.11, torch 2.14.1, transformers 5.20.1); raw numbers in [`results/compression.json`](results/compression.json). SVD = truncated SVD of each weight with at most as many parameters as its TT replacement.

**Random-init GPT-2** `GPT2Config(vocab_size=256, n_positions=64, n_embd=64, n_layer=2, n_head=4)`, 3 seeds, mean ± std of the logits error.

| TT rank | TT ratio | TT logits rel. err | SVD ratio (equal params) | SVD logits rel. err |
|---|---|---|---|---|
| full | 0.93x | 9.99e-07 ± 3.1e-08 | 0.93x | 0.182 ± 0.0058 |
| 32 | 0.93x | 9.99e-07 ± 3.1e-08 | 0.93x | 0.182 ± 0.0058 |
| 16 | 1.56x | 0.445 ± 0.0066 | 1.56x | 0.427 ± 0.0078 |
| 8 | 5.47x | 0.555 ± 0.0036 | 5.76x | 0.553 ± 0.0024 |

**distilgpt2** (pretrained), perplexity on the first 4096 tokens of WikiText-2 (raw) test in 512-token chunks. Dense perplexity: 54.55.

| TT rank | TT ratio | TT logits rel. err | TT ppl | SVD ratio (equal params) | SVD logits rel. err | SVD ppl |
|---|---|---|---|---|---|---|
| full | 0.99x | 1.55e-06 | 54.55 | 0.99x | 0.267 | 245.71 |
| 32 | 9.22x | 1.02 | 5291.20 | 9.23x | 0.569 | 6970.42 |
| 16 | 34.81x | 0.801 | 3506.91 | 35.89x | 0.982 | 4086.28 |
| 8 | 119.81x | 0.8 | 3480.67 | 137.69x | 0.778 | 3606.38 |

TT on attn.c_attn, attn.c_proj, mlp.c_fc, mlp.c_proj of every block, d=3, TT-SVD init, no fine-tuning. Ratio = dense / compressed parameters of those layers (weights + biases).

Without fine-tuning, every truncated rank tested here destroys the pretrained model (perplexity in the thousands), for TT and for SVD alike; full TT rank is exact but compresses nothing (see docs/THEORY.md in #6). These are starting points for fine-tuning, not usable compressed models.

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
python -m pytest
```

## Citation

If you use QCompress, please cite it with the metadata in [`CITATION.cff`](CITATION.cff) (added in #8; GitHub shows a "Cite this repository" button once it is on `main`), and cite Oseledets (2011) for TT-SVD and Novikov et al. (2015) for TT layers (see [docs/THEORY.md](docs/THEORY.md)).

## 📄 License

MIT License

## 🙏 Acknowledgments

- Tensor-Train decomposition research (Oseledets, 2011)
- Hugging Face Transformers library
- FastAPI and Next.js communities
- Quantum-inspired compression research
