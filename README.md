# Chandra

Chandra is a highly accurate OCR model that converts images and PDFs into structured HTML/Markdown/JSON while preserving layout information.

## Features

- Convert documents to markdown, html, or json with detailed layout information
- Good handwriting support
- Reconstructs forms accurately, including checkboxes
- Good support for tables, math, and complex layouts
- Extracts images and diagrams, with captions and structured data
- Support for 40+ languages
- Two inference modes: local (HuggingFace) and remote (vLLM server)

## Hosted API

- We have a hosted API for Chandra [here](https://www.datalab.to/), which also includes other accuracy improvements and document workflows.
- There is a free playground [here](https://www.datalab.to/playground) if you want to try it out without installing.

## Quickstart

The easiest way to start is with the CLI tools:

```shell
pip install chandra-ocr

# With VLLM
chandra_vllm
chandra input.pdf ./output

# With HuggingFace
chandra input.pdf ./output --method hf

# Interactive streamlit app
chandra_app
```

## Benchmarks

These are overall scores on the olmocr bench.

<img src="assets/benchmarks/bench.png" width="600px"/>

See full scores [below](#benchmark-table).

## Examples

<img src="assets/examples/forms/handwritten_form.png" width="600px"/>

| Type | Name | Link |
|------|------|------|
| Tables | Water Damage Form | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/tables/water_damage.png) |
| Tables | 10K Filing | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/tables/10k.png) |
| Forms | Handwritten Form | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/forms/handwritten_form.png) |
| Forms | Lease Agreement | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/forms/lease.png) |
| Handwriting | Doctor Note | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/handwriting/doctor_note.png) |
| Handwriting | Math Homework | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/handwriting/math_hw.png) |
| Books | Geography Textbook | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/books/geo_textbook_page.png) |
| Books | Exercise Problems | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/books/exercises.png) |
| Math | Attention Diagram | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/math/attn_all.png) |
| Math | Worksheet | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/math/worksheet.png) |
| Math | EGA Page | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/math/ega.png) |
| Newspapers | New York Times | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/newspapers/nyt.png) |
| Newspapers | LA Times | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/newspapers/la_times.png) |
| Other | Transcript | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/other/transcript.png) |
| Other | Flowchart | [View](https://github.com/datalab-to/chandra/blob/master/assets/examples/other/flowchart.png) |

## Community

[Discord](https://discord.gg//KuZwXNGnfH) is where we discuss future development.

## Installation

### Package

```bash
pip install chandra-ocr
```

If you're going to use the huggingface method, we also recommend installing [flash attention](https://github.com/Dao-AILab/flash-attention).

### From Source

```bash
git clone https://github.com/datalab-to/chandra.git
cd chandra
uv sync
source .venv/bin/activate
```

## Usage

### CLI

Process single files or entire directories:

```bash
# Single file, with vllm server (see below for how to launch vllm)
chandra input.pdf ./output --method vllm

# Process all files in a directory with local model
chandra ./documents ./output --method hf
```

**CLI Options:**
- `--method [hf|vllm]`: Inference method (default: vllm)
- `--page-range TEXT`: Page range for PDFs (e.g., "1-5,7,9-12")
- `--max-output-tokens INTEGER`: Max tokens per page
- `--max-workers INTEGER`: Parallel workers for vLLM
- `--include-images/--no-images`: Extract and save images (default: include)
- `--include-headers-footers/--no-headers-footers`: Include page headers/footers (default: exclude)
- `--batch-size INTEGER`: Pages per batch (default: 1)

**Output Structure:**

Each processed file creates a subdirectory with:
- `<filename>.md` - Markdown output
- `<filename>.html` - HTML output
- `<filename>_metadata.json` - Metadata (page info, token count, etc.)
- `images/` - Extracted images from the document

### Streamlit Web App

Launch the interactive demo for single-page processing:

```bash
chandra_app
```

### REST API

Start the REST API server for integration with bots and applications:

```bash
chandra_api
```

The API runs on `http://localhost:5000` by default. Available endpoints:

- `GET /api/health` - Health check
- `POST /api/ocr` - Process file (image or PDF)
- `POST /api/ocr/image` - Process image from base64

**API Authentication (Optional):**

To enable API key authentication, set environment variables:

```bash
CHANDRA_API_KEY=your_secret_key_here
CHANDRA_REQUIRE_API_KEY=true
```

The API key can be sent via:
- Header: `Authorization: Bearer <key>` or `Authorization: <key>`
- Query parameter: `?api_key=<key>`
- Form data: `api_key=<key>`
- JSON body: `{"api_key": "<key>"}`

**Deployment:**

For Railway deployment, the `railway.toml` is already configured. Set environment variables in Railway:
- `CHANDRA_API_KEY` (optional, for authentication)
- `CHANDRA_REQUIRE_API_KEY=true` (optional, to enable auth)
- `PORT` (automatically set by Railway)

### vLLM Server (Optional)

For production deployments or batch processing, use the vLLM server:

```bash
chandra_vllm
```

This launches a Docker container with optimized inference settings. Configure via environment variables:

- `VLLM_API_BASE`: Server URL (default: `http://localhost:8000/v1`)
- `VLLM_MODEL_NAME`: Model name for the server (default: `chandra`)
- `VLLM_GPUS`: GPU device IDs (default: `0`)

You can also start your own vllm server with the `datalab-to/chandra` model.

### Configuration

Settings can be configured via environment variables or a `local.env` file:

```bash
# Model settings
MODEL_CHECKPOINT=datalab-to/chandra
MAX_OUTPUT_TOKENS=8192

# vLLM settings
VLLM_API_BASE=http://localhost:8000/v1
VLLM_MODEL_NAME=chandra
VLLM_GPUS=0

# API authentication (optional)
CHANDRA_API_KEY=your_secret_key_here
CHANDRA_REQUIRE_API_KEY=false
```

### Railway Deployment (API + Local GPU)

Deploy the lightweight HTTP API on Railway while keeping the GPU-heavy vLLM server on your own machine (or any other GPU host):

1. **Run inference where you have GPU access**  
   Launch `chandra_vllm` (or `python -m chandra.scripts.vllm`) on your GPU box and expose it with Cloudflare Tunnel or any secure reverse proxy. Note the public URL (e.g. `https://tu-tunel.cloudflareclient.com/v1`).

2. **Deploy the API on Railway**  
   - Railway reads `railway.toml` and will run `python -m chandra.scripts.run_api`, automatically binding to the provided `$PORT`.  
   - Set the following Railway variables so the API knows how to reach your remote vLLM server:
     - `VLLM_API_BASE` → URL of your tunnel/public endpoint  
     - `VLLM_API_KEY` → token if your tunnel or server requires one (`EMPTY` otherwise)  
     - Optional: `MODEL_CHECKPOINT`, `MAX_OUTPUT_TOKENS`, `TORCH_DEVICE=cpu`, `TORCH_ATTN`, `BBOX_SCALE`, `IMAGE_DPI`, `MIN_PDF_IMAGE_DIM`, `MIN_IMAGE_DIM` to mirror your `local.env` defaults.

3. **Test the flow**  
   From your laptop or bot, call the Railway URL (`https://<app>.up.railway.app/api/ocr`). Railway forwards the request to your GPU-backed vLLM server, which returns the OCR output without exposing your home network directly.

This split keeps GPU costs off Railway while still providing a stable, internet-facing API endpoint.

# Commercial usage

This code is Apache 2.0, and our model weights use a modified OpenRAIL-M license (free for research, personal use, and startups under $2M funding/revenue, cannot be used competitively with our API). To remove the OpenRAIL license requirements, or for broader commercial licensing, visit our pricing page [here](https://www.datalab.to/pricing?utm_source=gh-chandra).

# Benchmark table

| **Model**                 |  ArXiv   | Old Scans Math |  Tables  | Old Scans | Headers and Footers | Multi column | Long tiny text | Base |    Overall     | Source |
|:--------------------------|:--------:|:--------------:|:--------:|:---------:|:-------------------:|:------------:|:--------------:|:----:|:--------------:|:------:|
| Datalab Chandra v0.1.0    |   82.2   | **80.3** | **88.0** | **50.4**  |        90.8         |     81.2     |    **92.3**    | **99.9** | **83.1 ± 0.9** | Own benchmarks |
| Datalab Marker v1.10.0    | **83.8** | 69.7 |   74.8   |   32.3    |        86.6         |     79.4     |      85.7      | 99.6 |   76.5 ± 1.0   | Own benchmarks |
| Mistral OCR API           |   77.2   | 67.5 |   60.6   |   29.3    |        93.6         |     71.3     |      77.1      | 99.4 |   72.0 ± 1.1   | olmocr repo |
| Deepseek OCR              |   75.2   | 72.3 |   79.7   |   33.3    |        96.1         |     66.7     |      80.1      | 99.7 |   75.4 ± 1.0   | Own benchmarks |
| GPT-4o (Anchored)         |   53.5   | 74.5 |   70.0   |   40.7    |        93.8         |     69.3     |      60.6      | 96.8 |   69.9 ± 1.1   | olmocr repo |
| Gemini Flash 2 (Anchored) |   54.5   | 56.1 |   72.1   |   34.2    |        64.7         |     61.5     |      71.5      | 95.6 |   63.8 ± 1.2   | olmocr repo |
| Qwen 3 VL 8B              |   70.2   | 75.1 |   45.6   |   37.5    |        89.1         |     62.1     |      43.0      | 94.3 |   64.6 ± 1.1   | Own benchmarks |
| olmOCR v0.3.0             |   78.6   | 79.9 |   72.9   |   43.9    |      **95.1**       |     77.3     |      81.2      | 98.9 |   78.5 ± 1.1   | olmocr repo |
| dots.ocr                  |   82.1   | 64.2 |   88.3   |   40.9    |        94.1         |   **82.4**   |      81.2      | 99.5 |   79.1 ± 1.0   | dots.ocr repo |


# Credits

Thank you to the following open source projects:

- [Huggingface Transformers](https://github.com/huggingface/transformers)
- [VLLM](https://github.com/vllm-project/vllm)
- [olmocr](github.com/allenai/olmocr)
- [Qwen 3 VL](https://github.com/QwenLM/Qwen3)