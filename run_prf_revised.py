from psychopy import visual, event, core, gui
from psychopy.visual import textbox
import psychopy
import time
import numpy as np
import os
import re
import random
import datetime
import csv
import socket


## >>> define functions
def list_files_recursive(path='.'):
    image_list = []
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            image_list.extend(list_files_recursive(full_path))  # Collect files recursively
        else:
            if (full_path[-4:] == '.png') or (full_path[-4:] == '.jpg'):
                image_list.append(full_path)  # Append file path
    return image_list
    
def get_image_number(filename):
    """Extracts the image number from the filename."""
    match = re.search(r'-(\d+)_', filename)  # Matches the number after '-' and before '_'
    if match:
        return int(match.group(1))
    else:
        return 0  # Handle cases where the number isn't found
        
def wait_for_scanner(trigger, offset = 0):
    ### >>> wait for scanner >>>
    #        k1 = keyboard.Keyboard()
    event.waitKeys(keyList=[trigger])
    triggerTime = clock.getTime() - offset
    #        keyPressed = k1.getKeys()[0]
    print(f'Trigger sent ({trigger})')
    ### <<< wait for scanner <<<
    return triggerTime
## <<< define functions

## >>> define variables
use_mock_scanner = False
fullscr_bool = True
use_frames_for_timing = False#True
window_size = [1920, 1200]
trigger = '5'
TR = 2.5
contrast_reverse_rate = 8 # Hz
nr_TRs_per_stim = 4
#nr_blocks = 1

fixation_with = 10
fixation_colour = 'red'
background_color = 'gray'
stim_size_param = 2
#stim_size_pix = window_size[1]# - 50
#print(1,stim_size_pix)

shuffle_imgs = False
## <<< define variables

 
##################### get subject/run information
myDlg = gui.Dlg(title="LGN PRF experiment")
myDlg.addText('Subject info')
myDlg.addField('Subject Nr:', required=True)
myDlg.addField('Run:', required=True)
myDlg.addText('Experiment Settings')
myDlg.addField('Blocks:', 4, required=True)
myDlg.addField('Type:', "eccentricity-ring", choices=["fixed-bar", "log-bar", "eccentricity-ring", "log-eccentricity-ring"])
run_data = myDlg.show()  # show dialog and wait for OK or Cancel
if not myDlg.OK:  # or if ok_data is not None
    print('User cancelled session')
    # Quit PsychoPy
    core.quit()


if '2023' in str(psychopy.__version__):
    print('Using 2023 compatibility')
    sub_nr = run_data[0]#run_data['Subject Nr:']
    run_nr = run_data[1]#run_data['Run:']
    nr_blocks = run_data[2]#np.int64(run_data['Blocks:'])
    condition_name = run_data[3] #run_data['Type:']
else:
    print('Using current state')
    sub_nr = run_data['Subject Nr:']
    run_nr = run_data['Run:']
    nr_blocks = np.int64(run_data['Blocks:'])
    condition_name = run_data['Type:']
#####################


## >>> Mock scanner
#import socket

def start_scanner(host = "127.0.0.1", port = 2333):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(b"Start")
if use_mock_scanner:
    if __name__ == "__main__":
        start_scanner()
## <<< Mock scanner



if condition_name == "fixed-bar":
    image_list = list_files_recursive('./stimuli/fixed-bar/')
    image_list_flip = list_files_recursive('./stimuli/fixed-bar-flipped/')
elif condition_name == "eccentricity-ring":
    image_list = list_files_recursive('./stimuli/eccec_rings/')
    image_list_flip = list_files_recursive('./stimuli/eccec_rings_flipped/')
elif condition_name == "log-eccentricity-ring":
    image_list = list_files_recursive('./stimuli/log_eccec_rings/')
    image_list_flip = list_files_recursive('./stimuli/log_eccec_rings_flipped/')
else:
    image_list = list_files_recursive('./stimuli/log-bar/')
    image_list_flip = list_files_recursive('./stimuli/log-bar-flipped/')

