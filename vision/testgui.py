# coding=utf-8
import cv2
from colors import BGR_COMMON
from findHSV import CalibrationGUI
import tools
import numpy as np
#import consol
# from collections import namedtuple
# from planning import Planner
# from worldstate import World

TEAM_COLORS = set(['yellow', 'blue'])


class GUI(object):
    VISION = 'VISION'
    BG_SUB = 'BG Subtract'
    NORMALIZE = 'Normalize  '
    COMMS = 'Communications on/off '
    RADIAL_DIST = "Undistort on/off"

    def nothing(self, x):
        pass

    def __init__(self, calibration, pitch, launch):
        self.zones = None
        self.consol_enabled = True
        # print calibration
        self.calibration_gui = CalibrationGUI(calibration)
        # self.arduino = arduino
        self.pitch = pitch
        self.launch = launch

        # Should create a window with name self.VISION
        cv2.namedWindow(self.VISION, cv2.WINDOW_NORMAL)


        """
        trackbarname – Name of the created trackbar.
        winname – Name of the window that will be used as a parent of the created trackbar.
        value – Optional pointer to an integer variable whose value reflects the position of the slider. Upon creation,
            the slider position is defined by this variable.
        count – Maximal position of the slider. The minimal position is always 0.
        onChange – Pointer to the function to be called every time the slider changes position. This function should be
            prototyped as void Foo(int,void*); , where the first parameter is the trackbar position and the second
            parameter is the user data (see the next parameter). If the callback is the NULL pointer, no callbacks
            are called, but only value is updated.
        userdata – User data that is passed as is to the callback. It can be used to handle trackbar events without using
            global variables.
        """
        cv2.createTrackbar(self.BG_SUB, self.VISION, 0, 1, self.nothing)
        cv2.createTrackbar(self.NORMALIZE, self.VISION, 0, 1, self.nothing)
        cv2.createTrackbar(self.RADIAL_DIST, self.VISION, 0, 1, self.nothing)
        # cv2.createTrackbar(
        #     self.COMMS, self.VISION, self.arduino.comms, 1, lambda x:  self.arduino.setComms(x))

    def to_info(self, args):
        """
        Convert a tuple into a vector

        Return a Vector
        """
        x, y, angle, velocity = None, None, None, None
        if args is not None:
            if 'location' in args:
                x = args['location'][0] if args['location'] is not None else None
                y = args['location'][1] if args['location'] is not None else None

            elif 'x' in args and 'y' in args:
                x = args['x']
                y = args['y']

            if 'angle' in args:
                angle = args['angle']

            if 'velocity' in args:
                velocity = args['velocity']

        return {'x': x, 'y': y, 'angle': angle, 'velocity': velocity}

    def cast_binary(self, x):
        return x == 1

    def draw(self, frame, model_positions, actions, regular_positions, fps,
             dState, aState, a_action, d_action, grabbers, our_color, our_side,
             key=None, preprocess=None, camera=None):
        """
        Draw information onto the GUI given positions from the vision and post processing.

        NOTE: model_positions contains coordinates with y coordinate reversed!
        """
        # Get general information about the frame
        
        frame_height, frame_width, channels = frame.shape


        # turn stuff off and on, i linked launch class in a variable called launch

        """
        # robot = self.launch.controller.robot_api

        if key == ord('c'):
            '''
            Planner.planner.current_plan.initi(None)
            robot.enabled = not robot.enabled
            World.world.our_attacker.hball = False
            '''

        if key == ord('k'):
            self.consol_enabled = not self.consol_enabled

        if key == 27:
            pass  # robot.enabled = False

        consol.log('Press k to disable/enable consol', True)
        # draw console
        if self.consol_enabled:
            consol.draw()
        """
        print "drew console"

        # Draw the calibration gui
        self.calibration_gui.show(frame, key)
        print "drew calibration"
        # Draw dividors for the zones
        self.draw_zones(frame, frame_width, frame_height)

        their_color = list(TEAM_COLORS - set([our_color]))[0]

        key_color_pairs = zip(
            ['our_defender', 'their_defender', 'our_attacker', 'their_attacker'],
            [our_color, their_color] * 2)

        self.draw_ball(frame, regular_positions['ball'])

        for key, color in key_color_pairs:
            self.draw_robot(frame, regular_positions[key], color)

        # Draw fps on the canvas
        if fps is not None:
            self.draw_text(frame, 'FPS: %.1f' % fps, 0, 10, BGR_COMMON['green'], 1)

        if preprocess is not None:
            # print preprocess
            preprocess['normalize'] = self.cast_binary(
                cv2.getTrackbarPos(self.NORMALIZE, self.VISION))
            preprocess['background_sub'] = self.cast_binary(
                cv2.getTrackbarPos(self.BG_SUB, self.VISION))

        if grabbers:
            self.draw_grabbers(frame, grabbers, frame_height)

        # Extend image downwards and draw states.
        blank = np.zeros_like(frame)[:200, :, :]
        frame_with_blank = np.vstack((frame, blank))
        self.draw_states(frame_with_blank, aState, (frame_width, frame_height))

        if model_positions and regular_positions:
            pass
            for key in ['our_defender', 'our_attacker', 'their_defender', 'their_attacker']:  # 'ball',
                if model_positions[key] and regular_positions[key]:
                    self.data_text(
                        frame_with_blank, (frame_width, frame_height), our_side, key,
                        model_positions[key].x, model_positions[key].y,
                        model_positions[key].angle, model_positions[key].velocity)
                    self.draw_velocity(
                        frame_with_blank, (frame_width, frame_height),
                        model_positions[key].x, model_positions[key].y,
                        model_positions[key].angle, model_positions[key].velocity)
        # Draw center of uncroppped frame (test code)
        # cv2.circle(frame_with_blank, (266,147), 1, BGR_COMMON['black'], 1)

        
        cv2.imshow(self.VISION, frame_with_blank)
        cv2.imshow(self.VISION, frame)
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('w'):
            print "detection level: gui.py, w"
            camera.stop_capture()
            cv2.destroyAllWindows()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print "detection level: gui.py, q"
            camera.stop_capture()
            cv2.destroyAllWindows()
        if cv2.waitKey(1) & 0xFF == ord('e'):
            print "detection level: gui.py, e"
            return True
        if key == ord('x'):
            print "x is sent"

        return False

    """
    def draw_zones(self, frame, width, height):
        # Re-initialize zones in case they have not been initalized
        if self.zones is None:
            self.zones = tools.get_zones(width, height, pitch=self.pitch)

        def draw_line(self, frame, points, thickness=2):
            if points is not None:
                cv2.line(frame, (int(points[0][0]), int(points[0][1])), (int(points[1][0]), int(points[1][1])),
                         BGR_COMMON['red'], thickness)

        for zone in self.zones:
            cv2.line(frame, (zone[1], 0), (zone[1], height), BGR_COMMON['orange'], 1)
    """
    def draw_ball(self, frame, position_dict):
        pass
        if position_dict and position_dict['x'] and position_dict['y']:
            frame_height, frame_width, _ = frame.shape
            self.draw_line(
                frame, ((int(position_dict['x']), 0), (int(position_dict['x']), frame_height)), 1)
            self.draw_line(
                frame, ((0, int(position_dict['y'])), (frame_width, int(position_dict['y']))), 1)

    def draw_dot(self, frame, location):
        if location is not None:
            cv2.circle(frame, location, 2, BGR_COMMON['white'], 1)

    def draw_robot(self, frame, position_dict, color):
        if position_dict['box']:
            cv2.polylines(frame, [np.array(position_dict['box'])], True, BGR_COMMON[color], 2)

            # frame = consol.draw_dots(frame)

        if position_dict['front']:
            p1 = (position_dict['front'][0][0], position_dict['front'][0][1])
            p2 = (position_dict['front'][1][0], position_dict['front'][1][1])
            cv2.circle(frame, p1, 3, BGR_COMMON['white'], -1)
            cv2.circle(frame, p2, 3, BGR_COMMON['white'], -1)
            cv2.line(frame, p1, p2, BGR_COMMON['red'], 2)

        if position_dict['dot']:
            cv2.circle(
                frame, (int(position_dict['dot'][0]), int(position_dict['dot'][1])),
                4, BGR_COMMON['black'], -1)

        # Draw predicted position
        '''
        cv2.circle(
            frame, (,
                    ),
            4, BGR_COMMON['yellow'], -1)
        '''
        # px = self.launch.planner.world.our_attacker.predicted_vector.x
        # py = len(frame) - self.launch.planner.world.our_attacker.predicted_vector.y
        # consol.log_dot([px, py], 'yellow', 'kalman')

        if position_dict['direction']:
            cv2.line(
                frame, position_dict['direction'][0], position_dict['direction'][1],
                BGR_COMMON['orange'], 2)

    def draw_line(self, frame, points, thickness=2):
        if points is not None:
            cv2.line(frame, points[0], points[1], BGR_COMMON['red'], thickness)

    def data_text(self, frame, frame_offset, our_side, text, x, y, angle, velocity):

        if x is not None and y is not None:
            frame_width, frame_height = frame_offset
            if text == "ball":
                y_offset = frame_height + 130
                draw_x = 30
            else:
                x_main = lambda zz: (frame_width / 4) * zz
                x_offset = 30
                y_offset = frame_height + 20

                if text == "our_defender":
                    draw_x = x_main(0) + x_offset
                elif text == "our_attacker":
                    draw_x = x_main(2) + x_offset
                elif text == "their_defender":
                    draw_x = x_main(3) + x_offset
                else:
                    draw_x = x_main(1) + x_offset

                if our_side == "right":
                    draw_x = frame_width - draw_x - 80

            self.draw_text(frame, text, draw_x, y_offset)
            self.draw_text(frame, 'x: %.2f' % x, draw_x, y_offset + 10)
            self.draw_text(frame, 'y: %.2f' % y, draw_x, y_offset + 20)

            if angle is not None:
                self.draw_text(frame, 'angle: %.2f' % angle, draw_x, y_offset + 30)

            if velocity is not None:
                self.draw_text(frame, 'velocity: %.2f' % velocity, draw_x, y_offset + 40)

    def draw_text(self, frame, text, x, y, color=BGR_COMMON['green'], thickness=1.3, size=0.3, ):
        if x is not None and y is not None:
            # TODO: changed size and thickness to ints
            cv2.putText(
                frame, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, int(size), color, int(thickness))

    def draw_grabbers(self, frame, grabbers, height):
        def_grabber = grabbers['our_defender'][0]
        att_grabber = grabbers['our_attacker'][0]

        def_grabber = [(x, height - y) for x, y in def_grabber]
        att_grabber = [(x, height - y) for x, y in att_grabber]

        def_grabber = [(int(x) if x > -1 else 0, int(y) if y > -1 else 0) for x, y in def_grabber]
        att_grabber = [(int(x) if x > -1 else 0, int(y) if y > -1 else 0) for x, y in att_grabber]

        def_grabber[2], def_grabber[3] = def_grabber[3], def_grabber[2]
        att_grabber[2], att_grabber[3] = att_grabber[3], att_grabber[2]

        cv2.polylines(frame, [np.array(def_grabber)], True, BGR_COMMON['red'], 1)
        cv2.polylines(frame, [np.array(att_grabber)], True, BGR_COMMON['red'], 1)

    def draw_velocity(self, frame, frame_offset, x, y, angle, vel, scale=10):
        if not (None in [frame, x, y, angle, vel]) and vel is not 0:
            frame_width, frame_height = frame_offset
            r = vel * scale
            y = frame_height - y
            start_point = (x, y)
            end_point = (x + r * np.cos(angle), y - r * np.sin(angle))
            self.draw_line(frame, (start_point, end_point))

    def draw_states(self, frame, aState, frame_offset):
        # print frame, frame_offset, dState,'\n'
        frame_width, frame_height = frame_offset
        x_main = lambda zz: (frame_width / 4) * zz
        x_offset = 20
        y_offset = frame_height + 140

        self.draw_text(frame, "Attacker State:", x_main(2) + x_offset, y_offset, size=0.6)
        self.draw_text(frame, "   " + aState[0], x_main(2) + x_offset, y_offset + 15, size=0.6)
        self.draw_text(frame, "Strategy State:", x_main(2) + x_offset, y_offset + 33, size=0.6)
        self.draw_text(frame, "   " + aState[1], x_main(2) + x_offset, y_offset + 50, size=0.6)

    def draw_actions(self, frame, action, x, y):
        self.draw_text(
            frame, "Left Motor: " + str(action['left_motor']), x, y + 5, color=BGR_COMMON['white'])
        self.draw_text(
            frame, "Right Motor: " + str(action['right_motor']), x, y + 15, color=BGR_COMMON['white'])
        self.draw_text(
            frame, "Speed: " + str(action['speed']), x, y + 25, color=BGR_COMMON['white'])
        self.draw_text(frame, "Kicker: " + str(action['kicker']), x, y + 35, color=BGR_COMMON['white'])
        self.draw_text(frame, "Catcher: " + str(action['catcher']), x, y + 45, color=BGR_COMMON['white'])
