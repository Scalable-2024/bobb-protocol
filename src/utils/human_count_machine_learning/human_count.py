# Written by Hrithika
import numpy as np
from PIL import Image
import tflite_runtime.interpreter as tflite

# Load TFLite model
def load_tflite_model(model_path):
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter

# Preprocess image to the required input size
def preprocess_image(image_path, input_size):
    image = Image.open(image_path).convert("RGB")  # Open image and ensure RGB format
    print(image.size)
    image = image.resize((input_size, input_size))  # Resize image
    input_image = np.array(image)

    input_image = np.expand_dims(input_image, axis=0)  # Add batch dimension
    return input_image, image

# Perform inference
def run_inference(interpreter, input_image):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], input_image)
    interpreter.invoke()

    # Retrieve outputs
    boxes = interpreter.get_tensor(output_details[0]['index'])[0]  # Bounding box coordinates
    classes = interpreter.get_tensor(output_details[1]['index'])[0]  # Class IDs
    scores = interpreter.get_tensor(output_details[2]['index'])[0]  # Confidence scores
    return boxes, classes, scores

# Count humans in the image
def count_humans(classes, scores, threshold=0.3):
    human_class_id = 0
    human_count = 0
    for i in range(len(classes)):
      if(classes[i] == human_class_id and scores[i] > threshold):
        human_count += 1
    return human_count


# Path to the TFLite model and test image
tflite_model_path = "efficientdet_lite3_512_ptq.tflite"
test_image_path = "flood.png"

# Load model and image
interpreter = load_tflite_model(tflite_model_path)
input_size = interpreter.get_input_details()[0]['shape'][1]  # Get model's input size
print(input_size)
input_image, original_image = preprocess_image(test_image_path, input_size)

# Run inference
boxes, classes, scores = run_inference(interpreter, input_image)

# Count humans
print(count_humans(classes, scores))