# sort image list
if ((condition_name == "eccentricity-ring") or (condition_name == "log-eccentricity-ring")):
    image_list = sorted(image_list)
    image_list_flip = sorted(image_list_flip)
else:    
    image_list = sorted(image_list, key=get_image_number)
    image_list_flip = sorted(image_list_flip, key=get_image_number)

# create window
win = visual.Window(window_size, color=background_color, units='pix', fullscr = fullscr_bool, screen=0)
#stim_size_pix = (win.size[1]/2) * 0.999 # CHECK FOR SCANNER!
stim_size_pix = np.int64(win.size[1]/2) #* 0.999
print(1,stim_size_pix)
#print(3,psychoJS.window.size[1])

refresh_rate = win.getActualFrameRate()
if refresh_rate is None:
    print(f"Refresh rate: NONE!")
    refresh_rate = 60  # fallback
print(f"Refresh rate: {refresh_rate:.2f} Hz")

frame_reverse = refresh_rate/contrast_reverse_rate # variable assignment

fixation_cross = visual.ShapeStim(
    win, vertices=((0, -10), (0, 10), (0, 0), (-10, 0), (10, 0)),
    lineWidth=fixation_with, closeShape=False, lineColor=fixation_colour
)
fixation_cross.size *= stim_size_param # change size of fixation cross
# draw fixation cross
fixation_cross.draw()
win.flip()

# start clock
clock = core.Clock()

# wait for first trigger
offset = 0
triggerTime = wait_for_scanner(trigger, offset)
offset = triggerTime
triggerTime_log = 0
## log start
log_arr = np.array([[triggerTime_log, '', '', "T", ""]], dtype='object')

# wait for 4 more triggers
curr_trig = 0
while curr_trig < 4:
    triggerTime = wait_for_scanner(trigger, offset)
    ## log start
    new_row = np.array([[triggerTime, '', '', "T", ""]], dtype='object')
    log_arr = np.vstack([log_arr, new_row])
    curr_trig += 1


if not((condition_name == "eccentricity-ring") or (condition_name == "log-eccentricity-ring")):
    block_size = 45

    image_list_blocks = [image_list[i:i+block_size] for i in range(0, len(image_list), block_size)]
    image_list_flip_blocks = [image_list_flip[i:i+block_size] for i in range(0, len(image_list_flip), block_size)]

    image_paired_blocks = list(zip(image_list_blocks, image_list_flip_blocks))
else:
    if nr_blocks%2 == 0:
        block_select = np.hstack([np.zeros(np.int64(nr_blocks/2)),(np.zeros(np.int64(nr_blocks/2))+1)])
        np.random.shuffle(block_select)
    # counterbalance

