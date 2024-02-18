import cv2
import numpy as np
import time

def on_blocks_per_row_change(val):
    global blocks_per_row, need_recalculation
    blocks_per_row = max(1, val)
    need_recalculation = True

def on_blocks_per_column_change(val):
    global blocks_per_column, need_recalculation
    blocks_per_column = max(1, val)
    need_recalculation = True

def on_shuffle_interval_change(val):
    global shuffle_interval
    shuffle_interval = val

def apply_color_shift(block, shift_range=100):
    shifts = np.random.randint(-shift_range, shift_range, (1, 1, 3))
    block_shifted = np.clip(block.astype(np.int16) + shifts, 0, 255).astype(np.uint8)
    return block_shifted

def divide_into_blocks(frame, blocks_per_row, blocks_per_column):
    block_height = frame.shape[0] // blocks_per_column
    block_width = frame.shape[1] // blocks_per_row
    blocks = []
    for i in range(blocks_per_column):
        for j in range(blocks_per_row):
            block = frame[i*block_height:(i+1)*block_height, j*block_width:(j+1)*block_width]
            blocks.append(block)
    return blocks

def generate_new_configuration(blocks_per_row, blocks_per_column):
    total_blocks = blocks_per_row * blocks_per_column
    new_order = np.random.permutation(total_blocks)
    return new_order

def apply_configuration(frame, blocks, new_order, blocks_per_row, blocks_per_column, color_shift=False):
    block_height = frame.shape[0] // blocks_per_column
    block_width = frame.shape[1] // blocks_per_row
    scrambled_frame = np.zeros_like(frame)
    for index, position in enumerate(new_order):
        dest_row = index // blocks_per_row
        dest_col = index % blocks_per_row
        
        block = blocks[position]
        
        if color_shift:
            block = apply_color_shift(block)
        
        scrambled_frame[dest_row*block_height:(dest_row+1)*block_height, dest_col*block_width:(dest_col+1)*block_width] = block
        
    return scrambled_frame

def on_color_shift_change(val):
    global color_shift
    color_shift = bool(val)

blocks_per_row = 8
blocks_per_column = 8
shuffle_interval = 5
color_shift = False
need_recalculation = True

cap = cv2.VideoCapture(0)

cv2.namedWindow('Scrambled Webcam Feed')
cv2.createTrackbar('Blocks per Row', 'Scrambled Webcam Feed', blocks_per_row, 20, on_blocks_per_row_change)
cv2.createTrackbar('Blocks per Column', 'Scrambled Webcam Feed', blocks_per_column, 20, on_blocks_per_column_change)
cv2.createTrackbar('Shuffle Interval (s)', 'Scrambled Webcam Feed', shuffle_interval, 30, on_shuffle_interval_change)
cv2.createTrackbar('Color Shift', 'Scrambled Webcam Feed', int(color_shift), 1, on_color_shift_change)  # 0 or 1

last_shuffle_time = time.time()
new_order = generate_new_configuration(blocks_per_row, blocks_per_column)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if need_recalculation:
        blocks = divide_into_blocks(frame, blocks_per_row, blocks_per_column)
        new_order = generate_new_configuration(blocks_per_row, blocks_per_column)
        need_recalculation = False

    current_time = time.time()
    if current_time - last_shuffle_time > shuffle_interval:
        new_order = generate_new_configuration(blocks_per_row, blocks_per_column)
        last_shuffle_time = current_time

    scrambled_frame = apply_configuration(frame, blocks, new_order, blocks_per_row, blocks_per_column, color_shift)

    cv2.imshow('Scrambled Webcam Feed', scrambled_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
