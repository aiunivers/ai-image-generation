import gradio as gr
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')
API_BASE = 'https://api.aiunivers.net/v2'

def wait(seconds):
    time.sleep(seconds)

def check_job_status(job_id):
    response = requests.post(
        f'{API_BASE}/jobId',
        headers={'X-API-KEY': API_KEY},
        json={'job': job_id}
    )
    return response.json()

def generate_headshot(prompt, image, canvas, negative_prompt, scheduler, seed, progress=gr.Progress()):
    headers = {'X-API-KEY': API_KEY}
    payload = {
        "prompt": prompt,
        "image": image,
        "canvas": canvas,
        "negative_prompt": negative_prompt,
        "scheduler": scheduler,
        "seed": int(seed)
    }
    try:
        response = requests.post(f'{API_BASE}/headshot', headers=headers, json=payload)
        task = response.json()
        while task['status'] in ['queued', 'generating']:
            progress(0.5, f"Status: {task['status']}")
            wait(5)
            task = check_job_status(task['job'])
        if task['status'] == 'succeeded':
            return [task['imageUrl'], None]
        else:
            return [None, f"Generation failed: {task['status']}"]
    except Exception as e:
        return [None, str(e)]

def generate_image(prompt, canvas, negative_prompt, scheduler, seed, progress=gr.Progress()):
    headers = {'X-API-KEY': API_KEY}
    payload = {
        "prompt": prompt,
        "canvas": canvas,
        "negative_prompt": negative_prompt,
        "scheduler": scheduler,
        "seed": int(seed)
    }
    try:
        response = requests.post(f'{API_BASE}/generate', headers=headers, json=payload)
        task = response.json()
        while task['status'] in ['queued', 'generating']:
            progress(0.5, f"Status: {task['status']}")
            wait(5)
            task = check_job_status(task['job'])
        if task['status'] == 'succeeded':
            return [task['imageUrl'], None]
        else:
            return [None, f"Generation failed: {task['status']}"]
    except Exception as e:
        return [None, str(e)]

def face_swap(source, target, progress=gr.Progress()):
    headers = {'X-API-KEY': API_KEY}
    payload = {
        "target_image": target,
        "swap_image": source
    }
    try:
        response = requests.post(f'{API_BASE}/faceswap', headers=headers, json=payload)
        task = response.json()
        while task['status'] in ['queued', 'processing']:
            progress(0.5, f"Status: {task['status']}")
            wait(5)
            task = check_job_status(task['job'])
        if task['status'] == 'succeeded':
            return [task['imageUrl'], None]
        else:
            return [None, f"Face swap failed: {task['status']}"]
    except Exception as e:
        return [None, str(e)]

# Gradio Interface
with gr.Blocks() as demo:
    with gr.Tabs():
        # Tab for Headshot Generation
        with gr.Tab("Headshot"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
                    image = gr.Textbox(label="Image Link", placeholder="Enter your Image Link...")
                    canvas = gr.Dropdown(
                        choices=["square", "portrait", "landscape"],
                        label="Canvas",
                        value="square"
                    )
                    with gr.Accordion("Advanced Options", open=False):
                        negative_prompt = gr.Textbox(label="Negative Prompt", placeholder="What to avoid in the image...")
                        scheduler = gr.Dropdown(
                            choices=["Euler a", "DPM++ SDE Karras", "Heun", "DPM++ 2M SDE Karras", "DPM++ 2M", "DDIM", "LMS", "PNDM", "UniPC"],
                            label="Scheduler",
                            value="DPM++ 2M SDE Karras"
                        )
                        seed = gr.Number(label="Seed (optional)", value=-1)
                    generate_btn = gr.Button("Generate Headshot")
                    error_output = gr.Textbox(label="Status/Error", interactive=False)
                with gr.Column():
                    output_image = gr.Image(label="Generated Image")
            generate_btn.click(
                fn=generate_headshot,
                inputs=[prompt, image, canvas, negative_prompt, scheduler, seed],
                outputs=[output_image, error_output]
            )

        # Tab for Image Generation
        with gr.Tab("Generate"):
            with gr.Row():
                with gr.Column():
                    prompt = gr.Textbox(label="Prompt", placeholder="Enter your prompt here...")
                    canvas = gr.Dropdown(
                        choices=["square", "portrait", "landscape"],
                        label="Canvas",
                        value="square"
                    )
                    with gr.Accordion("Advanced Options", open=False):
                        negative_prompt = gr.Textbox(label="Negative Prompt", placeholder="What to avoid in the image...")
                        scheduler = gr.Dropdown(
                            choices=["Euler a", "DPM++ SDE Karras", "Heun", "DPM++ 2M SDE Karras", "DPM++ 2M", "DDIM", "LMS", "PNDM", "UniPC"],
                            label="Scheduler",
                            value="DPM++ 2M SDE Karras"
                        )
                        seed = gr.Number(label="Seed (optional)", value=-1)
                    generate_btn = gr.Button("Generate Image")
                    error_output = gr.Textbox(label="Status/Error", interactive=False)
                with gr.Column():
                    output_image = gr.Image(label="Generated Image")
            generate_btn.click(
                fn=generate_image,
                inputs=[prompt, canvas, negative_prompt, scheduler, seed],
                outputs=[output_image, error_output]
            )

        # Face Swap Tab
        with gr.Tab("Face Swap"):
            with gr.Row():
                with gr.Column():
                    source = gr.Textbox(label="Source Image", placeholder="Source Image Link...")
                    target = gr.Textbox(label="Target Image", placeholder="Target Image Link...")
                    swap_btn = gr.Button("Swap Faces")
                    error_output = gr.Textbox(label="Status/Error", interactive=False)
                with gr.Column():
                    output_image = gr.Image(label="Face Swapped Image")
            swap_btn.click(
                fn=face_swap,
                inputs=[source, target],
                outputs=[output_image, error_output]
            )


if __name__ == "__main__":
    demo.launch(inbrowser=True)