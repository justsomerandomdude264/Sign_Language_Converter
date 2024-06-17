from django.http import JsonResponse
from rest_framework.decorators import api_view
from .media_processing import convert_image_to_text, convert_video_to_text
import os

UPLOAD_DIR = 'media/uploads/'

@api_view(['POST'])
def upload_media(request):
    if 'media' not in request.FILES:
        return JsonResponse({'error': 'No media file provided.'}, status=400)

    media_file = request.FILES['media']
    file_extension = os.path.splitext(media_file.name)[1].lower()
    file_name = os.path.splitext(media_file.name)[0]

    upload_path = os.path.join(UPLOAD_DIR, media_file.name)

    try:
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Save the uploaded file to UPLOAD_DIR
        with open(upload_path, 'wb') as f:
            for chunk in media_file.chunks():
                f.write(chunk)

        # Process media file directly
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            detected_text = convert_image_to_text(upload_path)
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            detected_text = convert_video_to_text(upload_path)
        else:
            return JsonResponse({'error': 'Unsupported file type.'})

        # Delete the file from server after processing
        os.remove(upload_path)

        return JsonResponse({'message': 'Media processed successfully.', 'text': detected_text})

    except Exception as e:
        # If any error occurs, delete the file if it was saved
        if os.path.exists(upload_path):
            os.remove(upload_path)
        return JsonResponse({'error': str(e)}, status=500)
