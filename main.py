from bokeh.plotting import figure, show
import cv2
import pandas
from datetime import datetime

first_frame = None


df = pandas.DataFrame({'Start': [], 'End': []})
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
times_of_motion = []
isinstance_of_motion = []
while True:

    check, frame = capture.read()

    motion = False

    frame_gs = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_gs = cv2.GaussianBlur(frame_gs, (21, 21), 0)

    if first_frame is None:

        first_frame = frame_gs
        # will only store the 1st frame and after that this if block will never be executed
        continue
        # will start again the loop from beggining

    delta_frame = cv2.absdiff(first_frame, frame_gs)

    thresh_frame = cv2.threshold(delta_frame, 40, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    outlines, _ = cv2.findContours(
        thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for outline in outlines:

        if cv2.contourArea(outline) < 11000:
            continue
            # go back to the beggining of the forloop i.e, check for another outline
        else:
            x, y, w, h = cv2.boundingRect(outline)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
            motion = True

    if motion == True:
        times_of_motion.append(datetime.now())
    else:
        if len(times_of_motion) > 1 and [times_of_motion[0], times_of_motion[-1]] not in isinstance_of_motion:
            isinstance_of_motion.append(
                [times_of_motion[0], times_of_motion[-1]])
            times_of_motion = []

    #cv2.imshow("vdo_gs", frame_gs)
    #cv2.imshow("diff", delta_frame)
    #cv2.imshow("thresh delta", thresh_frame)
    cv2.imshow("press q to quit...", frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        cv2.destroyAllWindows
        break


for i in isinstance_of_motion:
    df = df.append({'Start': i[0], 'End': i[-1]}, ignore_index=True)

df.to_csv("Times.csv")

# Plotting the time graph

df = pandas.read_csv("Times.csv", parse_dates=["Start", "End"])

f = figure(height=500, width=1200, x_axis_type="datetime",
           x_axis_label='Times', y_axis_label="Motion", title="Motion Graph")

# To remove the smaller scales from y axis
f.yaxis.minor_tick_line_color = None

f.quad(left=df["Start"], right=df["End"], bottom=0, top=1, color='green')

show(f)