for blk in range(0,nr_blocks):
    new_row = np.array([clock.getTime() - offset, str(blk+1), '', "Block onset", ''], dtype='object')
    log_arr = np.vstack([log_arr, new_row])
    
    if shuffle_imgs and not((condition_name == "eccentricity-ring") or (condition_name == "log-eccentricity-ring")):
        # shuffle blocks
        random.shuffle(image_paired_blocks)
        
        # set new lists
        image_list = [item for block, _ in image_paired_blocks for item in block]
        image_list_flip = [item for _, block in image_paired_blocks for item in block]
    elif shuffle_imgs and ((condition_name == "eccentricity-ring") or (condition_name == "log-eccentricity-ring")):
        if nr_blocks%2 == 0:
            reverse_choice = np.int64(block_select[blk])
        else:
            reverse_choice = random.choice([0,1])
        if reverse_choice == 1:
            image_list.reverse()
            image_list_flip.reverse()
    if not shuffle_imgs and blk>0:
        image_list.reverse()
        image_list_flip.reverse()

    frame_n = 0 # current frame nr
    flip_bol = True # var whether to flip contrast
    
    # pre allocate image
    stim1 = visual.ImageStim(win, image=image_list[0], units='pix', pos=[0, 0], size=[stim_size_pix,stim_size_pix])
    stim2 = visual.ImageStim(win, image=image_list_flip[0], units='pix', pos=[0, 0], size=[stim_size_pix,stim_size_pix])
    
    # go through images
    for img_idx in range(len(image_list)):
        stim1.image = image_list[img_idx]
        stim2.image = image_list_flip[img_idx]
        
        if use_frames_for_timing: # use frames for timing
            # logging
            img_name = image_list[img_idx][6+len(condition_name):] # take only relative image name
            new_row = np.array([clock.getTime() - offset, str(blk+1), str(img_idx+1), "Stimulus", img_name], dtype='object')
            log_arr = np.vstack([log_arr, new_row])
            for frame_n in range(int(refresh_rate*nr_TRs_per_stim*TR)):
                if frame_n % frame_reverse < 1:     # time to toggle?
                    flip_bol = not flip_bol
                if flip_bol:
                    stim1.draw()
                    img_name = image_list[img_idx]
                else:
                    stim2.draw()
                    img_name = image_list_flip[img_idx]
                fixation_cross.draw()
                win.flip()
                
        else: # use time for timing
            time_per_stim = 1
            start_time = clock.getTime()
            # logging
            img_name = image_list[img_idx][6+len(condition_name):] # take only relative image name
            new_row = np.array([clock.getTime() - offset, str(blk+1), str(img_idx+1), "Stimulus", img_name], dtype='object')
            log_arr = np.vstack([log_arr, new_row])
            while clock.getTime() < start_time+(time_per_stim*TR*nr_TRs_per_stim):
                flick_time = clock.getTime()
                if flip_bol:
                    stim1.draw()
                    img_name = image_list[img_idx]
                else:
                    stim2.draw()
                    img_name = image_list_flip[img_idx]
                
                fixation_cross.draw()
                win.flip()
                
                # decide how long to let flicker stay
                time2flicker = time_per_stim/contrast_reverse_rate #0.125 #0.075?
                time2wait = flick_time+time2flicker - clock.getTime()
                core.wait(time2wait) # wait predecided time
                flip_bol = not flip_bol
                
    new_row = np.array([clock.getTime() - offset, str(blk+1), '', "Baseline start", ''], dtype='object')
    log_arr = np.vstack([log_arr, new_row])
                
    # break
    fixation_cross.draw()
    win.flip()
    # wait for TR*nr_TRs_per_stim seconds at end of block
    core.wait(TR*(nr_TRs_per_stim-1) + 2)
                
    fixation_cross.draw()
    win.flip()
    # wait for TR*nr_TRs_per_stim seconds at end of block
    # wait for trigger (sync)
    triggerTime = wait_for_scanner(trigger, offset)
    ## log start
    new_row = np.array([[triggerTime, '', '', "T", ""]], dtype='object')
    log_arr = np.vstack([log_arr, new_row])
    # log end of block
    new_row = np.array([clock.getTime() - offset, str(blk+1), '', "Baseline stop", ''], dtype='object')
    log_arr = np.vstack([log_arr, new_row])

# wait some time at end
core.wait(12.5)

new_row = np.array([clock.getTime() - offset, str(blk+1), '', "EXP end", ''], dtype='object')
log_arr = np.vstack([log_arr, new_row])
# save data
nowTime = datetime.datetime.now()
nowTimeForFileName = '%04d%02d%02d_%02d%02d' %(nowTime.year,
                                               nowTime.month,
                                               nowTime.day,
                                               nowTime.hour,
                                               nowTime.minute)
folder_path = './data/'
if not os.path.exists(folder_path):
    try:
        os.makedirs(folder_path) 
        print(f"Folder '{folder_path}' created successfully.")
    except OSError as e:
        print(f"Error creating folder '{folder_path}': {e}")

file_name = f"./data/logdata_LGN_prf_sub_{sub_nr}_run_{run_nr}_{condition_name}_{nowTimeForFileName}.csv"
with open(file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time",  "Block Nr", "Trial Nr", "Event", "Additional info"])
    for row in log_arr:
      writer.writerow(row)

win.close()
core.quit()