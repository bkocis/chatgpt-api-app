import gradio as gr


def sketch_recognition(img):
    pass  # Implement your sketch recognition model here...


gr.Interface(fn=sketch_recognition, inputs="sketchpad", outputs="label").launch()
