import os
import base64
from django.shortcuts import render
from django.http import JsonResponse
from .utils import generate_chemistry_response, encode_image
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Conversation  # Import your Conversation model

# Ensure the images directory exists
images_dir = os.path.join(settings.BASE_DIR, 'images')
os.makedirs(images_dir, exist_ok=True)  # This line ensures the directory is created

def get_conversation(request):
    conversation = request.session.get("conversation", [])
    return JsonResponse({"conversation": conversation})

@csrf_exempt
def index(request):
    if request.method == "POST":
        print("Received POST request")  # Debugging statement
        user_input = request.POST.get("question", "").strip()
        image = request.FILES.get("image")

        # Retrieve conversation history from the request
        conversation = []
        for i in range(len(request.POST) // 2):  # Assuming each message has a role and content
            role = request.POST.get(f"conversation[{i}][role]")
            content = request.POST.get(f"conversation[{i}][content]")
            if role and content:
                conversation.append({"role": role, "content": content})

        print(f"User  input: {user_input}")  # Debugging statement
        print(f"Image received: {image is not None}")  # Debugging statement

        # Initialize variables
        bot_response = ""
        image_name = ""

        # Handle image input
        if image:
            print("Processing image...")  # Debugging statement
            base64_image = encode_image(image)
            image_name = f"image{len(os.listdir(images_dir)) + 1}.jpg"  # Create a unique image name
            image_path = os.path.join(images_dir, image_name)

            # Save the image to the directory
            with open(image_path, "wb") as img_file:
                img_file.write(base64.b64decode(base64_image))
            print(f"Image saved at: {image_path}")  # Debugging statement

            conversation.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            })
        elif user_input:
            conversation.append({"role": "user", "content": user_input})

        # Generate the assistant's response
        if conversation:
            response = generate_chemistry_response(conversation)
            bot_response = response
            conversation.append({"role": "assistant", "content": bot_response})

            # Save conversation to the database
            conversation_instance = Conversation.objects.create(
                user_question=user_input,
                bot_answer=bot_response,
                image_name=image_name
            )
            print(f"Conversation saved to database: {conversation_instance}")  # Debugging statement

            return JsonResponse({"response": bot_response})

    return render(request, "index.html")