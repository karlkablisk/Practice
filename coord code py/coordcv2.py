import cv2

# Initialize the starting and ending points of the rectangle
start_point = None
end_point = None
drawing = False

# Function to handle mouse events
def click_event(event, x, y, flags, param):
    global start_point, end_point, drawing
    
    # Check if the left mouse button is pressed down
    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True

    # Check if the mouse is being moved while the left button is pressed
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)
            img_copy = img.copy()
            cv2.rectangle(img_copy, start_point, end_point, (255, 0, 0), 2)
            cv2.imshow('image', img_copy)

    # Check if the left mouse button is released
    elif event == cv2.EVENT_LBUTTONUP:
        end_point = (x, y)
        drawing = False
        cv2.rectangle(img, start_point, end_point, (255, 0, 0), 2)
        cv2.imshow('image', img)
        print(f"Rectangle drawn from {start_point} to {end_point}")

# Driver function
if __name__ == "__main__":

    # Read the image
    img = cv2.imread('lena.jpg', 1)

    # Display the image
    cv2.imshow('image', img)

    # Set mouse handler for the image and call the click_event() function
    cv2.setMouseCallback('image', click_event)

    # Wait for a key to be pressed to exit
    cv2.waitKey(0)

    # Close the window
    cv2.destroyAllWindows()
